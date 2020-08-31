class Player:
    def __init__(self, name='nobody', user_id='', room_id='', is_admin=False): #default, empty player
        self.name = name
        self.user_id = user_id
        self.room_id = room_id   
        self.is_admin = is_admin     
        self.is_alive = True
        self.role = 'civilian'
        self.accusee = None
        self.is_accused = False
        self.kill_vote = False
        self.murder_attempts = 0
        self.has_attempted_murder = False
        self.has_detected = False
        self.has_protected = False
        self.is_protected = False
    
    def __str__(self):
        return self.name

    def __repr__(self):
        return f'{self.name} {self.user_id}'

class Players:
    @classmethod
    def from_config(cls, config):
        return [Player(player, config[player]['user_id'], config[player]['room_id'], config[player].get('is_admin', False)) for player in config]
