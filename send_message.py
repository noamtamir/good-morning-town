import asyncio
import requests
from config import config

async def send_message_to_room_async(message, room_id):
    response = requests.post(f'https://matrix.org/_matrix/client/r0/rooms/{room_id}/send/m.room.message',
    params={'access_token': config.ACCESS_TOKEN}, json={"msgtype":"m.text", "body": f"*The Town:* {message}"})
    return response

def send_message_to_room(message, room_id=config.MAIN_ROOM_ID):
    asyncio.ensure_future(send_message_to_room_async(message, room_id))