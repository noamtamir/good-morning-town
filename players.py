import json


class Player:
    def __init__(self, **data):
        self.name = 'nobody'
        self.user_id = ''
        self.room_id = ''
        self.is_admin = False
        self.is_alive = False
        self.role = 'civilian'
        self.accusee = None
        self.is_accused = False
        self.murder_attempts = 0
        self.has_attempted_murder = False
        self.has_detected = False
        self.has_protected = False
        self.is_protected = False
        self.__dict__.update(data)

    def __str__(self):
        return self.name

    def __repr__(self):
        return f'{self.name} {self.user_id}'

    @classmethod
    def from_dict(cls, data):
        return cls(**data)


class Players:
    def __init__(self, players):
        if players:
            self.as_list = [player_obj for player_name,
                            player_obj in players.items()]
            self.by_name = players
            self.by_user_id = {
                player_obj.user_id: player_obj for player_name, player_obj in players.items()}

    @classmethod
    def from_dict(cls, data):
        if not 'name' in data.keys():
            for player_name, player_obj in data.items():
                data[player_name]['name'] = player_name
        players = {player_name: Player.from_dict(
            player_data) for player_name, player_data in data.items()}
        return cls(players)

    def to_dict(self):
        players_dict = self.by_name.copy()
        return {player_name: player_obj.__dict__ for player_name, player_obj in players_dict.items()}

    def get_by_name(self, name):
        return self.by_name.get(name)

    def get_by_user_id(self, user_id):
        return self.by_user_id.get(user_id)
