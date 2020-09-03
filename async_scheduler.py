import asyncio
from datetime import datetime, timedelta, timezone
from config import ASYNC_TASKS

TLV = timezone(timedelta(hours=3))

async def wait_for(dt):
    # sleep until the specified datetime
    while True:
        now = datetime.now(tz=TLV)
        remaining = (dt - now).total_seconds()
        if remaining < 3600:
            break
        # asyncio.sleep doesn't like long sleeps, so don't sleep more
        # than a day at a time
        await asyncio.sleep(3600)
    await asyncio.sleep(remaining)

async def run_at(dt, coro):
    await wait_for(dt)
    return await coro


def schedule_next_day_at(time, func):
    task = asyncio.create_task(
            run_at(
                (datetime.now(tz=TLV) + timedelta(days=1)).replace(**time),
                func()
            )
        )
    ASYNC_TASKS.append(task)