# agame
CSCI121 project 4: "agame," by Canyon Foot and Jasper Fung. The game, agame, is PacMan. The objective of agame is to eat all the chicken nuggets on the floor and not run into the scary ghosts. If you run into the scary ghosts, you will die. You have three lives. There are no more lives after three. If you eat a sriracha nugget (red), you will be able to eat the scary ghosts. You will be able to tell if the ghosts are scary or tasty by their color: red ghosts are scary, ultramarine ghosts are tasty, just like blue gatorade. If you eat all the nuggets and don't die, you win.
You can see your friends play at the same time as you: they appear as purple squares on your map, moving in their own dimension.

# Installation
1. clone this repository or download it in zip format [here](https://github.com/overwatchcorp/agame/archive/master.zip)

agame requires the `socketIO_client_nexus` library for our ***hi-tech*** multiplayer i n t e r f a c e (HiTMi t e r f a c e for short).
1. If you don't have pip, you will need to install it. Get pip [here](https://pip.pypa.io/en/stable/installing/).
2. run `pip install socketIO_client_nexus` to install the library globally.   
or use virtualenv if you know how to do that :)

# Playing agame
To play agame, run `python3 PacMan.py` or, if on mac, double-click on `MACS_CLICK_HERE_TO_PLAY.command` (or run `./MACS_CLICK_HERE_TO_PLAY.command`) to play.

# Gameplay Notes
w,s,a,d to control

p to pause

t to teleport to spawn point (for use if PacMan gets stuck)

red nuggets allow PacMan to eat the ghosts

Sometimes the ghosts get stuck, eat them to unstick

When a ghost kills PacMan, the characters will move to their spawn points, and the game will pause. Press p to unpause

# Work Breakdown
Jasper: Ghosts, Multiplayer, Movement, Nuggets, PacMan Shape, Walls, World Basics, Colors   
Canyon: Movements, Maze Generation, Standard Map Generation, Sriracha Nuggets, PacMan Death and Ghost Eating

# Points Breakdown
- 2 transporter (Wrapping)
- 2 win/lose
- 2 status (nuggets)
- 4 status (points and lives)
- 2 pausing
- 10 platform
- 2 megabomb (sriracha nuggets0)
- 4+ generated world (depth first search algorithm) (jim said we would get points)
- 5 AI
- 2 game over
- 3 redraw performance enhancement (walls only redraw on maze change)
- 4+ networked multiplayer
- 2 shield


**Important Note**  
I (Canyon) developed the depth first maze function after a conversation with Jim about what turned out to be a different method of random maze production that would be worth many points. I would not have been able to write my function without the help of the internet, but especially a piece of code I found at https://code.activestate.com/recipes/578356-random-maze-generator/.
I also consulted wikipedia.
