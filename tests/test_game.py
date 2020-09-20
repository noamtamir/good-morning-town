from unittest import TestCase
from unittest.mock import patch, MagicMock
from game import Game
import json
from datetime import datetime, timedelta
from config import ASYNC_TASKS
from messages import StatusMessage, WtfMessage
from tests.test_utils import mock_send_message

# TODO: test all game class
# TODO: add single place for strings?


class TestGame(TestCase):
    def setUp(self):
        self.game_dict = {'accusee': 'nobody', 'in_progress': False, 'players': {'noam': {'accusee': None, 'has_attempted_murder': False, 'has_detected': False, 'has_protected': False, 'is_accused': False, 'is_admin': True, 'is_alive': True, 'is_protected': False, 'murder_attempts': 0, 'name': 'nobody', 'role': 'civilian', 'room_id': '!gjXjBLkCgjjnxglfdd:matrix.org', 'user_id': '@noamtamir:matrix.org'}, 'town-bot': {'accusee': None, 'has_attempted_murder': False, 'has_detected': False, 'has_protected': False, 'is_accused': False, 'is_admin': False, 'is_alive': True, 'is_protected': False, 'murder_attempts': 0, 'name': 'nobody', 'role': 'civilian', 'room_id': '!HQazkBumGDRHMrAmSI:matrix.org', 'user_id': '@town-bot:matrix.org'}, 'town-bot2': {'accusee': None, 'has_attempted_murder': False, 'has_detected': False, 'has_protected': False, 'is_accused': False, 'is_admin': False, 'is_alive': True, 'is_protected': False, 'murder_attempts': 0, 'name': 'nobody', 'role': 'civilian', 'room_id': '!dCqgDxkIleCKlsMFwK:matrix.org', 'user_id': '@town-bot2:matrix.org'}, 'town-bot3': {'accusee': None, 'has_attempted_murder': False, 'has_detected': False, 'has_protected': False, 'is_accused': False, 'is_admin': False,
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           'is_alive': True, 'is_protected': False, 'murder_attempts': 0, 'name': 'nobody', 'role': 'civilian', 'room_id': '!htalQrogHYITBOsWDV:matrix.org', 'user_id': '@town-bot3:matrix.org'}, 'town-bot4': {'accusee': None, 'has_attempted_murder': False, 'has_detected': False, 'has_protected': False, 'is_accused': False, 'is_admin': False, 'is_alive': True, 'is_protected': False, 'murder_attempts': 0, 'name': 'nobody', 'role': 'civilian', 'room_id': '!YMXQGllJcKUdcaEsaP:matrix.org', 'user_id': '@town-bot4:matrix.org'}, 'town-bot5': {'accusee': None, 'has_attempted_murder': False, 'has_detected': False, 'has_protected': False, 'is_accused': False, 'is_admin': False, 'is_alive': True, 'is_protected': False, 'murder_attempts': 0, 'name': 'nobody', 'role': 'civilian', 'room_id': '!XfWrqsJMHWcytClqkY:matrix.org', 'user_id': '@town-bot5:matrix.org'}, 'yoav': {'accusee': None, 'has_attempted_murder': False, 'has_detected': False, 'has_protected': False, 'is_accused': False, 'is_admin': False, 'is_alive': True, 'is_protected': False, 'murder_attempts': 0, 'name': 'nobody', 'role': 'civilian', 'room_id': '!TqkAvjdrufUnAtsYwk:yoavmoshe.com', 'user_id': '@chat:yoavmoshe.com'}}}

    def test_from_dict(self):
        game = Game.from_dict(self.game_dict)
        self.assertIsInstance(game, Game)
        self.assertEqual(game.players.get_by_name(
            'noam').__dict__, self.game_dict['players']['noam'])

    def test_to_json(self):
        game = Game.from_dict(self.game_dict)
        j = game.to_json()
        self.assertEqual(json.loads(j), self.game_dict)


class TestDetermineAccusee(TestCase):
    def setUp(self):
        self.game = Game()
        self.game.players.as_list[0].accusee = self.game.players.as_list[1].name

    def test_determine_accusee(self):
        self.game.determine_accusee()
        self.assertEqual(self.game.players.as_list[1], self.game.accusee)
        self.assertTrue(self.game.players.as_list[1].is_accused)


@patch('game.send_message_to_room', MagicMock(side_effect=mock_send_message))
class TestEndDay(TestCase):
    def setUp(self):
        self.game = Game()
        for player in self.game.players.as_list:
            player.is_alive = True
        self.game.players.as_list[4].role = 'murderer'
        self.game.players.as_list[2].accusee = 'noam'
        self.game.players.as_list[0].accusee = 'yoav'
        self.game.players.as_list[1].accusee = 'noam'

    def test_end_day(self):
        self.assertTrue(self.game.players.as_list[0].is_alive)
        self.game.end_day()
        self.assertFalse(self.game.players.as_list[0].is_alive)


@patch('game.send_message_to_room', MagicMock(side_effect=mock_send_message))
class TestBeginDay(TestCase):
    def setUp(self):
        self.game = Game()
        for player in self.game.players.as_list:
            player.is_alive = True
        self.game.players.as_list[4].role = 'murderer'
        self.game.players.as_list[3].murder_attempts = 1

    def test_begin_day(self):
        self.assertTrue(self.game.players.as_list[3].is_alive)
        self.game.begin_day()
        self.assertFalse(self.game.players.as_list[3].is_alive)


class TestGameStaticFunctions(TestCase):
    def setUp(self):
        self.game = Game()
        for player in self.game.players.as_list:
            player.is_alive = True
        self.game.players.as_list[0].is_alive = False

    def test_get_alive_status(self):
        alive_status = self.game.get_alive_status()
        self.assertFalse(alive_status['noam'])
        self.assertTrue(alive_status['yoav'])
