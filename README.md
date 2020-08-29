# Good Morning Town!

## Setup
In order for this bot to work, you need to add a `config.yml` file at the root. There is a `config-template.yml` which you can use to see how this file should look. The comments inisde are helpful and it is pretty self-explanatory.      
You MUST set up the Main Room in advance, as well as a private room with each player, in element/whatsapp. You need to retreive all user_ids and room_ids and input them into the `config.yml` file. All rooms should be unencrypted.

## Game Rules
* When a game is initiated, 2 Murderers and 1 Detective are randomly chosen and secretly assigned to the players. The rest of the players are Innocent Civilians. All are notified about their role via a private message.
* The game has three phases, NIGHT: 21:00 - 9:30, DAY: 9:00 - 20:00, and VOTES: 20:00-21:00.
* On the first day, the game rules are declared together with a dramatic opening speech, and the players get their roles.
### Day
* During the day, the town citizens may accuse each other for being a Murderer, and try to convince each other, who should be sent to the gallows.
### Votes
* At 20:00, the Town hold its daily Assembly, and holds 2 votes:
* Vote 1: Each citizen decalres, by name, who he thinks should be sent to the gallows. Vote ends at 20:30.
* Vote 2: The citizens vote whether the citizen with the greatest amount of votes on the first vote, should be killed or saved, Vote ends at 21:00, and the citizen is either killed or saved accordingly.
### Night
* During the night, the Detective can choose a player, and learn what his role is, secretly in a private message. Also the two Murderers can choose who they want to kill, secretly in a private message. If they both choose the same person, that person gets killed. If there is only 1 living Murderer, he always kills. On the following day, it is declared whether a murder has occured, and if so, who got killed.
* The Town, Civilians and Detective, win if both Murderers are dead. The Murderers win, when all but them are dead.

## WhatsApp Commands
### Group Commands
These are commands that can only be sent inside the main group chat. 

> `town init`  
> Initiate a new game, if no game is in progress. BTW- nobody can cancel a game once it has started.    
> `town accuse {name}`    
> Vote on the first vote of the Assembly, deciding who should be sent to the gallows.  
> `town kill`     
Vote on the second vote of the Assembly, deciding whether to kill or save the accusee.   
> `town save`   
> Decalring you vote against the kill. This is the default, so it is only useful in order to change your kill vote.   
### Private Commands
These are commands that can only be sent in a private chat with the bot.    

> `town detect {name}`    
> Learn the role of another player, only if you are the Detective.     
> `town murder {name}`    
> Attempt a murder during the night, only if you are a Murderer. If both Murderers pick the same player, he dies.` 