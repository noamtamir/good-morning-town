import json
import asyncio
from random import sample, choice
from collections import Counter
from datetime import datetime, timedelta
from contextlib import contextmanager
from config import config, ASYNC_TASKS, SCHEDULED_TASKS, TIME_OF
from send_message import send_message_to_room
from players import Players, Player


class Game:
    def __init__(self, in_progress=False, players=None, accusee=None):
        self.in_progress = in_progress
        self.players = players or Players.from_dict(config.PLAYERS)
        self.accusee = accusee or Player()

    # TODO:
    @classmethod
    def from_dict(cls, data):
        in_progress = data.get('in_progress', False)
        players_json = data.get('players') or config.PLAYERS
        players = Players.from_dict(players_json)
        accusee = players.get_by_name(data.get('accusee')) or Player()
        return cls(in_progress=in_progress, players=players, accusee=accusee)

    def to_json(self):
        game_dict = self.__dict__.copy()
        game_dict['accusee'] = self.accusee.name
        game_dict['players'] = self.players.to_dict()
        return json.dumps(game_dict, sort_keys=True)

    def initiate(self):
        self.in_progress = True
        self.players = Players.from_dict(config.PLAYERS)
        for player in self.players.as_list:
            player.is_alive = True
        self.accusee = Player()
        chosen_players = sample(self.players.as_list, 4)
        for player in chosen_players[:2]:
            player.role = 'murderer'
        chosen_players[2].role = 'detective'
        chosen_players[3].role = 'policeman'
        self.declare_new_game()
        self.send_roles_to_players()

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
Every evening, at 20:30 the Assembly will gather, and the Civilians of this town will vote on who they think the Murderer is.
At 21:00 exactly, the Assembly will be ajurned, and the verdict will be declared, and executed.
Thus, begins the night, where no Civilian is safe from the wrath of the Murderers...

Each of you will now receive your role in a private message. If you forget your role, just type 'town role' in your private chat.

For detailed rules and commands of the game:
https://github.com/noamtamir/good-morning-town/blob/master/README.md
            """
        )

    def send_roles_to_players(self):
        for player in self.players.as_list:
            send_message_to_room(
                f'Hey {player.name}! The game has begun and you are a {player.role}! Have fun!', player.room_id)

    def vote(self):
        send_message_to_room(
            '''
Who should we send to the gallow tonight?
You have until 21:00 to decide.
Just type 'town kill' and the name of the person you think is the murderer!
            '''
        )

    def determine_accusee(self):
        counter = Counter(
            list(filter(None, [player.accusee for player in self.players.as_list])))
        # If tied, then just pick the first one.
        try:
            accusee = counter.most_common(1)[0][0]
        except IndexError:
            return
        accusee = self.players.get_by_name(accusee)
        if accusee:
            accusee.is_accused = True
            self.accusee = accusee
        else:
            self.accusee = self.kill_random()
            return

    def accuse(self, player, accusee):
        setattr(player, 'accusee', accusee)

    def end_day(self):
        self.determine_accusee()
        self.accusee.is_alive = False
        send_message_to_room(
            f'''
{self.accusee.name} has been killed! Good night town!
Murderers, if you wish to murder tonight, just type 'town murder' and the name of the person you wish to murder.
Remember, you both have to pick the same person!
Policeman, you can prevent such a murder from happening by protect 1 Civilian, just type 'town protect' and the name of the person you wish to protect.
Detective, if you wish to find out the role a person, just type 'town detect' and the name of the person you wish to detect.
Sweet dreams!
                '''
        )
        self.clear_votes()
        self.check_victory()

    def clear_votes(self):
        for player in self.players.as_list:
            player.accusee = None
            player.is_accused = False
        self.accusee = Player()

    def check_victory(self):
        alive_by_role_status = dict(Counter(
            [player.role for player in self.players.as_list if player.is_alive]).most_common())
        if not alive_by_role_status.get('murderer'):
            send_message_to_room(
                'The Town has won! All murderers have been killed!')
            self.cleanup_game()
        if not alive_by_role_status.get('civilian') and not alive_by_role_status.get('detective'):
            send_message_to_room(
                'The Murderers have won! All civilians are dead!')
            self.cleanup_game()
            # TODO: initiate new game automaticaly?

    def cleanup_game(self):
        self.in_progress = False
        self.players = Players.from_dict(config.PLAYERS)
        for player in self.players.as_list:
            player.is_alive = False
        self.accusee = Player()
        for task in ASYNC_TASKS:
            task.cancel()

    def detect(self, detective, other_player):
        if detective.has_detected:
            return "You have already detected once tonight!"
        if other_player.name == 'nobody':
            return "You have attempted to detect nobody! Try again!"
        if detective.role == 'detective':
            role = other_player.role
            detective.has_detected = True
            return f'{other_player.name} is a {role}'

    def murder(self, murderer, other_player):
        if not murderer.role == 'murderer':
            return "You are not a murderer!"
        if murderer.has_attempted_murder:
            return "You have already attempted murder tonight!"
        if other_player.name == 'nobody':
            return "You have attempted to murder nobody! Try again!"
        if murderer.role == 'murderer' and not murderer.has_attempted_murder:
            if other_player.is_alive:
                other_player.murder_attempts += 1
                murderer.has_attempted_murder = True
                return f"Attempted to murder {other_player.name}"
            else:
                return f"{other_player.name} is already dead! Try again!"

    def protect(self, policeman, other_player):
        if policeman.has_protected:
            return "You have already protected once tonight!"
        if other_player.name == 'nobody':
            return "You have attempted to protect nobody! Try again!"
        if policeman.role == 'policeman':
            policeman.has_protected = True
            other_player.is_protected = True
            return f'{other_player.name} will be protected tonight.'

    def begin_day(self):
        # Recurring function every morning at 9:00
        player_to_be_murdered = self.check_murder_attempt()
        if player_to_be_murdered:
            if player_to_be_murdered.is_protected:
                murder_message = f'Tonight, there was an attempt to murder {player_to_be_murdered.name}, but he was protected by the policeman!'
            else:
                self.execute_murder(player_to_be_murdered)
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

    def check_murder_attempt(self):
        number_of_murderers = [
            player.role for player in self.players.as_list if player.is_alive].count('murderer')
        if number_of_murderers:
            for player in self.players.as_list:
                if player.murder_attempts == number_of_murderers:
                    return player

    @staticmethod
    def execute_murder(player):
        player.is_alive = False

    def clear_night(self):
        for player in self.players.as_list:
            player.has_attempted_murder = False
            player.has_detected = False
            player.has_protected = False
            player.is_protected = False

    def get_alive_status(self):
        alive_status = {
            player.name: player.is_alive for player in self.players.as_list}
        return alive_status

    def kill_random(self):
        alive_players = [player for player in self.players.as_list if player.is_alive]
        player = choice(alive_players)
        player.is_alive = False
        return player
