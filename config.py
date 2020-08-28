import yaml

class Config:
    def __init__(self, **entries):
        self.__dict__.update(entries)

with open("config.yml", 'r') as f:
    config = Config(**yaml.safe_load(f))

CURRENT_GAME = None