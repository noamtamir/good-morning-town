from unittest import TestCase
from unittest.mock import MagicMock
import json

from db import JsonDB
from game import Game
import os

class TestJsonDB(TestCase):
    def test_save_game(self):
        with open('game_state.json', 'w') as f:
            f.write('{}')
        self.game = MagicMock()
        self.game.to_json = MagicMock(return_value='{"test":"123"}')
        JsonDB.save_game(self.game)
        with open('game_state.json', 'r') as f:
            text = f.read()
        self.assertEqual(text, '{"test":"123"}')

    def test_load_game_empty_file(self):
        with open('game_state.json', 'w') as f:
            f.write('')
        game = JsonDB.load_game()
        self.assertIsInstance(game, Game)
        with open('game_state.json', 'r') as f:
            game_state = json.loads(f.read())
            keys = list(game_state.keys())
        self.assertEqual(keys, ['accusee', 'in_progress', 'players'])

    def test_load_game_no_file(self):
        os.remove('game_state.json')
        game = JsonDB.load_game()
        self.assertIsInstance(game, Game)
        with open('game_state.json', 'r') as f:
            game_state = json.loads(f.read())
            keys = list(game_state.keys())
        self.assertEqual(keys, ['accusee', 'in_progress', 'players'])

    def test_load_game(self): # depends on Game, Player, Players, and save_game()
        with open('game_state.json', 'w') as f:
            f.write('{"accusee": null, "in_progress": false, "players": null}')
        game = JsonDB.load_game()
        self.assertIsInstance(game, Game)
        with open('game_state.json', 'r') as f:
            game_state = json.loads(f.read())
            keys = list(game_state.keys())
        self.assertEqual(keys, ['accusee', 'in_progress', 'players'])

    def test_clear(self):
        JsonDB.clear()
        with open('game_state.json', 'r') as f:
            text = f.read()
        self.assertEqual(text, '{}')