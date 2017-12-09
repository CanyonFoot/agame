from tkinter import *
from Game import Game, Agent
from geometry import Point2D, Vector2D
import math
import random
import time

TIME_STEP = 0.5
frameCounter = 0

# thank you stackoverflow
# https://stackoverflow.com/questions/1969240/mapping-a-range-of-values-to-another
# originally I used numpy
def translate(value, leftMin, leftMax, rightMin, rightMax):
    # Figure out how 'wide' each range is
    leftSpan = leftMax - leftMin
    rightSpan = rightMax - rightMin

    # Convert the left range into a 0-1 range (float)
    valueScaled = float(value - leftMin) / float(leftSpan)

    # Convert the 0-1 range into a value in the right range.
    return rightMin + (valueScaled * rightSpan)

class MovingBody(Agent):

    def __init__(self, p0, v0, world):
        self.velocity = v0
        self.accel    = Vector2D(0.0,0.0)
        Agent.__init__(self,p0,world)

    def color(self):
        return "#000080"

    def shape(self):
        p1 = self.position + Vector2D( 0.125, 0.125)
        p2 = self.position + Vector2D(-0.125, 0.125)
        p3 = self.position + Vector2D(-0.125,-0.125)
        p4 = self.position + Vector2D( 0.125,-0.125)
        return [p1,p2,p3,p4]

    def steer(self):
        return Vector2D(0.0)

    def update(self):
        self.position = self.position + self.velocity * TIME_STEP
        self.velocity = self.velocity + self.accel * TIME_STEP
        self.accel    = self.steer()
        self.world.trim(self)

# world kept in 45x60 matrix
# 1 = walls
# 0 = maze, contains a nugget
gameWorld = [ [ 1 for x in range(45) ] for x in range(30) ]

# small segment for pacman to always have a place to move
for x in range(5, 20):
    gameWorld[x][23] = 0

# random segment generator
def draw_vert(column, start, end):
    for x in range(start, end):
        gameWorld[column][x] = 0

def draw_hor(row, start, end):
    for x in range(start, end):
        gameWorld[x][row] = 0
