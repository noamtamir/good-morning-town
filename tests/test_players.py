from unittest import TestCase
from players import Player, Players

class TestPlayer(TestCase):
    def setUp(self):
        self.player_dict = dict(
            name = 'test',
            user_id = '123',
            room_id = '456',
            is_admin = True,
            is_alive = False,
            role = 'detective',
            accusee = None,
            is_accused = True,
            kill_vote = False,
            murder_attempts = 1,
            has_attempted_murder = True,
            has_detected = False,
            has_protected = False,
            is_protected = True
        )
        
    def test_from_dict(self):
        player = Player.from_dict(self.player_dict)
        self.assertIsInstance(player, Player)
        self.assertEqual(player.name, self.player_dict.get('name'))
        self.assertEqual(player.role, self.player_dict.get('role'))
        self.assertTrue(player.is_protected)


class TestPlayers(TestCase): # depends on Player...
    def setUp(self):
        self.players_dict = {"noam": {"accusee": None, "has_attempted_murder": False, "has_detected": False, "has_protected": False, "is_accused": False, "is_admin": True, "is_alive": True, "is_protected": False, "kill_vote": False, "murder_attempts": 0, "name": "noam", "role": "civilian", "room_id": "!gjXjBLkCgjjnxglfdd:matrix.org", "user_id": "@noamtamir:matrix.org"}, "town-bot": {"accusee": None, "has_attempted_murder": False, "has_detected": False, "has_protected": False, "is_accused": False, "is_admin": False, "is_alive": True, "is_protected": False, "kill_vote": False, "murder_attempts": 0, "name": "town-bot", "role": "civilian", "room_id": "!HQazkBumGDRHMrAmSI:matrix.org", "user_id": "@town-bot:matrix.org"}, "town-bot2": {"accusee": None, "has_attempted_murder": False, "has_detected": False, "has_protected": False, "is_accused": False, "is_admin": False, "is_alive": True, "is_protected": False, "kill_vote": False, "murder_attempts": 0, "name": "town-bot2", "role": "civilian", "room_id": "!dCqgDxkIleCKlsMFwK:matrix.org", "user_id": "@town-bot2:matrix.org"}, "town-bot3": {"accusee": None, "has_attempted_murder": False, "has_detected": False, "has_protected": False, "is_accused": False, "is_admin": False, "is_alive": True, "is_protected": False, "kill_vote": False, "murder_attempts": 0, "name": "town-bot3", "role": "civilian", "room_id": "!htalQrogHYITBOsWDV:matrix.org", "user_id": "@town-bot3:matrix.org"}, "town-bot4": {"accusee": None, "has_attempted_murder": False, "has_detected": False, "has_protected": False, "is_accused": False, "is_admin": False, "is_alive": True, "is_protected": False, "kill_vote": False, "murder_attempts": 0, "name": "town-bot4", "role": "civilian", "room_id": "!YMXQGllJcKUdcaEsaP:matrix.org", "user_id": "@town-bot4:matrix.org"}, "town-bot5": {"accusee": None, "has_attempted_murder": False, "has_detected": False, "has_protected": False, "is_accused": False, "is_admin": False, "is_alive": True, "is_protected": False, "kill_vote": False, "murder_attempts": 0, "name": "town-bot5", "role": "civilian", "room_id": "!XfWrqsJMHWcytClqkY:matrix.org", "user_id": "@town-bot5:matrix.org"}, "yoav": {"accusee": None, "has_attempted_murder": False, "has_detected": False, "has_protected": False, "is_accused": False, "is_admin": False, "is_alive": True, "is_protected": False, "kill_vote": False, "murder_attempts": 0, "name": "yoav", "role": "civilian", "room_id": "!TqkAvjdrufUnAtsYwk:yoavmoshe.com", "user_id": "@chat:yoavmoshe.com"}}
    def test_from_dict(self):
        players = Players.from_dict(self.players_dict)
        self.assertIsInstance(players, Players)
        for player in players.as_list:
            self.assertIsInstance(player, Player)

    def test_to_dict(self):
        players = Players.from_dict(self.players_dict)
        players_dict = players.to_dict()
        self.assertEqual(self.players_dict, players_dict)
        pass