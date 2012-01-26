#!/usr/bin/env python

import pygame

RADIUS=20
OFFSET_X=50
OFFSET_Y=50
WIDTH=400
HEIGHT=200
FPS=60

class Ball:
	def __init__(self,x,y,vx,vy):
		self.pos = [float(x),float(y)]
		self.x_velocity = float(vx)
		self.y_velocity = float(vy)
	def next_iter(self):
		print self.pos
		(a,b) = self.pos
		(a,b) = (a+self.x_velocity, b+self.y_velocity)
		self.pos = [a,b]

class Simulation:
	def __init__(self):
		self.balls = []
	def add_ball(self, x, y, vx, vy):
		self.balls.append(Ball(x,y,vx/FPS,vy/FPS))
	def next_iter(self):
		self.detect_collisions()
		for b in self.balls:
			b.next_iter()
	def detect_collisions_with_walls(self):
		for ball in self.balls:
			(x, y) = ball.pos
			if not (0 < x < 2):
				x *= -1
			if not (0 < y < 1):
				y *= -1
	def detect_collisions(self):
		self.detect_collisions_with_walls()
	def get_balls(self):
		return [b.pos for b in self.balls]
 
black    = (   0,   0,   0)
white    = ( 255, 255, 255)
green    = ( 100, 255, 100)
red      = ( 255,   0,   0)
 
if __name__ == '__main__':
	pygame.init()

	size = [640,480]
	screen = pygame.display.set_mode(size)

	pygame.display.set_caption("Bilard")

	done=False

	clock=pygame.time.Clock()
	sim = Simulation()
	sim.add_ball(0.0,0.0,0.5,0.0)
	sim.add_ball(0.0,0.0,0.0,0.0)
	screen.fill(green)
	pygame.display.update()
	while done==False:
		for event in pygame.event.get(): # User did something
			if event.type == pygame.QUIT: # If user clicked close
				done=True # Flag that we are done so we exit this loop 
		screen.fill(green)
		balls = sim.balls
		a = balls[0]
		b = balls[1]
		ap = (int(a.pos[0]*WIDTH)+OFFSET_X, int(a.pos[1]*WIDTH)+OFFSET_Y)
		pygame.draw.circle(screen,red,ap,RADIUS)
		#pygame.draw.circle(screen,black,b.pos,RADIUS) 
		pygame.draw.rect(screen,black,[OFFSET_X,OFFSET_Y,OFFSET_X+WIDTH,OFFSET_Y+HEIGHT], 2)
		sim.next_iter()
		clock.tick(FPS)
		#pygame.display.update((ap[0]-20, ap[1]-20,ap[0]+20,ap[0]+20))
		pygame.display.update()
	pygame.quit ()
