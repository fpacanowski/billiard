#!/usr/bin/env python2

import math
import sys
import pygame

from simulation import Simulation
from interface import Interface
from conf import Conf

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
				v = Conf.VMAX*power
				angle = (angle/180.0)*math.pi
				self.sim.balls[0].x_velocity = -v*math.sin(angle)/Conf.FPS
				self.sim.balls[0].y_velocity = -v*math.cos(angle)/Conf.FPS
			
			#check if player hit any pockets and update score
			res = self.sim.next_iter()
			if 0 in [p[0] for p in res]:
				self.sim.add_ball(0, 0.5, 0.5, 0.0, 0.0)
				self.scores[current_player] -= 1
			for ball, pocket in res:
				if ball != 0:
					self.scores[current_player] += 1
			self.gui.scores = self.scores

			clock.tick(Conf.FPS)


if __name__ == '__main__':
	Billiard()

