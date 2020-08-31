import json
import asyncio
from random import sample
from collections import Counter
from datetime import datetime, timedelta
from contextlib import contextmanager
from config import config, ASYNC_TASKS, TIME_OF
from send_message import send_message_to_room
from async_scheduler import run_at, wait_for, TLV, schedule_next_day_at
from players import Players, Player
from db import JsonDB, NoDB

class Game:
    def __init__(self):
        self.in_progress = False
        self.players = Players.from_config(config.PLAYERS)
        self.accusee = Player()
        self.db = JsonDB()

    @property
    def players_by_user_id(self):
        return {player.user_id: player for player in self.players}

    @property
    def players_by_name(self):
        return {player.name: player for player in self.players}

    def initiate(self):
        self.in_progress = True
        self.players = Players.from_config(config.PLAYERS)
        self.accusee = Player()
        chosen_players = sample(self.players, 4)
        for player in chosen_players[:2]:
            player.role = 'murderer'
        chosen_players[2].role = 'detective'
        chosen_players[3].role = 'policeman'
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
There are 2 Murderers among you! And they are trying to kill you every night!
They succeed when they work together and both try to kill the same person.
Luckily, you have your trusty Policeman to help you out. He protects 1 Civilian every night.
Also, the Detective goes out every night and investigates. Everynight, he figures out the role of one of you.
Every evening, at 20:00 the Assembly will gather, and the Civilians of this town will vote on who they think the Murderer is.
At 20:30 exactly, the votes will be collected, and the Accusee will be declared.
A second vote will take place, and the Civilians will decide wether the Accusee should be sent to the gallow or not!
At 21:00 exactly, the Assembly will be ajurned, and the verdict will be declared, and executed.
Thus, begins the night, where no Civilian is safe from the wrath of the Murderers...

Each of you will now receive your role in a private message. If you forget your role, just type 'town role' in your private chat.

