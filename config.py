import yaml
import sys
import re


class Config:
    def __init__(self, **entries):
        self.__dict__.update(entries)


config_file = 'config.yml'
try:
    if re.search(r'\S+\.yml', sys.argv[1]):
        config_file = sys.argv[1]
except IndexError:
    pass

print(f'Loading config file: {config_file}')

with open("config.yml", 'r') as f:
    config = Config(**yaml.safe_load(f))

ROOMS = [config.PLAYERS[player]['room_id'] for player in config.PLAYERS] + [config.MAIN_ROOM_ID]


def time_from_string(time_str):
    time_as_list = [int(i) for i in time_str.split(':')]
    return dict(hour=time_as_list[0], minute=time_as_list[1], second=0, microsecond=0)

SCHEDULED_TASKS = {}
for task, time in config.SCHEDULE.items():
    SCHEDULED_TASKS[task.lower()] = time_from_string(time)

TIME_OF = SCHEDULED_TASKS

ASYNC_TASKS = []