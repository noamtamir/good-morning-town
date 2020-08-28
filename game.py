import json
import asyncio
from random import sample
from collections import Counter
from datetime import datetime, timedelta
from contextlib import contextmanager
from config import config, CURRENT_GAME, ASYNC_TASKS
from send_message import send_message_to_room
from async_scheduler import run_at, wait_for, TLV, schedule_next_day_at
from players import Players
from db import JsonDb

class Game:
    def __init__(self):
        self.players = Players.from_config(config.PLAYERS)
        self.candidate = None
        self.db = JsonDb()

    @property
    def players_by_user_id(self):
        return {player.user_id: player for player in self.players}

    def initiate(self):
        chosen_players = sample(self.players, 3)
        for player in chosen_players[:2]:
            player.role = 'murderer'
        chosen_players[2].role = 'detective'
        self.declare_new_game()
        self.send_roles_to_players()
        self.schedule_votes()
        self.db.update_db(self)

    @staticmethod
    def declare_new_game():
        send_message_to_room(
            """
Good Morning Town!
A new game of The Town has now begun!
Each of you has will now receive your role in a private message. The rules of the game are:
Blah blah blah...
            """
        )

    def send_roles_to_players(self):
        for player in self.players:
            send_message_to_room(f'Hey {player.name}! The game has begun and you are a {player.role}! Have fun!')
    
    def schedule_votes(self):
        now = datetime.now(tz=TLV)
        scheduled_vote1 = now.replace(hour=20, minute=0, second=0, microsecond=0)
        scheduled_vote2 = now.replace(hour=20, minute=30, second=0, microsecond=0)
        scheduled_end_day = now.replace(hour=20, minute=30, second=0, microsecond=0)
        scheduled_begin_day = now.replace(hour=9, minute=30, second=0, microsecond=0)
        self.check_time_and_schedule(now, scheduled_vote1, self.vote1)
        self.check_time_and_schedule(now, scheduled_vote2, self.vote2)
        self.check_time_and_schedule(now, scheduled_end_day, self.end_day)
        self.check_time_and_schedule(now, scheduled_begin_day, self.begin_day)
    
    @staticmethod
    def check_time_and_schedule(now, scheduled, func):
        if now > scheduled:
            scheduled += timedelta(days=1)
        task = asyncio.ensure_future(
            run_at(
                scheduled,
                func()
            )
        )
        ASYNC_TASKS.append(task)

    async def vote1(self):
        send_message_to_room(
            '''
Who should we send to the gallow tonight?
You have until 20:30 to decide / change your mind.
Just type 'candidate' and the name of your candidate!
            '''
        )
        schedule_next_day_at((20,0), self.vote1)

    async def vote2(self):
        candidate = determine_candidate()
        send_message_to_room(
            f'''
Do you think {candidate} should be sent to the gallow?
You have until 21:00 to decide / change your mind.
Just type 'kill' or 'save'!
            '''
        )
        schedule_next_day_at((20,30), self.vote2)
    
    def determine_candidate(self):
        counter = Counter(list(filter(None, [player.candidate for player in self.players])))
        candidate = counter.most_common(1)[0][0] # If tied, then just pick the first one.
        candidate.is_candidate = True
        self.candidate = candidate
        self.db.update_db(self)
        return candidate

    def vote_on_candidate(self, user_id, candidate):
        self.update_player_field_if_alive(user_id, 'candidate', candidate)

    def vote_on_kill(self, user_id, kill_vote):
        self.update_player_field_if_alive(user_id, 'kill_vote', kill_vote)

    def update_player_field_if_alive(self, user_id, field, value):
        player = self.players_by_user_id[user_id]
        if player.is_alive:
            setattr(player, field, value)
        self.db.update_db(self)
    
    async def end_day(self):
        counter = Counter([self.player.kill_vote for player in self.players])
        accumulated_votes = dict(counter.most_common())
        alive = True
        if accumulated_votes[True] > accumulated_votes[False]:
            alive = False
            verdict = 'killed'
            self.candidate.is_alive = alive
        else:
            verdict = 'saved'

        self.clear_votes()
        send_message_to_room(f'{self.candidate.name} has been {verdict}! Good night town!')
        self.check_victory()
        schedule_next_day_at((21,0), self.end_day)

    def clear_votes(self):
        for player in self.players:
            self.player.candidate = None
            self.player.is_candidate = False
            self.player.kill_vote = False
        self.candidate = None
        self.db.update_db(self)

    def check_victory(self):
        alive_by_role_status = dict(Counter([player.role for player in self.players if player.is_alive]).most_common())
        if not alive_by_role_status.get('murderer'):
            send_message_to_room('The Town has won! All murderers have been killed!')
            self.cleanup_game()
        if not alive_by_role_status.get('civilian') and not alive_by_role_status.get('detective'):
            send_message_to_room('The Murderers have won! All civilians are dead!')
            self.cleanup_game()

    def cleanup_game(self):
        global CURRENT_GAME
        CURRENT_GAME = None
        for task in ASYNC_TASKS:
            task.cancel()
        self.db.update_db(self)
        #TODO: initiate new game?

    def detect(self, user_id, other_player_user_id):
        detective = self.players_by_user_id[user_id]
        other_player = self.players_by_user_id[other_player_user_id]
        if self.detective.role == 'detective':
            role = self.other_player.role
            return role
        else:
            return '... Hey! Wait a minute! You are not a detective!'

    def murder(self, user_id, other_player_user_id):
        murderer = self.players_by_user_id[user_id]
        other_player = self.players_by_user_id[other_player_user_id]
        if not self.murderer.role == 'murderer':
            return "You are not a murderer!"
        if self.murderer.has_attempted_murder:
            return "You have already attempted murder tonight!"
        if self.murderer.role == 'murderer' and not self.murderer.has_attempted_murder:
            if self.other_player.is_alive:
                self.other_player.murder_attempts += 1
                self.murderer.has_attempted_murder = True
                self.db.update_db(self)
                return f"Attempted to murder {other_player.name}"
            else:
                return f"{other_player.name} is already dead! Try again!"
    
    async def begin_day(self):
        # Recurring function every morning at 9:00
        murdered = self.check_and_execute_if_murder_occured()
        if not murdered:
            murdered = 'nobody'
        send_message_to_room(
            f'''
Good Morning Town!
Tonight {murdered} has been killed!
This is the alive status:
{self.get_alive_status()}
            '''
        )
        self.check_victory()
        schedule_next_day_at((21,0), self.end_day)

    def check_and_execute_if_murder_occured(self):
        number_of_murderers = [player.role for player in self.players if player.is_alive].count('murderer')
        if number_of_murderers:
            for player in self.players:
                if self.player.murder_attempts == number_of_murderers:
                    self.player.is_alive = False
                    self.db.update_db(self)
                    return player

    def get_alive_status(self):
        alive_status = {player.name: player.is_alive for player in self.players}
        return alive_status
