import json
from config import CURRENT_GAME
from contextlib import contextmanager

class JsonDb:
    @staticmethod
    def load_game_state_from_game(game):
        game_state = {player.name: player.__dict__ for player in game.players}
        return game_state

    @staticmethod
    def load_game_state_from_db():
        with open('game_state.json', 'r') as f:
            game_state = json.loads(f.read())
        return game_state

    @staticmethod
    def save_game_state(game_state, clear=False):
        if clear:
            game_state = {}
        with open('game_state.json', 'w') as f:
            f.write(json.dumps(game_state))
    
    def update_db(self, game):
        game_state = self.load_game_state_from_game(game)
        self.save_game_state(game_state)
            
    def clear_db(self):
        self.save_game_state(clear=True)