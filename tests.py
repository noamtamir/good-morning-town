from unittest import TestCase, IsolatedAsyncioTestCase, TestSuite, TextTestRunner
from unittest.mock import MagicMock, patch
from game import Game
from messages import StatusMessage, WtfMessage


def mock_send_message(*args):
    print(args[0])

def mock_schedule_next_day_at(*args):
    print(f'scheduled task {args[1].__name__} at {args[0]}')

class TestDetermineAccusee(TestCase):
    def setUp(self):
        self.game = Game()
        self.game.players[0].accusee = self.game.players[1]

    def test_determine_accusee(self):
        self.game.determine_accusee()
        self.assertEqual(self.game.players[1], self.game.accusee)
        self.assertTrue(self.game.players[1].is_accused)
@patch('game.schedule_next_day_at', MagicMock(side_effect=mock_schedule_next_day_at))
@patch('game.send_message_to_room', MagicMock(side_effect=mock_send_message))
class TestVote2(IsolatedAsyncioTestCase):
    def setUp(self):
        self.game = Game()
        self.game.players[0].accusee = self.game.players[1]

    async def test_vote2(self):
        await self.game.vote2()
        self.assertEqual(self.game.players[1], self.game.accusee)
        self.assertTrue(self.game.players[1].is_accused)

@patch('game.schedule_next_day_at', MagicMock(side_effect=mock_schedule_next_day_at))
@patch('game.send_message_to_room', MagicMock(side_effect=mock_send_message))
class TestEndDay(IsolatedAsyncioTestCase):
    def setUp(self):
        self.game = Game()
        self.game.players[4].role = 'murderer'
        self.game.accusee = self.game.players[0]
        for player in self.game.players:
            player.kill_vote = True

    async def test_end_day(self):
        self.assertTrue(self.game.players[0].is_alive)
        await self.game.end_day()
        self.assertFalse(self.game.players[0].is_alive)


