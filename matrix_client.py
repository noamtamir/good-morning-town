import asyncio
from nio import AsyncClient, MatrixRoom, RoomMessageText
from config import config, ROOMS
from messages import MessageFactory, InitGameMessage


async def message_callback(room: MatrixRoom, event: RoomMessageText) -> None:
    if room.room_id not in ROOMS:
        return
    message = await MessageFactory.from_event(room, event)
    if message:
        message.execute()
    print(
        f"Message received in room {room.display_name}\n"
        f"{room.user_name(event.sender)} | {event.body}"
    )


async def main() -> None:
    client = AsyncClient(config.HOST_URL, config.CLIENT_ID)
    client.add_event_callback(message_callback, RoomMessageText)

    print(await client.login(password=config.PASSWORD))
    # members = await client.joined_members(config.MAIN_ROOM_ID)
    await client.sync_forever(timeout=30000)  # milliseconds

asyncio.get_event_loop().run_until_complete(main())
