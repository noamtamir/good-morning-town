# Good Morning Town!

## Setup

In order for this bot to work, you need to add a `config.yml` file at the root. There is a `config-template.yml` which you can use to see how this file should look. The comments inisde are helpful and it is pretty self-explanatory.  
You MUST set up the Main Room in advance, as well as a private room with each player, in element/whatsapp. You need to retreive all user_ids and room_ids and input them into the `config.yml` file. All rooms should be unencrypted.

Runs with `python 3.8.5`  
To run just install all dependecies from `requirements.txt`, and run `python matrix_client.py`.  
Run `python matrix_client.py some_other_config.yml` to run with different configurations (different rooms for example).

## Game Rules

- When a game is initiated, 2 Murderers and 1 Detective are randomly chosen and secretly assigned to the players. The rest of the players are Innocent Civilians. All are notified about their role via a private message.
- The game has three phases, NIGHT: 21:00 - 9:30, DAY: 9:00 - 20:00, and VOTES: 20:00-21:00.
- On the first day, the game rules are declared together with a dramatic opening speech, and the players get their roles.

### Day

- During the day, the town citizens may accuse each other for being a Murderer, and try to convince each other, who should be sent to the gallows.

### Vote

- At 20:30, the Town hold its daily Assembly, and holds a vote:
- Each citizen decalres, by name, who he thinks should be sent to the gallows. Vote ends at 21:00.
- The citizen with most votes is killed. If there is a tie, one of them dies.

### Night

- During the night, the Detective can choose a player, and learn what his role is, secretly in a private message.
- The two Murderers can choose who they want to kill, secretly in a private message. If they both choose the same person, that person gets killed. If there is only 1 living Murderer, he always kills.
- The Policeman can choose to protect 1 Civilian during the night, and if the Murderers attempt to kill him, he is protected.
- On the following day, it is declared whether a murder has occured, and if so, who got killed. If a murder was prevented, it will also be declared.

### Victory

- The Town, Civilians and Detective, win if both Murderers are dead. The Murderers win, when all but them are dead.

## WhatsApp Commands

### Group Commands

These are commands that can only be sent inside the main group chat.

> `town init`  
> Initiate a new game, if no game is in progress. BTW- nobody can cancel a game once it has started.  
> `town kill {name}`  
> Vote on who should be sent to the gallows.

### Private Commands

These are commands that can only be sent in a private chat with the bot.

> `town detect {name}`  
> Learn the role of another player, only if you are the Detective.  
> `town murder {name}`  
> Attempt a murder during the night, only if you are a Murderer. If both Murderers pick the same player, he dies.  
> `town protect {name}`  
> Protect a Civilian from being murdered during the night, only if you are a Policeman.  
> `town role`  
> Learn what your role is in case you forgot.

### Global Commands

These are commands that can be sent anywhere.

> `town say hello`  
> Check to see that the bot is active.  
> `town status`  
> Check who is alive and who is dead.  
> `town wtf`  
> When you're really pissed at the bot...

### Admin Commands

These are commands that can only be sent by admin (declared in config.yml).

> `town admin quit`  
> Quit game.  
> `town admin restart`  
> Restart game.  
> `town admin terminate {name}`  
> Terminate a player.
