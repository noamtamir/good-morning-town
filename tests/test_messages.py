from unittest import TestCase
from unittest.mock import patch, MagicMock
from messages import Message, IgnoreInstructionMessages, PublicAlivePermission, \
    PublicPermission, AdminPermission, PrivatePermission, PrivateRolePermission
from test_utils import mock_send_message
from config import config


class ConcreteMessage(Message):
    def execute(self): pass

class TestMessage(TestCase):
    def setUp(self):
        room = MagicMock()
        room.room_id = '!123'
        event = MagicMock()
        event.body = 'body'
        event.sender = '@town-bot:matrix.org'
        self.message = ConcreteMessage(room, event, 'message')

    def test_execute_on_nobody(self):
        self.assertEqual(self.message.execute_on.name, 'nobody')

    def test_execute_on(self):
        self.message.event.body = 'body noam'
        self.assertEqual(self.message.execute_on.name, 'noam')


class TestIgnoreInstructionMessages(TestCase):
    def test_is_instruction(self):
        message = IgnoreInstructionMessages()
        message.body = 'test'
        self.assertFalse(message.is_instruction)
        message.body = 'just type'
        self.assertTrue(message.is_instruction)


@patch('messages.send_message_to_room', MagicMock(side_effect=mock_send_message))
class TestPublicAlivePermission(TestCase):
    def setUp(self):
        self.permission = PublicAlivePermission()
    
    def test_sender_is_dead(self):
        self.permission.sender = MagicMock()
        self.permission.sender.is_alive = False
        self.assertFalse(self.permission.authorized)
        
    def test_public_room(self):
        self.permission.sender = MagicMock()
        self.permission.sender.is_alive = True
        self.permission.room_id = '!1234'
        self.assertFalse(self.permission.authorized)

    def test_sender_authorized(self):
        self.permission.sender = MagicMock()
        self.permission.sender.is_alive = True
        self.permission.room_id = config.MAIN_ROOM_ID
        self.assertTrue(self.permission.authorized)

@patch('messages.send_message_to_room', MagicMock(side_effect=mock_send_message))
class TestPublicPermission(TestCase):
    def setUp(self):
        self.permission = PublicPermission()
        self.permission.sender = MagicMock()
    
    def test_public_room(self):
        self.permission.room_id = config.MAIN_ROOM_ID
        self.assertTrue(self.permission.authorized)
        self.permission.room_id = '!1234'
        self.assertFalse(self.permission.authorized)

@patch('messages.send_message_to_room', MagicMock(side_effect=mock_send_message))
class TestAdminPermission(TestCase):
    def test_is_admin(self):
        permission = AdminPermission()
        permission.sender = MagicMock()
        permission.room_id = '!123'
        permission.sender.is_admin = True
        self.assertTrue(permission.authorized)
        permission.sender.is_admin = False
        self.assertFalse(permission.authorized)

@patch('messages.send_message_to_room', MagicMock(side_effect=mock_send_message))
class TestPrivatePermission(TestCase):
    def test_public_room(self):
        permission = PrivatePermission()
        permission.sender = MagicMock()
        permission.sender.room_id = '!1234'
        permission.room_id = '!1234'
        self.assertTrue(permission.authorized) 
        permission.room_id = '!4321'
        self.assertFalse(permission.authorized) 


@patch('messages.send_message_to_room', MagicMock(side_effect=mock_send_message))
class TestPrivateRolePermission(TestCase):
    def setUp(self):
        self.permission = PrivateRolePermission()
        self.permission.sender = MagicMock()
        self.permission.room_id = '!1234'

    def test_not_same_room(self):
        self.permission.sender.room_id = '!4321'
        self.assertFalse(self.permission.authorized)

    def test_not_same_room(self):
        self.permission.sender.room_id = '!4321'
        self.assertFalse(self.permission.authorized)
    
    def test_not_allowed_role(self):
        self.permission.sender.room_id = '!1234'
        self.permission.allowed_role = 'test'
        self.permission.sender.role = 'wrong role'
        self.assertFalse(self.permission.authorized)

    def test_authorized(self):
        self.permission.sender.room_id = '!1234'
        self.permission.allowed_role = 'test'
        self.permission.sender.role = 'test'
        self.assertTrue(self.permission.authorized)