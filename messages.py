import asyncio
import re
from config import config
from abc import ABC, abstractmethod

from db import JsonDB, InMemoryJsonDB
from game import Game
from players import Player
from send_message import send_message_to_room
import requests

db = JsonDB # Change DB type here

class Message(ABC):
    def __init__(self, room, event, msg_type):
        self.game = db.load_game()
        self.room_id = room.room_id
        self.event = event
        self.msg_type = msg_type
    
    @property
    def body(self):
        return self.event.body
    
    @property
    def sender(self):
        return self.game.players.get_by_user_id(self.event.sender)
    
    @property
    def execute_on(self):
        for player in self.game.players.as_list:
            match = re.search(player.name, self.body)
            if match:
                return player
        else:
            return Player()
    
    @abstractmethod
    def execute(self): pass

class Permission(ABC):
    @abstractmethod
    def authorized(self): pass


class IgnoreInstructionMessages:
    @property
    def is_instruction(self):
        match = re.search(r'just type', self.body)
        if match:
            return True
        else:
            return False


class PublicAlivePermission(Permission):
    @property
    def authorized(self):
        authorized = False
        if not self.sender.is_alive:
            send_message_to_room(f'{self.sender.name}, you are dead! You cannot vote!', self.sender.room_id)
        elif not self.room_id == config.MAIN_ROOM_ID:
            send_message_to_room(f'{self.sender.name}, you must send this message in the group!', self.sender.room_id)
        else:
            authorized = True
        return authorized


class PublicPermission(Permission):
    @property
    def authorized(self):
        if self.room_id == config.MAIN_ROOM_ID:
            return True
        else:
            send_message_to_room(f'{self.sender.name}, you must send this message in the group!', self.sender.room_id)
            return False


class AdminPermission(Permission):
    @property
    def authorized(self):
        if self.sender.is_admin:
            return True
        else:
            send_message_to_room(f'{self.sender.name}, you are not admin!', self.room_id)
            return False


class PrivatePermission(Permission):
    @property
    def authorized(self):
        if not self.room_id == self.sender.room_id:
            send_message_to_room(f'{self.sender.name}, you must send this message in your private group chat!', self.room_id)
            return False
        return True


class PrivateRolePermission(Permission):
    allowed_role = ''
    @property
    def authorized(self):
        authorized = False
        if not self.room_id == self.sender.room_id:
            send_message_to_room(f'{self.sender.name}, you must send this message in your private group chat!', self.room_id)
        elif not self.sender.role == self.allowed_role:
            send_message_to_room(f'{self.sender.name}, you are not a {self.allowed_role}!', self.room_id)
        elif not self.sender.is_alive:
            send_message_to_room(f'{self.sender.name}, you are dead! You cannot play!', self.sender.room_id)
        else: 
            authorized = True
        return authorized


class HelloMessage(Message):
    def execute(self):
        send_message_to_room(f'Hello {self.sender.name}', self.room_id)


class WtfMessage(Message):
    def execute(self):
        r = requests.get('https://insult.mattbas.org/api/insult')
        send_message_to_room(r.text)


class StatusMessage(Message):
    def execute(self):
        send_message_to_room(self.game.get_alive_status())


class WhoIsAdminMessage(Message):
    def execute(self):
        send_message_to_room(f'{[player.name for player in self.game.players.as_list if player.is_admin][0]} is admin.')


class QuitMessage(Message, AdminPermission):
    def execute(self):
        if self.authorized:
            self.game.cleanup_game()
            db.clear()
            send_message_to_room('The game has been cancelled with great HUTZPA!')


class RestartMessage(Message, AdminPermission):
    def execute(self):
        if self.authorized:
            self.game.cleanup_game()
            send_message_to_room('Starting a new game...')
            self.game.initiate()
            db.save_game(self.game)


class TerminateMessage(Message, AdminPermission):
    def execute(self):
        if self.authorized:
            self.execute_on.is_alive = False
            send_message_to_room(f'God terminated {self.execute_on.name}! Mwahahaha!!!')
            db.save_game(self.game)


