from unittest import TestCase, IsolatedAsyncioTestCase, mock
from game import Game
from messages import StatusMessage, WtfMessage


class TestDetermineAccusee(TestCase):
    def setUp(self):
        self.game = Game()
        self.game.players[0].accusee = self.game.players[1]

    def test_determine_accusee(self):
        self.game.determine_accusee()
        self.assertEqual(self.game.players[1], self.game.accusee)
        self.assertTrue(self.game.players[1].is_accused)


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