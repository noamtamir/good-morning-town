import yaml
import sys
import re

class Config:
    def __init__(self, **entries):
        self.__dict__.update(entries)

class TimeFromString:
    def __init__(self, string):
        self.string = string
    
    @property
    def tuple(self):
        return tuple(int(i) for i in self.string.split(':'))
    @property
    def dict(self):
        return dict(hour=self.tuple[0], minute=self.tuple[1], second=0, microsecond=0)
config_file = 'config.yml'
try:
    if re.search(r'\S+\.yml', sys.argv[1]):
        config_file = sys.argv[1]
except IndexError:
    pass

print(f'Loading config file: {config_file}')

with open("config.yml", 'r') as f:
    config = Config(**yaml.safe_load(f))

CURRENT_GAME = None
ASYNC_TASKS = []

TIME_OF = {}
for sched_task, time in config.SCHEDULE.items():
    TIME_OF[sched_task] = TimeFromString(time)

ROOMS = [config.PLAYERS[player]['room_id'] for player in config.PLAYERS]+ [config.MAIN_ROOM_ID]