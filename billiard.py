#!/usr/bin/env python

import pygame
from math import sqrt
import math
import sys
import threading

#Constants
RADIUS=10
POCKET_RADIUS=20
OFFSET_X=50
OFFSET_Y=120
WIDTH=800
HEIGHT=400
FPS=60
FRICTION=0.001/FPS
VMAX=1.0

#Color definitions
black = (0, 0, 0)
white = (255, 255, 255)
green = (100, 255, 100)
red = (255, 0, 0)
yellow = (255, 255, 0)
blue = (0, 0, 255)
orange = (255, 69, 0)
brown = (139, 69,19)
dgreen = (0, 255, 0)

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

	def distance(self, pos1, pos2):
		return (pos1[0]-pos2[0])**2+(pos1[1] - pos2[1])**2

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
		v = [vel2[0]-vel1[0], vel2[1]-vel1[1]]
		direction = [pos2[0]-pos1[0],pos2[1]-pos1[1]]
		l = direction[0]**2 + direction[1]**2
		l = sqrt(l)
		direction = [direction[0]/l, direction[1]/l]
		dv_len = v[0]*direction[0] + v[1]*direction[1]
		dv = [dv_len*direction[0], dv_len*direction[1]]
		r = [dv[0]+vel1[0], dv[1]+vel1[1], vel2[0]-dv[0], vel2[1]-dv[1]]
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
			if l == label or (label,l) in self.processed:
				continue
			ball2 = self.balls[l]
			if self.distance(ball.pos, ball2.pos) < (2*r)**2:
				v1 = (ball.x_velocity, ball.y_velocity)
				v2 = (ball2.x_velocity, ball2.y_velocity)
				(ball.x_velocity,ball.y_velocity,ball2.x_velocity, ball2.y_velocity) = \
					self.count_new_velocity(v1,v2, ball.pos, ball2.pos)
			self.processed.add((label,l))
			self.processed.add((l,label))

	def detect_collisions_with_pockets(self, label):
		ball = self.balls[label]
		r = float(POCKET_RADIUS)/HEIGHT
		for pocket_nr in range(6):
			pocket = self.pockets[pocket_nr]
			if self.distance(ball.pos, pocket) < r**2:
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
		self.angle = 0
		self.power = 0.5
		self.balls = {}
		self.ball_colors = {0: white, 1: red, 2: yellow, 3: blue, 4:dgreen, 5: brown,
				    6:orange, 7:red, 8: yellow, 9: blue, 10:dgreen,
				    11:brown, 12: orange, 13:red, 14:yellow, 15:blue}
		self.shots = []
		self.stable = True
		self.done=False
		self.new_game_request = True
		pygame.init()
		threading.Thread.__init__(self)
	def draw_table(self):
		pockets = [[0, 0], [WIDTH/2, 0], [WIDTH, 0], \
			   [0, HEIGHT], [WIDTH/2, HEIGHT], [WIDTH, HEIGHT]]

		self.screen.fill(green)
		pygame.draw.rect(self.screen,(102,51,0),[OFFSET_X,OFFSET_Y,WIDTH,HEIGHT], 20)
		pygame.draw.rect(self.screen,(0, 102,0),[OFFSET_X,OFFSET_Y,WIDTH,HEIGHT])
		for x,y in pockets:
			pygame.draw.circle(self.screen, black, [x+OFFSET_X, y+OFFSET_Y], POCKET_RADIUS)

	def draw_ball(self, label):
		pos = self.balls[label]
		col = self.ball_colors[label]
		pygame.draw.circle(self.screen,black,self.scale_position(pos),RADIUS+1)
		pygame.draw.circle(self.screen,col,self.scale_position(pos),RADIUS)
		if label == 0 and self.stable:
			self.draw_arrow(self.angle, self.scale_position(pos), self.power)

	def draw_arrow(self, angle, pos, length):
		angle = (angle/180.0)*math.pi
		(dx, dy) = (-100*length*math.sin(angle), -100*length*math.cos(angle))
		pygame.draw.aaline(self.screen, red, pos, [pos[0]+dx,pos[1]+dy])

	def draw_scores(self):
		font = pygame.font.Font(None, 50)
		c1 = (100, 255, 205)
		c2 = (159, 182, 205)
		if self.current_player == 1:
			(c1, c2) = (c2, c1)
		s1 = font.render('Player 1: %d'%self.scores[0], True, (255, 255, 255), c1)
		s2 = font.render('Player 2: %d'%self.scores[1], True, (255, 255, 255), c2)

		s1rect = s1.get_rect()
		s2rect = s2.get_rect()
		s1rect.centerx = 150
		s2rect.centerx = 730
		s1rect.centery = s2rect.centery = 50
		
		self.screen.blit(s1, s1rect)
		self.screen.blit(s2, s2rect)
	

	def run(self):
		self.screen = pygame.display.set_mode([900,600])
		pygame.display.set_caption("Billiard")

		#main event loop
		clock=pygame.time.Clock()
		while not self.done:
			#process events
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					self.done=True
				if event.type == pygame.KEYDOWN and self.stable:
					if event.key == pygame.K_LEFT:
						self.angle += 5
					elif event.key == pygame.K_RIGHT:
						self.angle -= 5
					elif event.key == pygame.K_UP:
						self.power = min(1.0, self.power+0.1)
					elif event.key == pygame.K_DOWN:
						self.power = max(0.1, self.power-0.1)
					elif event.key == pygame.K_SPACE:
						self.shots.append([self.angle, self.power])
				if event.type == pygame.KEYDOWN:
					if event.unicode == 'n':
						self.new_game_request = True
					if event.key == pygame.K_ESCAPE:
						self.done=True

			#do some drawing
			self.draw_table()
			self.draw_scores()
			for label in self.balls.iterkeys():
				self.draw_ball(label)
			pygame.display.update()

			clock.tick(FPS)
		pygame.quit ()
		sys.exit()


