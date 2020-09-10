from unittest import TestCase
from unittest.mock import patch, MagicMock
from game import Game
import json
from datetime import datetime, timedelta
from config import ASYNC_TASKS


class TestGame(TestCase):
    def setUp(self):
        self.game_dict = {'accusee': 'nobody', 'in_progress': False, 'players': {'noam': {'accusee': None, 'has_attempted_murder': False, 'has_detected': False, 'has_protected': False, 'is_accused': False, 'is_admin': True, 'is_alive': True, 'is_protected': False, 'kill_vote': False, 'murder_attempts': 0, 'name': 'nobody', 'role': 'civilian', 'room_id': '!gjXjBLkCgjjnxglfdd:matrix.org', 'user_id': '@noamtamir:matrix.org'}, 'town-bot': {'accusee': None, 'has_attempted_murder': False, 'has_detected': False, 'has_protected': False, 'is_accused': False, 'is_admin': False, 'is_alive': True, 'is_protected': False, 'kill_vote': False, 'murder_attempts': 0, 'name': 'nobody', 'role': 'civilian', 'room_id': '!HQazkBumGDRHMrAmSI:matrix.org', 'user_id': '@town-bot:matrix.org'}, 'town-bot2': {'accusee': None, 'has_attempted_murder': False, 'has_detected': False, 'has_protected': False, 'is_accused': False, 'is_admin': False, 'is_alive': True, 'is_protected': False, 'kill_vote': False, 'murder_attempts': 0, 'name': 'nobody', 'role': 'civilian', 'room_id': '!dCqgDxkIleCKlsMFwK:matrix.org', 'user_id': '@town-bot2:matrix.org'}, 'town-bot3': {'accusee': None, 'has_attempted_murder': False, 'has_detected': False, 'has_protected': False, 'is_accused': False, 'is_admin': False,
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       'is_alive': True, 'is_protected': False, 'kill_vote': False, 'murder_attempts': 0, 'name': 'nobody', 'role': 'civilian', 'room_id': '!htalQrogHYITBOsWDV:matrix.org', 'user_id': '@town-bot3:matrix.org'}, 'town-bot4': {'accusee': None, 'has_attempted_murder': False, 'has_detected': False, 'has_protected': False, 'is_accused': False, 'is_admin': False, 'is_alive': True, 'is_protected': False, 'kill_vote': False, 'murder_attempts': 0, 'name': 'nobody', 'role': 'civilian', 'room_id': '!YMXQGllJcKUdcaEsaP:matrix.org', 'user_id': '@town-bot4:matrix.org'}, 'town-bot5': {'accusee': None, 'has_attempted_murder': False, 'has_detected': False, 'has_protected': False, 'is_accused': False, 'is_admin': False, 'is_alive': True, 'is_protected': False, 'kill_vote': False, 'murder_attempts': 0, 'name': 'nobody', 'role': 'civilian', 'room_id': '!XfWrqsJMHWcytClqkY:matrix.org', 'user_id': '@town-bot5:matrix.org'}, 'yoav': {'accusee': None, 'has_attempted_murder': False, 'has_detected': False, 'has_protected': False, 'is_accused': False, 'is_admin': False, 'is_alive': True, 'is_protected': False, 'kill_vote': False, 'murder_attempts': 0, 'name': 'nobody', 'role': 'civilian', 'room_id': '!TqkAvjdrufUnAtsYwk:yoavmoshe.com', 'user_id': '@chat:yoavmoshe.com'}}}

    def test_from_dict(self):
        game = Game.from_dict(self.game_dict)
        self.assertIsInstance(game, Game)
        self.assertEqual(game.players.get_by_name(
            'noam').__dict__, self.game_dict['players']['noam'])

    def test_to_json(self):
        game = Game.from_dict(self.game_dict)
        j = game.to_json()
        self.assertEqual(json.loads(j), self.game_dict)

    # @patch('game.run_at', MagicMock(side_effect=lambda scheduled, func: f'run {func} at {scheduled}'))
    # @patch('game.asyncio.create_task', MagicMock(side_effect=lambda func: MagicMock(return_value=func)))
    # def test_check_time_and_schedule(self):
    #     now = datetime.now()
    #     scheduled = now+timedelta(hours=1)
    #     Game.check_time_and_schedule(now, scheduled, lambda: 'func')
    #     self.assertIn(MagicMock(), ASYNC_TASKS)

# class TestGameAsync(IsolatedAsyncioTestCase):

        # if now > scheduled:
        #     scheduled += timedelta(days=1)
        # task = asyncio.create_task(
        #     run_at(
        #         scheduled,
        #         func()
        #     )
        # )
        # task.set_name(f'{str(func)} at {str(scheduled)}')
        # ASYNC_TASKS.append(task)

    # def test_initiate(self):
    #     pass
