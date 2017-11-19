from tkinter import *
from Game import Game, Agent
from geometry import Point2D, Vector2D
import math
import random
import time

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











class PacMan(MovingBody):
    
    ACCELERATION   = 0.0
    MAX_SPEED      = 2.0

    def __init__(self,world):
        position0    = Point2D()
        velocity0    = Vector2D(.5,0.0)
        MovingBody.__init__(self,position0,velocity0,world)
        self.speed   = 0.0
        self.impulse = 0

    def color(self):
        return "#F0C080"

   
        
    def turn_left(self):
        self.velocity = Vector2D(-0.5,0)

    def turn_right(self):
        self.velocity = Vector2D(0.5,0)

    def turn_up(self):
        self.velocity = Vector2D(0,0.5)

    def turn_down(self):
        self.velocity = Vector2D(0,-0.5)

  

   
    

    

class PlayPacMan(Game):

    DELAY_START      = 150
    MAX_ASTEROIDS    = 6
    INTRODUCE_CHANCE = 0.01
    
    def __init__(self):
        Game.__init__(self,"ASTEROIDS!!!",60.0,45.0,800,600,topology='wrapped')

        self.number_of_asteroids = 0
        self.number_of_shrapnel = 0
        self.level = 1
        self.score = 0

        self.before_start_ticks = self.DELAY_START
        self.started = False

        self.PacMan = PacMan(self)

    def max_asteroids(self):
        return min(2 + self.level,self.MAX_ASTEROIDS)

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
        

print("Hit j and l to turn, i to create thrust, and SPACE to shoot. Press q to quit.")
game = PlayPacMan()
while not game.GAME_OVER:
    time.sleep(1.0/60.0)
    game.update()