For detailed rules and commands of the game:
https://github.com/noamtamir/good-morning-town/blob/master/README.md
            """
        )

    def send_roles_to_players(self):
        for player in self.players:
            send_message_to_room(f'Hey {player.name}! The game has begun and you are a {player.role}! Have fun!', player.room_id)
    
    def schedule_votes(self):
        now = datetime.now(tz=TLV)
        scheduled_vote1 = now.replace(**TIME_OF['VOTE1'].dict)
        scheduled_vote2 = now.replace(**TIME_OF['VOTE2'].dict)
        scheduled_end_day = now.replace(**TIME_OF['END_DAY'].dict)
        scheduled_begin_day = now.replace(**TIME_OF['BEGIN_DAY'].dict)
        self.check_time_and_schedule(now, scheduled_vote1, self.vote1)
        self.check_time_and_schedule(now, scheduled_vote2, self.vote2)
        self.check_time_and_schedule(now, scheduled_end_day, self.end_day)
        self.check_time_and_schedule(now, scheduled_begin_day, self.begin_day)
    
    @staticmethod
    def check_time_and_schedule(now, scheduled, func):
        if now > scheduled:
            scheduled += timedelta(days=1)
        task = asyncio.create_task(
            run_at(
                scheduled,
                func()
            )
        )
        task.set_name(f'{str(func)} at {str(scheduled)}')
        ASYNC_TASKS.append(task)

    async def vote1(self):
        send_message_to_room(
            '''
Who should we send to the gallow tonight?
You have until 20:30 to decide / change your mind.
Just type 'town accuse' and the name of your accusee!
            '''
        )
        schedule_next_day_at(TIME_OF['VOTE1'].tuple, self.vote1)

    async def vote2(self):
        accusee = self.determine_accusee()
        send_message_to_room(
            f'''
Do you think {accusee.name} should be sent to the gallow?
You have until 21:00 to decide / change your mind.
Just type 'town kill' or 'town save'!
            '''
        )
        schedule_next_day_at(TIME_OF['VOTE2'].tuple, self.vote2)
    
    def determine_accusee(self):
        counter = Counter(list(filter(None, [player.accusee for player in self.players])))
        accusee = counter.most_common(1)[0][0] # If tied, then just pick the first one.
        accusee = self.players_by_name[accusee]
        accusee.is_accused = True
        self.accusee = accusee
        self.db.update_db(self)
        return accusee

    def accuse(self, player, accusee):
        self.update_player_field_if_alive(player, 'accusee', accusee)

    def vote_on_kill(self, player, kill_vote):
        if not self.accusee.name == 'nobody':
            self.update_player_field_if_alive(player, 'kill_vote', kill_vote)
        return self.accusee

    def update_player_field_if_alive(self, player, field, value):
        if player.is_alive:
            setattr(player, field, value)
        self.db.update_db(self)
    
    async def end_day(self):
        counter = Counter([player.kill_vote for player in self.players])
        accumulated_votes = dict(counter.most_common())
        alive = True
        if accumulated_votes.get(True, 0) > accumulated_votes.get(False, 0):
            alive = False
            verdict = 'killed'
            self.accusee.is_alive = alive
        else:
            verdict = 'saved'

        send_message_to_room(
            f'''
{self.accusee.name} has been {verdict}! Good night town!
Murderers, if you wish to murder tonight, just type 'town murder' and the name of the person you wish to murder.
Remember, you both have to pick the same person!
Policeman, you can prevent such a murder from happening by protect 1 Civilian, just type 'town protect' and the name of the person you wish to protect.
Detective, if you wish to find out the role a person, just type 'town detect' and the name of the person you wish to detect.
Sweet dreams!
            '''
        )
        self.clear_votes()
        self.check_victory()
        schedule_next_day_at(TIME_OF['END_DAY'].tuple, self.end_day)

    def clear_votes(self):
        for player in self.players:
            player.accusee = None
            player.is_accused = False
            player.kill_vote = False
        self.accusee = Player()
        self.db.update_db(self)

    def check_victory(self):
        alive_by_role_status = dict(Counter([player.role for player in self.players if player.is_alive]).most_common())
        if not alive_by_role_status.get('murderer'):
            send_message_to_room('The Town has won! All murderers have been killed!')
            self.cleanup_game()
        if not alive_by_role_status.get('civilian') and not alive_by_role_status.get('detective'):
            send_message_to_room('The Murderers have won! All civilians are dead!')
            self.cleanup_game()
            #TODO: initiate new game automaticaly?

    def cleanup_game(self):
        self.in_progress = False
        for player in self.players:
            player.is_alive = False
        self.db.clear_db()
        for task in ASYNC_TASKS:
            task.cancel()

    def detect(self, detective, other_player):
        if detective.has_detected:
            return "You have already detected once tonight!"
        if detective.role == 'detective':
            role = other_player.role
            detective.has_detected = True
            self.db.update_db(self)
            return f'{other_player.name} is a {role}'

    def murder(self, murderer, other_player):
        if not murderer.role == 'murderer':
            return "You are not a murderer!"
        if murderer.has_attempted_murder:
            return "You have already attempted murder tonight!"
        if murderer.role == 'murderer' and not murderer.has_attempted_murder:
            if other_player.is_alive:
                other_player.murder_attempts += 1
                murderer.has_attempted_murder = True
                self.db.update_db(self)
                return f"Attempted to murder {other_player.name}"
            else:
                return f"{other_player.name} is already dead! Try again!"
    
    def protect(self, policeman, other_player):
        if policeman.has_protected:
            return "You have already protected once tonight!"
        if policeman.role == 'policeman':
            policeman.has_protected = True
            other_player.is_protected = True
            self.db.update_db(self)
            return f'{other_player.name} will be protected tonight.'
    
    async def begin_day(self):
        # Recurring function every morning at 9:00
        player_to_be_murdered = self.check_murder_attempt()
        if player_to_be_murdered:
            if player_to_be_murdered.is_protected:
                murder_message = f'Tonight, there was an attempt to murder {player_to_be_murdered.name}, but he was protected by the policeman!'
            else:
                self.execute_murder()
                murder_message = f'Tonight, {player_to_be_murdered.name} has been killed!'
        else:
            murder_message = 'Tonight, nobody has been killed!'
        send_message_to_room(
            f'''
Good Morning Town!
{murder_message}
This is the alive status:
{self.get_alive_status()}
            '''
        )
        self.clear_night()
        self.check_victory()
        schedule_next_day_at(TIME_OF['BEGIN_DAY'].tuple, self.end_day)

    def check_murder_attempt(self):
        number_of_murderers = [player.role for player in self.players if player.is_alive].count('murderer')
        if number_of_murderers:
            for player in self.players:
                if player.murder_attempts == number_of_murderers:
                    return player
    
    def execute_murder(self):
        self.accusee.is_alive = False
        self.db.update_db(self)

    def clear_night(self):
        for player in self.players:
            player.has_attempted_murder = False
            player.has_detected = False
            player.has_protected = False
            player.is_protected = False
        self.db.update_db(self)

    def get_alive_status(self):
        alive_status = {player.name: player.is_alive for player in self.players}
        return alive_status
