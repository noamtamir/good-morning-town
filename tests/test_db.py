from unittest import TestCase
from unittest.mock import MagicMock
import json

from db import JsonDB, InMemoryJsonDB, in_memory_file
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

class TestInMemoryJsonDB(TestCase):
    def test_save_game(self):
        self.game = MagicMock()
        self.game.to_json = MagicMock(return_value='{"test":"123"}')
        InMemoryJsonDB.save_game(self.game)
        self.assertEqual(in_memory_file.getvalue(), '{"test":"123"}')

    def test_load_game_empty_stream(self):
        in_memory_file.truncate(0)
        in_memory_file.seek(0)
        game = InMemoryJsonDB.load_game()
        self.assertIsInstance(game, Game)
        keys = list(json.loads(in_memory_file.getvalue()).keys())
        self.assertEqual(keys, ['accusee', 'in_progress', 'players'])

    def test_load_game(self): # depends on Game, Player, Players, and save_game()
        in_memory_file.truncate(0)
        in_memory_file.seek(0)
        in_memory_file.write('{"accusee": null, "in_progress": false, "players": null}')
        game = InMemoryJsonDB.load_game()
        self.assertIsInstance(game, Game)
        keys = list(json.loads(in_memory_file.getvalue()).keys())
        self.assertEqual(keys, ['accusee', 'in_progress', 'players'])

    def test_clear(self):
        in_memory_file.truncate(0)
        in_memory_file.seek(0)
        in_memory_file.write('abcdefg')
        InMemoryJsonDB.clear()
        data = in_memory_file.getvalue()
        self.assertEqual(data, '{}')