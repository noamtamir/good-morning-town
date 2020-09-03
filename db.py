import json
from players import Player
from game import Game
from abc import ABC, abstractmethod
from io import StringIO


class BaseDB:
    @abstractmethod
    def save_game(self): pass

    @abstractmethod
    def load_game(self): pass
   
    @abstractmethod
    def clear(self): pass

in_memory_file = StringIO()

class InMemoryJsonDB(BaseDB):
    
    @staticmethod
    def save_game(game):
        in_memory_file.write(game.to_json())

    @classmethod
    def load_game(cls):
        data = json.loads(in_memory_file.getvalue())
        if not data:
            game = Game()
            cls.save_game(game)
        else:
            game = Game.from_dict(data)
        return game
    
    @staticmethod            
    def clear():
        in_memory_file.write('{}')


class JsonDB(BaseDB):
    @staticmethod
    def save_game(game):
        with open('game_state.json', 'w') as f:
            f.write(game.to_json())

    @classmethod
    def load_game(cls):
        try:
            with open('game_state.json', 'r') as f:
                data = f.read()
                if not data:
                    game = Game()
                    cls.save_game(game)
                else:
                    game = Game.from_dict(json.loads(data))               
            return game
        except FileNotFoundError:
            game = Game()
            cls.save_game(game)
            return game
    
    @staticmethod            
    def clear():
        with open('game_state.json', 'w') as f:
            f.write('{}')