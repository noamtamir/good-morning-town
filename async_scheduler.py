import asyncio
from datetime import datetime, timedelta, timezone
from config import ASYNC_TASKS, SCHEDULED_TASKS, TIME_OF
from db import JsonDB as db

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
    game = db.load_game()
    getattr(game, coro)()
    db.save_game(game)
    schedule_next_day(coro)


def schedule_next_day(func):
    time = TIME_OF[func]
    task = asyncio.create_task(
        run_at(
            (datetime.now(tz=TLV) + timedelta(days=1)
             ).replace(**time),
            func
        )
    )
    ASYNC_TASKS.append(task)


def schedule_votes():
    now = datetime.now(tz=TLV)
    for task, time in SCHEDULED_TASKS.items():
        scheduled_task_time = now.replace(**time)
        check_time_and_schedule(now, scheduled_task_time, task)


def check_time_and_schedule(now, scheduled, func):
    if now > scheduled:
        scheduled += timedelta(days=1)
    task = asyncio.create_task(
        run_at(
            scheduled,
            func
        )
    )
    task.set_name(f'{str(func)} at {str(scheduled)}')
    ASYNC_TASKS.append(task)