def draw_map():
    draw_hor(23, 0, 30)
    firstnum = random.randint(5, 40)
    secondnum = random.randint(2, 28)
    while firstnum in (18, 28) or firstnum % 2 != 0:
        firstnum = random.randint(5, 40)
    draw_hor(firstnum, 0, 30)
    draw_hor(45 - firstnum, 0, 30)
    draw_vert(secondnum, firstnum, 45 - firstnum)
    draw_vert(30 - secondnum, firstnum, 45 - firstnum)
    draw_vert(secondnum, 45 - firstnum, firstnum)
    draw_vert(30 - secondnum, 45 - firstnum,  firstnum)
    draw_hor(firstnum//2, 0, 30)
    draw_hor(45 - firstnum//2, 0, 30)
    draw_vert(secondnum, firstnum//2, 45 - firstnum//2)
    draw_vert(30 - secondnum, firstnum//2, 45 - firstnum//2)

# random segment generator
for q in range(0, 10):
    x = random.randint(0, 29)
    y = random.randint(0, 44)
    upDown = random.randint(0,1)
    howFar = random.randint(0, 20)
    if upDown == 0:
        for l in range(0, howFar):
            gameWorld[x][y - l] = 0
    else:
        for l in range(0, howFar):
            gameWorld[x - l][y] = 0


draw_map()

# finger licking good
class Nugget(MovingBody):
    def __init__(self, world, x, y):
        position0 = Point2D(x, y)
        MovingBody.__init__(self, position0, Vector2D(0), world)

    def color(self):
        return "#F0C080"

    def remove(self):
        for i, nugget in enumerate(self.world.nuggets):
            if self == nugget:
                # move nugget to somewhere off the map
                self.world.nuggets[i].position = Point2D(300, 22)

# derrivative of agent that stays within map
class MazeBoundAgent(MovingBody):
    def __init__(self,world, speedMod = 1):
        position0    = Point2D(0,0)
        velocity0    = Vector2D(.5,0.0)
        MovingBody.__init__(self,position0,velocity0,world)
        # pacman will turn to intention's direciton when the path is clear
        self.direction = 'left'
        self.intention = self.direction
        # each turn, pacman is aligned to stay within the grid
        self.aligned = True
        '''
        when changing direcitons, especially on a 2x2+ wide rectangle,
        we add or subtract a bit to the rounding so that the MazeBoundAgent goes into the right collum or row
        '''
        self.verticalBias = 0
        self.horizontalBias = 0
        # we use this to slow the ghosts
        self.speedMod = speedMod

    def color(self):
        return 'green'

    def turn_left(self):
        self.intention = 'left'
        self.aligned = False

    def turn_right(self):
        self.intention = 'right'
        self.aligned = False

    def turn_up(self):
        self.intention = 'up'
        self.aligned = False

    def turn_down(self):
        self.intention = 'down'
        self.aligned = False

    def update(self):
        MovingBody.update(self)
        x = int(translate(self.position.x, 0, 30, -15, 15))
        y = int(translate(self.position.y, 0, 45, -22.5, 22.5))

        verticalBias = self.verticalBias
        horizontalBias = self.horizontalBias

        # when changing direcitons from horizontal to vertical or vice versa,
        # we use bias to make sure MazeBoundAgent ends up in the right collum/row
        bias = 0.5
        if self.direction == 'up':
            verticalBias = bias
            horizontalBias = 0
        elif self.direction == 'down':
            verticalBias = -bias
            horizontalBias = 0
        elif self.direction == 'left':
            verticalBias = 0
            horizontalBias = -bias
        elif self.direction == 'right':
            verticalBias = 0
            horizontalBias = bias

        # each time MazeBoundAgent turns, we realign it so it stays within the grid
        aligned = self.aligned
        clearance = 0.5
        if len(gameWorld) > abs(x - clearance):
            leftClear = gameWorld[int(x-clearance - 0.5)][y] == 0
        else:
            leftClear = gameWorld[int(x-clearance)][y] == 0
        if leftClear and self.intention == 'left':
            if not aligned:
                self.position.y = int(self.position.y + verticalBias)
                self.aligned = True
            self.direction = 'left'

        # whenever MazeBoundAgent intends to turn, it checks to see if the path is clear
        # when the path is clear, then MazeBoundAgent can turns
        rightClear = gameWorld[int(x+clearance)][y] == 0
        if rightClear and self.intention == 'right':
            if not aligned:
                self.position.y = int(self.position.y + verticalBias)
                self.aligned = True
            self.direction = 'right'

        if len(gameWorld[x]) - 0.5 > abs(y + clearance):
            upClear = gameWorld[x][int((y+clearance + 1) // 1)] == 0
        else:
            upClear = gameWorld[x][int((y+clearance) // 1)] == 0
        if upClear and self.intention == 'up':
            if not aligned:
                self.position.x = int(self.position.x + horizontalBias)
                self.aligned = True
            self.direction = 'up'

        if len(gameWorld[x]) > abs(y - clearance):
            downClear = gameWorld[x][int((y-clearance) // 1)] == 0
        else:
            downClear = gameWorld[x][int((y-clearance + 1) // 1)] == 0
        if downClear and self.intention == 'down':
            if not aligned:
                self.position.x = int(self.position.x + horizontalBias)
                self.aligned = True
            self.direction = 'down'

        # checks to see if we've hit a wall in the maze
        shift = 1
        speedMod = self.speedMod
        if self.direction == 'left':
            x = int(x - shift)
            if len(gameWorld) < x and gameWorld[x][y] == 1:
                self.velocity = Vector2D(0)
            else:
                self.velocity = Vector2D(-0.5 * speedMod,0)
        elif self.direction == 'right':
            x = int(x + shift - 1)
            if gameWorld[x][y] == 1:
                self.velocity = Vector2D(0)
            else:
                self.velocity = Vector2D(0.5 * speedMod,0)
        elif self.direction == 'up':
            y = int(y + shift)
            if gameWorld[x][y] == 1:
                self.velocity = Vector2D(0)
            else:
                self.velocity = Vector2D(0,0.5 * speedMod)
        elif self.direction == 'down':
            if gameWorld[x][y] == 1:
                self.velocity = Vector2D(0)
            else:
                self.velocity = Vector2D(0,-0.5 * speedMod)


class PacMan(MazeBoundAgent):
    def color(self):
        return "#F0C080"

    def shape(self):
        pacShape = []
        pacShape.append(self.position + Vector2D(-.25, -.5))
        pacShape.append(self.position + Vector2D(.25, -.5))
        pacShape.append(self.position + Vector2D(.5, -.25))
        pacShape.append(self.position + Vector2D(.5, .25))
        pacShape.append(self.position + Vector2D(.25, .5))
        pacShape.append(self.position + Vector2D(-.25, .5))
        pacShape.append(self.position + Vector2D(-.5, .25))
        pacShape.append(self.position + Vector2D(-.5, -.25))
        # pacmans 'mouth' is just the center point, we change where it is in the array to make it turn
        if self.direction == 'right':
            pacShape.insert(3, self.position + Vector2D(0,0))
        elif self.direction == 'up':
            pacShape.insert(5, self.position + Vector2D(0,0))
        elif self.direction == 'left':
            pacShape.insert(7, self.position + Vector2D(0,0))
        elif self.direction == 'down':
            pacShape.insert(1, self.position + Vector2D(0,0))
        return pacShape

    def update(self):
        MazeBoundAgent.update(self)
        for nugget in self.world.nuggets:
            if (nugget.position - self.position).magnitude() < 1:
                self.world.addPoints(1)
                nugget.remove()

class Ghost(MazeBoundAgent):
    lethal = False

    def shape(self):
        pacShape = []
        pacShape.append(self.position + Vector2D(-.25, -.5))
        pacShape.append(self.position + Vector2D(.25, -.5))
        pacShape.append(self.position + Vector2D(.5, -.25))
        pacShape.append(self.position + Vector2D(.5, .25))
        pacShape.append(self.position + Vector2D(.25, .5))
        pacShape.append(self.position + Vector2D(-.25, .5))
        pacShape.append(self.position + Vector2D(-.5, .25))
        pacShape.append(self.position + Vector2D(-.5, -.25))
        return pacShape

    def color(self):
        if self.lethal:
            return 'red'
        else:
            if frameCounter // 10 % 2 == 0:
                return 'green'
            else:
                return 'red'

    def update(self):
        if self.lethal == False:
            self.velocity = Vector2D(0)
        else:
            # ghosts check to see which direciton would get it closest to pacman and moves in that direction
            current = (self.position - self.world.PacMan.position).magnitude()
            gx = self.position.x
            gy = self.position.y
            px = self.world.PacMan.position.x
            py = self.world.PacMan.position.y
            mutateLeft = (Point2D(gx - 1, gy) - self.world.PacMan.position).magnitude()
            mutateRight = (Point2D(gx + 1, gy) - self.world.PacMan.position).magnitude()
            mutateDown = (Point2D(gx, gy - 1) - self.world.PacMan.position).magnitude()
            mutateUp = (Point2D(gx, gy + 1) - self.world.PacMan.position).magnitude()
            target = min(mutateLeft, mutateRight, mutateDown, mutateUp)
            if mutateLeft == target:
                self.intention = 'left'
            if mutateRight == target:
                self.intention = 'right'
            if mutateDown == target:
                self.intention = 'down'
            if mutateUp == target:
                self.intention = 'up'
            print(self.intention)
        MazeBoundAgent.update(self)
        if self.lethal and (self.position - self.world.PacMan.position).magnitude() < 1:
            self.world.gameOver = True

class PlayPacMan(Game):
    def __init__(self):
        Game.__init__(self,"PACMAN!!!",30.0,45.0,400,600,topology='wrapped')

        self.score = 0


        self.PacMan = PacMan(self)

        self.ghosts = []
        self.ghosts.append(Ghost(self, 0.5))

        self.nuggets = []
        self.walls = []

        counter = 0

        # any square with a value greater than 5 will have a wall drawn on it
        # squares immeidately adjacent (not diagonal) to nuggets have values added
        # Game.py will draw blue rectangles on any 5+ points in matrix
        wallMap = [ [ 0 for x in range(45) ] for x in range(30) ]

        for x, r in enumerate(gameWorld):
            for y, c in enumerate(r):
                h = translate(x, 0, 30, -15, 15) - 0.2
                v = translate(y, 0, 45, -22, 22) - 0.5
                if gameWorld[x][y] == 0:
                    self.nuggets.append(Nugget(self, h, v))

                    wallMap[x][y] -= 1000
                    if len(wallMap) > x+1:
                        wallMap[x+1][y] += 5
                    if len(wallMap) > x-1:
                        wallMap[x-1][y] += 5
                    if len(wallMap[x]) > y+1:
                        wallMap[x][y+1] += 5
                    if len(wallMap[x]) > y-1:
                        wallMap[x][y-1] += 5
        self.walls = wallMap

    def addPoints(self, p):
        self.score += 1
    def handle_keypress(self,event):
        Game.handle_keypress(self,event)
        if event.char == 'i':
            self.PacMan.speed_up()
        elif event.char == 'a':
            self.PacMan.turn_left()
        elif event.char == 'd':
            self.PacMan.turn_right()
        elif event.char == 'w':
            self.PacMan.turn_up()
        elif event.char == 's':
            self.PacMan.turn_down()
        elif event.char == 'p':
            self.paused = not self.paused


    def update(self):
        # Are we waiting to toss asteroids out?
        # haha no we are not. in fact, PacMan has no asteroids
        # this send text to Game.py, where it will display whatever string we put in here
        self.display = 'score: ' + str(self.score)
        Game.update(self)
        # add ghosts after 60 frames have been rendered
        if frameCounter == 60:
            for g in self.ghosts:
                g.lethal = True



game = PlayPacMan()
while not game.GAME_OVER:
    # time.sleep(1.0/60.0)
    game.update()
    frameCounter += 1
