from tkinter import *
from Game import Game, Agent
from geometry import Point2D, Vector2D
import math
import random
import time
import os

TIME_STEP = 0.5
frameCounter = 0
def round(x):
    if x - int(x) < .5:
        x = int(x)
    else:
        x = int(int(x) + 1)
    return x

# thank you stackoverflow
# https://stackoverflow.com/questions/1969240/mapping-a-range-of-values-to-another
# originally I used numpy - jasper
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
def draw_vert(column, start, end):
    for x in range(start, end):
        gameWorld[column][x] = 0

def draw_hor(row, start, end):
    for x in range(start, end):
        gameWorld[x][row] = 0
def draw_map():
    # Draws the basic map
    draw_hor(40,0,30)
    draw_hor(23,0,30)
    draw_hor(6, 0, 30)
    draw_vert(15, 6, 40)
    draw_vert(7, 6, 40)
    draw_vert(24, 6, 40)
    draw_hor(15, 0, 15)
    draw_hor(15, 15, 30)

def draw_maze():
    x_vector = [0, 1, 0, -1]
    y_vector = [-1, 0, 1, 0]
    # This function uses a depth first search to construct a random maze
    coordinate_list = [(random.randint(0,45), random.randint(0,30), 0)]

    while len(coordinate_list) > 0:
        (cur_x, cur_y, cur_direction) = coordinate_list[-1]
        if len(coordinate_list) > 3:
            if cur_direction != coordinate_list[-2][2]:
                direction_set = [cur_direction]
            else:
                direction_set = range(4)
        else:
            direction_set = range(4)


        gameWorld[cur_x][cur_y] = 0
        possible_squares = []
        for q in range(4):
            new_x = cur_x + x_vector[q]
            new_y = cur_y + y_vector[q]
            if new_x >= 0 and new_x < 29 and new_y >= 0 and new_y < 44:
                if gameWorld[new_x][new_y] == 1:
                    check = 0
                    for p in range(4):
                        future_x = new_x + x_vector[p]
                        future_y = new_y + y_vector[p]
                        if future_x >= 0 and future_x < 29 and future_y >= 0 and future_y < 44:
                            if gameWorld[future_x][future_y] == 0:
                                check += 1
                    if check == 1:
                        possible_squares.append(q)
        if len(possible_squares) > 0:
            direction = cur_direction
            pot_direction = possible_squares[random.randint(0, len(possible_squares) - 1)]
            if pot_direction != 2 or pot_direction != 4:
                pot_direction = possible_squares[random.randint(0, len(possible_squares) - 1)]
            if pot_direction != direction:
                if random.randint(0,9) > 7:
                    direction = pot_direction
            cur_x = cur_x + x_vector[direction]
            cur_y = cur_y + y_vector[direction]
            coordinate_list.append((cur_x, cur_y, direction))
            # Uses random numbers to create a bias toward continuing in one direction
            # to make maze paths longer
        else:
            coordinate_list.pop()

randommap = input('do you want a randomly generated map (y/n)')
if randommap.lower() == 'y':
    # algorithmically genearted rabndom maze
    draw_maze()
else:
    # the same map every time
    draw_map()

