# agame
CSCI121 project 4: "agame," by Canyon Foot and Jasper Fung. The game, agame, is PacMan. The objective of agame is to eat all the chicken nuggets on the floor and not run into the scary ghosts. If you run into the scary ghosts, you will die. You have three lives. There are no more lives after three. If you eat a sriacha nugget (red), you will be able to eat the scary ghosts. You will be able to tell if the ghosts are scary or tasty by their color: red ghosts are scary, ultramarine ghosts are tasty, just like blue gatorade. If you eat all the nuggets and don't die, you win.
You can see your friends play at the same time as you: they appear as purple squares on your map, moving in their own dimension.

# Installation
agame requires the `socketIO_client_nexus` library for our hi-tech multiplayer functionality. Since there is no singleplayer option, you must install it.
1. If you don't have pip, you will need to install it. Instructions on how to install pip can be found [here](https://pip.pypa.io/en/stable/installing/).
2. run `pip install socketIO_client_nexus` to install the library globally.

# Playing agame
To play agame, run `python3 PacMan.py` or, if on mac, double-click on `MACS_CLICK_HERE_TO_PLAY.command` (or run `./MACS_CLICK_HERE_TO_PLAY.command`) to play.

# Points Breakdown
- 2 transporter
- 2 win/lose
- 2 status (nuggets)
- 4 status (points and lives)
- 2 pausing
- 10 platform
- 2 megabomb (sriacha nuggets0)
- 4+ generated world (depth first search algorithm) (jim said we would get points)
- 5 ai
- 2 game over
- 3 redraw performance enhancement (walls only redraw on maze change)
- 4 multiplayer
