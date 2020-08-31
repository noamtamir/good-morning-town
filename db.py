import json
from players import Player
from abc import ABC, abstractmethod

class BaseDB:
    @staticmethod
    def load_game_state_from_game(game):
        game_state = {player.name: player.__dict__ for player in game.players}
        for player in game_state:
            if type(game_state[player]['accusee']) is Player:
                game_state[player]['accusee'] = game_state[player]['accusee'].name
        return game_state

    @abstractmethod
    def update_db(self, game): pass
    
    @abstractmethod
    def clear_db(self): pass


class NoDB(BaseDB):
    def update_db(self, game): pass
    def clear_db(self): pass

class JsonDB(BaseDB):
    @staticmethod
    def load_game_state_from_db():
        with open('game_state.json', 'r') as f:
            game_state = json.loads(f.read())
        return game_state

    @staticmethod
    def save_game_state(game_state):
        with open('game_state.json', 'w') as f:
            f.write(json.dumps(game_state))
    
    def update_db(self, game):
        game_state = self.load_game_state_from_game(game)
        self.save_game_state(game_state)
            
    def clear_db(self):
        self.save_game_state({})