# finger licking good
class Nugget(MovingBody):
    def __init__(self, world, x, y, type):
        position0 = Point2D(x, y)
        MovingBody.__init__(self, position0, Vector2D(0), world)
        self.type = type

    def color(self):
        if self.type == 'normal':
            return "#F0C080"
        elif self.type == 'red':
            return "#FF0000"

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
        x = round(translate(self.position.x, 0, 30, -15, 15))
        y = round(translate(self.position.y, 0, 45, -22.5, 22.5))
        if gameWorld[x][y] == 1:
            if x > 1 and gameWorld[x-1][y] == 0:
                self.position.x = translate(x - .5, -15, 15, 0, 30)
            elif x < 30 and gameWorld[x+1][y] == 0:
                self.position.x = translate(x + .5, -15, 15, 0, 30)
            elif y > 0 and gameWorld[x][y-1] == 0:
                self.position.y = translate(y - .5, -22.5, 22.5, 0, 45)
            elif y < 45 and gameWorld[x][y+1] == 0:
                self.position.y = translate(y + .5, -22.5, 22.5, 0, 45)

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
            leftClear = gameWorld[round(x-clearance - 0.5)][y] == 0
        else:
            leftClear = gameWorld[round(x-clearance)][y] == 0
        if leftClear and self.intention == 'left':
            if not aligned:
                self.position.y = round(self.position.y + verticalBias)
                self.aligned = True
            self.direction = 'left'

        # whenever MazeBoundAgent intends to turn, it checks to see if the path is clear
        # when the path is clear, then MazeBoundAgent can turns
        rightClear = gameWorld[round(x+clearance)][y] == 0
        if rightClear and self.intention == 'right':
            if not aligned:
                self.position.y = round(self.position.y + verticalBias)
                self.aligned = True
            self.direction = 'right'

        if len(gameWorld[x]) - 0.5 > abs(y + clearance):
            upClear = gameWorld[x][round((y+clearance + 1) // 1)] == 0
        else:
            upClear = gameWorld[x][round((y+clearance) // 1)] == 0
        if upClear and self.intention == 'up':
            if not aligned:
                self.position.x = round(self.position.x + horizontalBias)
                self.aligned = True
            self.direction = 'up'

        if len(gameWorld[x]) > abs(y - clearance):
            downClear = gameWorld[x][round((y-clearance) // 1)] == 0
        else:
            downClear = gameWorld[x][round((y-clearance + 1) // 1)] == 0
        if downClear and self.intention == 'down':
            if not aligned:
                self.position.x = round(self.position.x + horizontalBias)
                self.aligned = True
            self.direction = 'down'

        # checks to see if we've hit a wall in the maze
        shift = 1
        speedMod = self.speedMod
        if self.direction == 'left':
            x = round(x - shift)
            if len(gameWorld) < x and gameWorld[x][y] == 1:
                self.velocity = Vector2D(0)
            else:
                self.velocity = Vector2D(-0.5 * speedMod,0)
        elif self.direction == 'right':
            x = round(x + shift - 1)
            if gameWorld[x][y] == 1:
                self.velocity = Vector2D(0)
            else:
                self.velocity = Vector2D(0.5 * speedMod,0)
        elif self.direction == 'up':
            y = round(y + shift)
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
    def __init__(self,world, speedMod = 1):
        self.eat_mode = False
        self.eat_mode_ticks = 0
        self.lives = 3
        MazeBoundAgent.__init__(self,world)
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

        if self.eat_mode == True:
            self.eat_mode_ticks += 1
        if self.eat_mode_ticks >= 100:
            self.eat_mode = False
            self.eat_mode_ticks = 0

        MazeBoundAgent.update(self)
        for nugget in self.world.nuggets:
            if (nugget.position - self.position).magnitude() < 1:
                self.world.addPoints(1)
                self.world.nuggets_eaten += 1
                nugget.remove()
                if nugget.type == 'red':
                    self.eat_mode = True


class Ghost(MazeBoundAgent):

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
            # aquamarine
            return '#00FFFF'


    def update(self):

        if self.world.PacMan.eat_mode == True:
            self.lethal = False
        else:
            self.lethal = True
        use_rand = 1
        # ghosts check to see which direciton would get it closest to pacman and moves in that direction
        if use_rand == 1:
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




        MazeBoundAgent.update(self)
        if self.lethal and (self.position - self.world.PacMan.position).magnitude() < 1:
            y = -10
            for g in self.world.ghosts:
                g.position.x = -8
                g.position.y = y
                y += 4
                g.intention = 'up'
                g.direction = 'up'

            self.world.PacMan.lives -= 1
            self.world.PacMan.position.x = 0
            self.world.PacMan.position.y = 0

            game.paused = True

        if self.world.PacMan.eat_mode == True:
            self.velocity= -self.velocity
        if self.world.PacMan.eat_mode == True and (self.position - self.world.PacMan.position).magnitude() < 1:
            self.world.addPoints(20)
            self.position.x = 0
            self.position.y = 0

class PlayPacMan(Game):
    def __init__(self):
        Game.__init__(self,"PACMAN!!!",30.0,45.0,400,600,topology='wrapped')

        self.score = 0
        self.nuggets_eaten = 0

        self.PacMan = PacMan(self)

        self.ghosts = []
        g1 = Ghost(self, 0.6)
        g2 = Ghost(self, 0.6)
        g3 = Ghost(self, 0.6)

        self.ghosts.append(g1)
        self.ghosts.append(g2)
        self.ghosts.append(g3)

        g1.position.x = 4
        g1.position.y = 16.5

        g2.position.x = 26
        g2.position.y = 16.5

        g3.position.x = 27
        g3.position.y = -16.5

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
                    counter += 1

                    if counter % 31  == 0:
                        Nugget.type = 'red'
                        self.nuggets.append(Nugget(self, h, v, 'red'))
                    else:
                        self.nuggets.append(Nugget(self, h, v, 'normal'))



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
        elif event.char == 't':
            self.PacMan.position.x = 0
            self.PacMan.position.y = 0


    def update(self):
        # Are we waiting to toss asteroids out?
        # haha no we are not. in fact, PacMan has no asteroids
        # this send text to Game.py, where it will display whatever string we put in here
        self.display = '_______           Score: ' + str(self.score) + ' Lives ' + str(self.PacMan.lives)
        if self.PacMan.lives <= 0:
            game.GAME_OVER = True
        if self.nuggets_eaten == len(self.nuggets):
            self.display = "_________        YOU WIN!" + " Final Score:" + str(self.score)
            Game.update(self)
            self.paused = True
        Game.update(self)

game = PlayPacMan()
while not game.GAME_OVER:
    # time.sleep(1.0/60.0)
    game.update()
    frameCounter += 1
