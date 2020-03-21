# [Twitter Poker Bot]
A TwitterBot that lets you play Texas Hold 'Em with other players in the comments of Tweets that this Bot makes.
The Bot serves as game master wand will comment about the the current and changes to the state of the game
Players get their hands and "chips"(no actual value just place holders) Dm'd to them. 
Each comment they make is an "action" they take in game

## Author:
George Aoyagi


## Technologies used and Dependencies needed:
Heroku
Deck of Cards API
Twitter API

##  Breakdown:
- Twitter.py: deals with posting tweets, comments, and Dm'ing players on twitter when needed
- TexasHold.py: deals with the workings of the game,


## TODO:
#twitter.py:
- Be able to tweet  [x]
- be able to reply to a tweet [x]
- be able to DM players [ ]
- Read through comments  [ ]
- be able to take the contents of a replay and figure what actions was done [ ]

#texasHold.py:
-  make a players object [x]
- create a new deck [x]
- make a game object [x]
- add a draw function [x]
- add a shuffle functionality [ ]
- add a bet functionality [x]
- add round end condition [ ]
- be able to last more than 1 round [  ]

#texasHold_test.py