class Billiard:
	def new_game(self):
		self.scores = [0, 0]
		self.sim.add_ball(0, 0.5, 0.5, 0.0, 0.0)

		#build balls triangle
		for i in range(6):
			for j in range(i):
				self.sim.add_ball((i*(i-1))/2+j+1, 1.3+i*0.06, 0.5+j*0.06-i*0.03, 0.0, 0.0)
		
	def __init__(self):
		self.gui = Interface()
		self.gui.start()
		self.sim = Simulation()
		clock = pygame.time.Clock()
		self.gui.current_player = 0

		while not self.gui.done:
			current_player = self.gui.current_player

			#start new game if requested
			if self.gui.new_game_request:
				self.gui.new_game_request = False
				self.new_game()
			self.gui.balls = {}

			#has current player changed?
			if not self.gui.stable and self.sim.is_stable():
				current_player = (current_player+1)%2
				self.gui.current_player = current_player
			self.gui.stable = self.sim.is_stable()

			#update ball positions
			for label, ball in self.sim.balls.iteritems():
				self.gui.balls[label] = ball.pos

			#read shot command from interface and execute them
			if len(self.gui.shots) != 0:
				(angle, power) = self.gui.shots.pop()
				v = VMAX*power
				angle = (angle/180.0)*math.pi
				self.sim.balls[0].x_velocity = -v*math.sin(angle)/FPS
				self.sim.balls[0].y_velocity = -v*math.cos(angle)/FPS
			
			#check if player hit any pockets and update score
			res = self.sim.next_iter()
			if 0 in [p[0] for p in res]:
				self.sim.add_ball(0, 0.5, 0.5, 0.0, 0.0)
				self.scores[current_player] -= 1
			for ball, pocket in res:
				if ball != 0:
					self.scores[current_player] += 1
			self.gui.scores = self.scores

			clock.tick(FPS)


if __name__ == '__main__':
	Billiard()

