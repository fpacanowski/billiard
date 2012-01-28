#!/usr/bin/env python

import pygame
from math import sqrt
import sys
import threading

RADIUS=20
POCKET_RADIUS=30
OFFSET_X=50
OFFSET_Y=50
WIDTH=800
HEIGHT=400
FPS=60
FRICTION=0.001/FPS
black    = (   0,   0,   0)
white    = ( 255, 255, 255)
green    = ( 100, 255, 100)
red      = ( 255,   0,   0)
 

def distance(pos1, pos2):
	return (pos1[0]-pos2[0])**2+(pos1[1] - pos2[1])**2

class Ball:
	def __init__(self,x,y,vx,vy):
		if type(x) != float or type(y) != float or \
		   type(vx) != float or type(vy) != float:
			raise TypeError
		self.pos = [x, y]
		self.x_velocity = vx
		self.y_velocity = vy
	def apply_friction(self, v):
		if abs(v) < FRICTION:
			v = 0.0
		else:
			v = (v/abs(v))*(abs(v)-FRICTION)
		return v
	def next_iter(self):
		#print self.pos
		(a,b) = self.pos
		(a,b) = (a+self.x_velocity, b+self.y_velocity)
		self.pos = [a,b]
		self.x_velocity = self.apply_friction(self.x_velocity)
		self.y_velocity = self.apply_friction(self.y_velocity)

class Simulation:
	def __init__(self):
		self.balls = {}
		self.processed = set()
		self.pockets = [[0.0, 0.0], [1.0, 0.0], [2.0, 0.0], \
		                [0.0, 1.0], [1.0, 1.0], [2.0, 1.0]]
	def add_ball(self, label, x, y, vx, vy):
		self.balls.update({label: Ball(x,y,vx/FPS,vy/FPS)})
	def next_iter(self):
		self.detect_collisions()
		for b in self.balls.itervalues():
			b.next_iter()
		res = self.result
		self.result = []
		return res
	def count_new_velocity(self, vel1, vel2, pos1, pos2):
		##print pos1,pos2,vel1,vel2
		v = [vel2[0]-vel1[0], vel2[1]-vel1[1]]
		direction = [pos2[0]-pos1[0],pos2[1]-pos1[1]]
		##print "*",v
		l = direction[0]**2 + direction[1]**2
		l = sqrt(l)
		direction = [direction[0]/l, direction[1]/l]
		dv_len = v[0]*direction[0] + v[1]*direction[1]
		dv = [dv_len*direction[0], dv_len*direction[1]]
		##print dv,direction
		#return [0.01, 0.0, -0.01, 0.0]
		r = [dv[0]+vel1[0], dv[1]+vel1[1], vel2[0]-dv[0], vel2[1]-dv[1]]
		##print dv,vel1
		##print dv[0],vel1[0],dv[0]+vel1[0]
		##print r 
		#sys.exit()
		return r
	def detect_collisions_with_walls(self, label):
		ball = self.balls[label]
		r = float(RADIUS)/HEIGHT
		(vx, vy) = (ball.x_velocity, ball.y_velocity)
		(x, y) = ball.pos
		if not (0+r < x < 2-r):
			vx *= -1
		if not (0+r < y < 1-r):
			vy *= -1
		ball.pos = [x,y]
		(ball.x_velocity, ball.y_velocity) = (vx, vy)
	
	def detect_collisions_with_balls(self, label):
		ball = self.balls[label]
		self.processed.add(label)
		r = float(RADIUS)/HEIGHT
		for l in self.balls.iterkeys():
			if l in self.processed:
				continue
			ball2 = self.balls[l]
			if distance(ball.pos, ball2.pos) < (2*r)**2:
				v1 = (ball.x_velocity, ball.y_velocity)
				v2 = (ball2.x_velocity, ball2.y_velocity)
				print label, l
				(ball.x_velocity,ball.y_velocity,ball2.x_velocity, ball2.y_velocity) = \
					self.count_new_velocity(v1,v2, ball.pos, ball2.pos)
			self.processed.add(l)
	def detect_collisions_with_pockets(self, label):
		ball = self.balls[label]
		r = float(RADIUS)/HEIGHT + float(POCKET_RADIUS)/HEIGHT
		for pocket_nr in range(6):
			pocket = self.pockets[pocket_nr]
			if distance(ball.pos, pocket) < r**2:
				self.result.append([label,pocket_nr])
	def detect_collisions(self):
		self.result = []
		for ball in self.balls.iterkeys():
			self.detect_collisions_with_walls(ball)
			self.detect_collisions_with_balls(ball)
			self.detect_collisions_with_pockets(ball)
		self.processed = set()
		for label, k in self.result:
			del self.balls[label]
	def get_balls(self):
		return [b.pos for b in self.balls]
	def step(self, nr):
		res = []
		for i in range(nr*FPS):
			res += self.next_iter()
		return res
	def is_stable(self):
		V = 0.0
		for b in self.balls.values():
			V += (b.x_velocity+b.y_velocity)
		return V == 0.0
class Interface(threading.Thread):
	def scale_position(self, pos):
		return (int(0.5*pos[0]*float(WIDTH))+OFFSET_X, int(pos[1]*float(HEIGHT))+OFFSET_Y)
	def __init__(self):
		self.balls = {}
		self.ball_colors = {0: black, 1: red}
		pygame.init()
		threading.Thread.__init__(self)
	def run(self):
		size = [900,600]
		screen = pygame.display.set_mode(size)
	
		pygame.display.set_caption("Bilard")
	
		done=False
	
		clock=pygame.time.Clock()
		screen.fill(green)
		pygame.display.update()
		while done==False:
			for event in pygame.event.get(): # User did something
				if event.type == pygame.QUIT: # If user clicked close
					done=True # Flag that we are done so we exit this loop 
			screen.fill(green)
			pygame.draw.rect(screen,black,[OFFSET_X,OFFSET_Y,WIDTH,HEIGHT], 2)
			for label in self.balls.iterkeys():
				pos = self.balls[label]
				col = self.ball_colors[label]
				pygame.draw.circle(screen,col,self.scale_position(pos),RADIUS)
			clock.tick(FPS)
			pygame.display.update()
		pygame.quit ()

class Biliard:
	def __init__(self):
		self.gui = Interface()
		self.gui.start()
		self.sim = Simulation()
		self.sim.add_ball(0, 0.2,0.2,-0.3,0.3)
		self.sim.add_ball(1, 0.7,0.7,-0.6,-0.6)
		clock = pygame.time.Clock()
		while True:
			self.gui.balls = {}
			for label, ball in self.sim.balls.iteritems():
				self.gui.balls[label] = ball.pos
			self.sim.next_iter()
			clock.tick(FPS)
		#self.

if __name__ == '__main__':
	Biliard()

