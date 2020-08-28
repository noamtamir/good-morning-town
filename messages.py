import asyncio
import re
from config import CURRENT_GAME, config
from abc import ABC

from good_morning_town import vote_on_kill, vote_on_candidate
from game import Game
from send_message import send_message_to_room


class Message(ABC):
    def __init__(self, event, msg_type):
        self.event = event
        self.msg_type = msg_type
    
    @property
    def body(self):
        return self.event.body
    
    @property
    def sender(self):
        return self.event.sender
    
    @property
    def execute_on(self):
        for name in config.PLAYERS:
            match = re.search(name, self.body)
            if match:
                return name


class InitGameMessage(Message):
    def execute(self):
        global CURRENT_GAME
        if not CURRENT_GAME:
            CURRENT_GAME = Game()
            CURRENT_GAME.initiate()
        else:
            send_message_to_room('A game is already in progress.')


class KillVoteMessage(Message):
    @property
    def vote(self):
        if self.msg_type == 'kill':
            return True
        else:
            return False

    def execute(self):
        CURRENT_GAME.vote_on_kill(self.sender, self.vote)
        send_message_to_room(f'{self.sender}, you voted to {self.msg_type} {CURRENT_GAME.candidate}!')


class CandidateMessage(Message):
    def execute(self):
        CURRENT_GAME.vote_on_candidate(self.sender, self.execute_on)
        send_message_to_room(f'{CURRENT_GAME.players_by_user_id[self.sender]}, you suggested to bring {self.execute_on} to the gallows!')


class DetectMessage(Message):
    def execute(self):
        role = CURRENT_GAME.detect(self.sender, self.execute_on)
        send_message_to_room(f'{self.execute_on} is a {role}')

class MurderMessage(Message):
    def execute(self):
        response = CURRENT_GAME.murder(self.sender, self.execute_on)
        send_message_to_room(response)

class MessageFactory:
    MESSAGE_TYPES = {
        'init': {
            'regex': 'town.* init',
            'subclass': InitGameMessage
            },
        'kill': {
            'regex': 'town.* kill',
            'subclass': KillVoteMessage
            },
        'save': {
            'regex': 'town.* save',
            'subclass': KillVoteMessage
            },
        'candidate': {
            'regex': 'town.* candidate',
            'subclass': CandidateMessage
            },
        'detect': {
            'regex': 'town.* detect',
            'subclass': DetectMessage
            },
        'murder': {
            'regex': 'town.* murder',
            'subclass': MurderMessage
            }
            
    }
    
    @classmethod
    async def from_event(cls, event):
        for msg_type in cls.MESSAGE_TYPES:
            match = re.search(cls.MESSAGE_TYPES[msg_type]['regex'], event.body)
            if match:
                return cls.MESSAGE_TYPES[msg_type]['subclass'](event, msg_type)