class InitGameMessage(Message, PublicPermission):
    def execute(self):
        if self.authorized:
            if not self.game.in_progress:
                self.game.initiate()
                db.save_game(self.game)
            else:
                send_message_to_room('A game is already in progress.')
        


class KillVoteMessage(Message, PublicAlivePermission, IgnoreInstructionMessages):
    @property
    def vote(self):
        if self.msg_type == 'kill':
            return True
        else:
            return False

    def execute(self):
        if self.is_instruction:
            return
        if self.authorized:
            accusee = self.game.vote_on_kill(self.sender, self.vote)
            db.save_game(self.game)
            send_message_to_room(f'{self.sender.name}, you voted to {self.msg_type} {accusee.name}!')


class AccuseMessage(Message, PublicAlivePermission, IgnoreInstructionMessages):
    def execute(self):
        if self.is_instruction:
            return
        if self.authorized:
            self.game.accuse(self.sender, self.execute_on)
            db.save_game(self.game)
            send_message_to_room(f'{self.sender.name}, you suggested to bring {self.execute_on.name} to the gallows!')
            

class DetectMessage(Message, PrivateRolePermission, IgnoreInstructionMessages):
    allowed_role = 'detective'
    def execute(self):
        if self.is_instruction:
            return
        if self.authorized:
            response = self.game.detect(self.sender, self.execute_on)
            db.save_game(self.game)
            send_message_to_room(response, self.sender.room_id)


class MurderMessage(Message, PrivateRolePermission, IgnoreInstructionMessages):
    allowed_role = 'murderer'
    def execute(self):
        if self.is_instruction:
            return
        if self.authorized:
            response = self.game.murder(self.sender, self.execute_on)
            db.save_game(self.game)
            send_message_to_room(response, self.sender.room_id)


class ProtectMessage(Message, PrivateRolePermission, IgnoreInstructionMessages):
    allowed_role = 'policeman'
    def execute(self):
        if self.is_instruction:
            return
        if self.authorized:
            response = self.game.protect(self.sender, self.execute_on)
            db.save_game(self.game)
            send_message_to_room(response, self.sender.room_id)


class RoleMessage(Message, PrivatePermission, IgnoreInstructionMessages):
    def execute(self):
        if self.is_instruction:
            return
        if self.authorized:
            send_message_to_room(f'You are a {self.sender.role}', self.sender.room_id)


class MessageFactory:
    MESSAGE_TYPES = {
        'init': {
            'regex': 'town init',
            'subclass': InitGameMessage
            },
        'kill': {
            'regex': 'town kill',
            'subclass': KillVoteMessage
            },
        'save': {
            'regex': 'town save',
            'subclass': KillVoteMessage
            },
        'accuse': {
            'regex': 'town accuse',
            'subclass': AccuseMessage
            },
        'detect': {
            'regex': 'town detect',
            'subclass': DetectMessage
            },
        'murder': {
            'regex': 'town murder',
            'subclass': MurderMessage
            },
        'protect': {
            'regex': 'town protect',
            'subclass': ProtectMessage
            },
        'hello': {
            'regex': 'town say hello',
            'subclass': HelloMessage
            },
        'role': {
            'regex': 'town role',
            'subclass': RoleMessage
            },
        'wtf': {
            'regex': 'town wtf',
            'subclass': WtfMessage
        },
        'status': {
            'regex': 'town status',
            'subclass': StatusMessage
        },
        'whoisadmin': {
            'regex': 'town who is admin',
            'subclass': WhoIsAdminMessage
        },
        'quit': {
            'regex': 'town admin quit',
            'subclass': QuitMessage
        },
        'restart': {
            'regex': 'town admin restart',
            'subclass': RestartMessage
        },
        'terminate': {
            'regex': 'town admin terminate',
            'subclass': TerminateMessage
        }
    }
    
    @classmethod
    async def from_event(cls, room, event):
        for msg_type in cls.MESSAGE_TYPES:
            match = re.search(cls.MESSAGE_TYPES[msg_type]['regex'], event.body)
            if match:
                return cls.MESSAGE_TYPES[msg_type]['subclass'](room, event, msg_type)