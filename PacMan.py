from tkinter import *
from Game import Game, Agent
from geometry import Point2D, Vector2D
import math
import random
import time
import numpy

TIME_STEP = 0.5

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

world = [ [1] * 45 ] * 60
world[30] = [0] * 60
world[31] = [0] * 60
world[32] = [0] * 60
for r in world:
    r[30] = 0
    r[31] = 0
    r[32] = 0

class Nugget(MovingBody):
    def __init__(self, world, x, y):
        position0 = Point2D(x, y)
        MovingBody.__init__(self, position0, Vector2D(0), world)

    def color(self):
        return "#F0C080"

class PacMan(MovingBody):
    
    ACCELERATION   = 0.0
    MAX_SPEED      = 2.0

    def __init__(self,world):
        position0    = Point2D()
        velocity0    = Vector2D(.5,0.0)
        MovingBody.__init__(self,position0,velocity0,world)
        self.speed   = 0.0
        self.impulse = 0
        self.angle = 90
        self.direction = 'right'

    def color(self):
        return "#F0C080"
    
    def get_heading(self):
        angle = self.angle * math.pi / 180.0
        return Vector2D(math.cos(angle), math.sin(angle))

    def shape(self):
        h  = self.get_heading()
        hp = h.perp()
        print(hp)
        pacShape = []
        pacShape.append(self.position + Vector2D(-1, -2))
        pacShape.append(self.position + Vector2D(1, -2))
        pacShape.append(self.position + Vector2D(2, -1))
        pacShape.append(self.position + Vector2D(2, 1))
        pacShape.append(self.position + Vector2D(1, 2))
        pacShape.append(self.position + Vector2D(-1, 2))
        pacShape.append(self.position + Vector2D(-2, 1))
        pacShape.append(self.position + Vector2D(-2, -1))
        if self.direction == 'right':
            pacShape.insert(3, self.position + Vector2D(0,0))
        elif self.direction == 'up':
            pacShape.insert(5, self.position + Vector2D(0,0))
        elif self.direction == 'left':
            pacShape.insert(7, self.position + Vector2D(0,0))
        elif self.direction == 'down':
            pacShape.insert(1, self.position + Vector2D(0,0))
        return pacShape
        
    def turn_left(self):
        self.direction = 'left'
        self.velocity = Vector2D(-0.5,0)

    def turn_right(self):
        self.direction = 'right'
        self.velocity = Vector2D(0.5,0)

    def turn_up(self):
        self.direction = 'up'
        self.velocity = Vector2D(0,0.5)

    def turn_down(self):
        self.direction = 'down'
        self.velocity = Vector2D(0,-0.5)

    def update(self):
        MovingBody.update(self)
        x = int(numpy.interp(self.position.x, [-30, 30], [0, 60]))
        y = int(numpy.interp(self.position.y, [-22, 22], [0, 45]))
        print(x,y)
        if self.direction == 'right':
            x += 1
        elif self.direction == 'left':
            x -= 1
        elif self.direction == 'up':
            y += 1
        elif self.direction == 'down':
            y -= 1
        if world[x][y] == 1:
            self.velocity = Vector2D(0.0)
            
class PlayPacMan(Game):

    DELAY_START      = 150
    MAX_ASTEROIDS    = 6
    INTRODUCE_CHANCE = 0.01
    
    def __init__(self):
        Game.__init__(self,"PACMAN!!!",60.0,45.0,800,600,topology='wrapped')

        self.number_of_asteroids = 0
        self.number_of_shrapnel = 0
        self.level = 1
        self.score = 0

        self.before_start_ticks = self.DELAY_START
        self.started = False

        self.PacMan = PacMan(self)
        self.nuggets = []
        for x in range(-30, 30):
            for y in range(9, 10):
                self.nuggets.append(Nugget(self, x, y))
        for x in range(2, 3):
            for y in range(-30, 30):
                self.nuggets.append(Nugget(self, x, y))

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
        
        
    def update(self):
        # Are we waiting to toss asteroids out?
        if self.before_start_ticks > 0:
            self.before_start_ticks -= 1
        else:
            self.started = True
        
        # Should we toss a new asteroid out?
        

        Game.update(self)
        

game = PlayPacMan()
while not game.GAME_OVER:
    time.sleep(1.0/60.0)
    game.update()
