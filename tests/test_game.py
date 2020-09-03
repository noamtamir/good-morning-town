from unittest import TestCase
from game import Game
import json

class TestGame(TestCase):
    def setUp(self):
        self.game_dict = {'accusee': 'nobody', 'in_progress': False, 'players': {'noam': {'accusee': None, 'has_attempted_murder': False, 'has_detected': False, 'has_protected': False, 'is_accused': False, 'is_admin': True, 'is_alive': True, 'is_protected': False, 'kill_vote': False, 'murder_attempts': 0, 'name': 'nobody', 'role': 'civilian', 'room_id': '!gjXjBLkCgjjnxglfdd:matrix.org', 'user_id': '@noamtamir:matrix.org'}, 'town-bot': {'accusee': None, 'has_attempted_murder': False, 'has_detected': False, 'has_protected': False, 'is_accused': False, 'is_admin': False, 'is_alive': True, 'is_protected': False, 'kill_vote': False, 'murder_attempts': 0, 'name': 'nobody', 'role': 'civilian', 'room_id': '!HQazkBumGDRHMrAmSI:matrix.org', 'user_id': '@town-bot:matrix.org'}, 'town-bot2': {'accusee': None, 'has_attempted_murder': False, 'has_detected': False, 'has_protected': False, 'is_accused': False, 'is_admin': False, 'is_alive': True, 'is_protected': False, 'kill_vote': False, 'murder_attempts': 0, 'name': 'nobody', 'role': 'civilian', 'room_id': '!dCqgDxkIleCKlsMFwK:matrix.org', 'user_id': '@town-bot2:matrix.org'}, 'town-bot3': {'accusee': None, 'has_attempted_murder': False, 'has_detected': False, 'has_protected': False, 'is_accused': False, 'is_admin': False, 'is_alive': True, 'is_protected': False, 'kill_vote': False, 'murder_attempts': 0, 'name': 'nobody', 'role': 'civilian', 'room_id': '!htalQrogHYITBOsWDV:matrix.org', 'user_id': '@town-bot3:matrix.org'}, 'town-bot4': {'accusee': None, 'has_attempted_murder': False, 'has_detected': False, 'has_protected': False, 'is_accused': False, 'is_admin': False, 'is_alive': True, 'is_protected': False, 'kill_vote': False, 'murder_attempts': 0, 'name': 'nobody', 'role': 'civilian', 'room_id': '!YMXQGllJcKUdcaEsaP:matrix.org', 'user_id': '@town-bot4:matrix.org'}, 'town-bot5': {'accusee': None, 'has_attempted_murder': False, 'has_detected': False, 'has_protected': False, 'is_accused': False, 'is_admin': False, 'is_alive': True, 'is_protected': False, 'kill_vote': False, 'murder_attempts': 0, 'name': 'nobody', 'role': 'civilian', 'room_id': '!XfWrqsJMHWcytClqkY:matrix.org', 'user_id': '@town-bot5:matrix.org'}, 'yoav': {'accusee': None, 'has_attempted_murder': False, 'has_detected': False, 'has_protected': False, 'is_accused': False, 'is_admin': False, 'is_alive': True, 'is_protected': False, 'kill_vote': False, 'murder_attempts': 0, 'name': 'nobody', 'role': 'civilian', 'room_id': '!TqkAvjdrufUnAtsYwk:yoavmoshe.com', 'user_id': '@chat:yoavmoshe.com'}}}

    def test_from_dict(self):
        game = Game.from_dict(self.game_dict)
        self.assertIsInstance(game, Game)
        self.assertEqual(game.players.get_by_name('noam').__dict__, self.game_dict['players']['noam'])

    def test_to_json(self):
        game = Game.from_dict(self.game_dict)
        j = game.to_json()
        self.assertEqual(json.loads(j), self.game_dict)
