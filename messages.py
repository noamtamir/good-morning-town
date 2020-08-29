import asyncio
import re
from config import CURRENT_GAME, config
from abc import ABC, abstractmethod

from game import Game
from send_message import send_message_to_room


class Message(ABC):
    def __init__(self, room, event, msg_type):
        global CURRENT_GAME
        if not CURRENT_GAME:
            CURRENT_GAME = Game()
        self.room_id = room.room_id
        self.event = event
        self.msg_type = msg_type
    
    @property
    def body(self):
        return self.event.body
    
    @property
    def sender(self):
        return CURRENT_GAME.players_by_user_id[self.event.sender]
    
    @property
    def execute_on(self):
        for player in CURRENT_GAME.players:
            match = re.search(player.name, self.body)
            if match:
                return player
    
    @abstractmethod
    def execute(self): pass

class Permission(ABC):
    @abstractmethod
    def authorized(self): pass


class PublicAlivePermission(Permission):
    @property
    def authorized(self):
        authorized = False
        if not self.room_id == config.MAIN_ROOM_ID:
            send_message_to_room(f'{self.sender.name}, you must send this message in the group!', self.sender.room_id)
        if not self.sender.is_alive:
            send_message_to_room(f'{self.sender.name}, you are dead! You cannot vote!', self.sender.room_id)
        if self.room_id == config.MAIN_ROOM_ID and self.sender.is_alive:
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


class PrivateRolePermission(Permission):
    allowed_role = ''
    @property
    def authorized(self):
        authorized = False
        if not self.room_id == self.sender.room_id:
            send_message_to_room(f'{self.sender.name}, you must send this message in your private group chat!', self.room_id)
        if not self.sender.is_alive:
            send_message_to_room(f'{self.sender.name}, you are dead! You cannot play!', self.sender.room_id)
        if not self.sender.role == self.allowed_role:
            send_message_to_room(f'{self.sender.name}, you are not a {self.allowed_role}!', self.sender.room_id)
        authorized = True
        return authorized


class InitGameMessage(Message, PublicPermission):
    def execute(self):
        if self.authorized:
            global CURRENT_GAME
            if not CURRENT_GAME:
                CURRENT_GAME.initiate()
            elif not CURRENT_GAME.in_progress:
                CURRENT_GAME.initiate()
            else:
                send_message_to_room('A game is already in progress.')


class KillVoteMessage(Message, PublicAlivePermission):
    @property
    def vote(self):
        if self.msg_type == 'kill':
            return True
        else:
            return False

    def execute(self):
        if self.authorized:
            accusee = CURRENT_GAME.vote_on_kill(self.sender, self.vote)
            send_message_to_room(f'{self.sender.name}, you voted to {self.msg_type} {accusee.name}!')


class AccuseMessage(Message, PublicAlivePermission):
    def execute(self):
        if self.authorized:
            CURRENT_GAME.vote_on_accusee(self.sender, self.execute_on)
            send_message_to_room(f'{self.sender.name}, you suggested to bring {self.execute_on.name} to the gallows!')


class DetectMessage(Message, PrivateRolePermission):
    allowed_role = 'detective'
    def execute(self):
        if self.authorized:
            response = CURRENT_GAME.detect(self.sender, self.execute_on)
            send_message_to_room(response, self.sender.room_id)


class MurderMessage(Message, PrivateRolePermission):
    allowed_role = 'murderer'
    def execute(self):
        if self.authorized:
            response = CURRENT_GAME.murder(self.sender, self.execute_on)
            send_message_to_room(response, self.sender.room_id)


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
            }
            
    }
    
    @classmethod
    async def from_event(cls, room, event):
        for msg_type in cls.MESSAGE_TYPES:
            match = re.search(cls.MESSAGE_TYPES[msg_type]['regex'], event.body)
            if match:
                return cls.MESSAGE_TYPES[msg_type]['subclass'](room, event, msg_type)