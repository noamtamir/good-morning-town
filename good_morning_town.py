import json
from random import sample
from collections import Counter
from contextlib import contextmanager


PLAYERS = ['noam', 'yuval', 'yoav', 'alon', 'ohad', 'ido', 'elad']
DEFAULT_ROLE = 'civilian'
INIT_GAME_STATE = {
    player: {
        'alive': True,
        'role': DEFAULT_ROLE,
        'candidate': None,
        'is_candidate': False,
        'kill_vote': False
        } for player in PLAYERS
    }


def load_game_state():
    with open('game_state.json', 'r') as f:
        game_state = json.loads(f.read())
    return game_state


def save_game_state(game_state):
    with open('game_state.json', 'w') as f:
        f.write(json.dumps(game_state))


@contextmanager
def update_game_state():
    game_state = load_game_state()
    try:
        yield game_state
    finally:
        save_game_state(game_state)


def update_player_field_if_alive(player, field, value):
    with update_game_state() as game_state:
        if game_state[player]['alive']:
            game_state[player][field] = value


def declare_new_game():
    #TODO: placeholder. write function
    # Send a message to the group with the game rules and declare that a new game has begun.
    print('Good Morning Town! A new game of The Town has now begun! Each of you has just received your role in a private message. The rules of the game are...')


def send_roles_to_players():
    #TODO: placeholder. write function
    game_state = load_game_state()
    print({player[0]: player[1]['role'] for player in game_state.items()})


def initiate_game():
    chosen_players = sample(PLAYERS, 3)
    for player in chosen_players[:2]:
        INIT_GAME_STATE[player]['role'] = 'murderer'
    INIT_GAME_STATE[chosen_players[2]]['role'] = 'detective'
    save_game_state(INIT_GAME_STATE)
    declare_new_game()
    send_roles_to_players()


def vote1():
    #TODO: placeholder. write function
    # Recurring function every night at 20:00
    # Send message to group
    print('Who should be sent to the gallow? You have until 20:30 to decide / change your mind.')
    

def vote_on_candidate(player, candidate):
    update_player_field_if_alive(player, 'candidate', candidate)


def determine_candidate():
    with update_game_state() as game_state:
        counter = Counter(list(filter(None, [player[1]['candidate'] for player in game_state.items()])))
        candidate = counter.most_common(1)[0][0] # If tied, then just pick the first one.
        game_state[candidate]['is_candidate'] = True
    return candidate


def vote2():
    # Recurring function every night at 20:30
    candidate = determine_candidate()
    # Send message to group
    print(f'Do you think {candidate} should be sent to the gallow? You have until 21:00 to decide / change your mind.')
    pass


def vote_on_kill(player, kill_vote):
    update_player_field_if_alive(player, 'kill_vote', kill_vote)


def get_candidate():
    game_state = load_game_state()
    candidate = [player[0] for player in game_state.items() if player[1]['is_candidate']][0]
    return candidate


def clear_votes():
    with update_game_state() as game_state:
        for player in game_state:
            game_state[player]['candidate'] = None
            game_state[player]['is_candidate'] = False
            game_state[player]['kill_vote'] = False

def end_day():
    # Recurring function every night at 21:00
    candidate = get_candidate()
    with update_game_state() as game_state:
        counter = Counter([player[1]['kill_vote'] for player in game_state.items()])
        accumulated_votes = dict(counter.most_common())
        alive = True
        if accumulated_votes[True] > accumulated_votes[False]:
            alive = False
            verdict = 'killed'
            game_state[candidate]['alive'] = alive
        else:
            verdict = 'saved'

    clear_votes()
    # Send message to group
    print(f'{candidate} has been {verdict}! Good night town!')
    pass

def get_alive_status():
    game_state = load_game_state()
    alive_status = {player[0]: player[1]['alive'] for player in game_state.items()}
    return alive_status
        

def begin_day():
    # Recurring function every morning at 9:00
    # Send message to group
    print('Good Morning Town! Tonight: x has been killed. This is that alive status:')
    print(get_alive_status())


initiate_game()
vote1()
vote_on_candidate('noam', 'yuval')
vote_on_candidate('yoav', 'yuval')
vote_on_candidate('ohad', 'ido')
vote2()
vote_on_kill('noam', True)
vote_on_kill('yoav', True)
vote_on_kill('alon', True)
vote_on_kill('elad', True)
end_day()
begin_day()


#TODO: Write regex for all functions except recurring ones.
pass