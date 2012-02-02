import pygame
import math
import threading
import sys

from conf import Colors
from conf import Conf

class Interface(threading.Thread):
	def scale_position(self, pos):
		return (int(0.5*pos[0]*float(Conf.WIDTH))+Conf.OFFSET_X, int(pos[1]*float(Conf.HEIGHT))+Conf.OFFSET_Y)
	def __init__(self):
		self.angle = 0
		self.power = 0.5
		self.balls = {}
		self.ball_colors = {0: Colors.white, 1: Colors.red, 2: Colors.yellow, 3: Colors.blue, 4:Colors.dgreen, 5: Colors.brown,
				    6:Colors.orange, 7:Colors.red, 8: Colors.yellow, 9: Colors.blue, 10:Colors.dgreen,
				    11:Colors.brown, 12: Colors.orange, 13:Colors.red, 14:Colors.yellow, 15:Colors.blue}
		self.shots = []
		self.stable = True
		self.done=False
		self.new_game_request = True
		pygame.init()
		threading.Thread.__init__(self)
	def draw_table(self):
		pockets = [[0, 0], [Conf.WIDTH/2, 0], [Conf.WIDTH, 0], \
			   [0, Conf.HEIGHT], [Conf.WIDTH/2, Conf.HEIGHT], [Conf.WIDTH, Conf.HEIGHT]]

		self.screen.fill(Colors.green)
		pygame.draw.rect(self.screen,(102,51,0),[Conf.OFFSET_X, Conf.OFFSET_Y, Conf.WIDTH, Conf.HEIGHT], 20)
		pygame.draw.rect(self.screen,(0, 102,0),[Conf.OFFSET_X, Conf.OFFSET_Y, Conf.WIDTH, Conf.HEIGHT])
		for x,y in pockets:
			pygame.draw.circle(self.screen, Colors.black, [x+Conf.OFFSET_X, y+Conf.OFFSET_Y], Conf.POCKET_RADIUS)

	def draw_ball(self, label):
		pos = self.balls[label]
		col = self.ball_colors[label]
		pygame.draw.circle(self.screen,Colors.black,self.scale_position(pos), Conf.RADIUS+1)
		pygame.draw.circle(self.screen,col,self.scale_position(pos), Conf.RADIUS)
		if label == 0 and self.stable:
			self.draw_arrow(self.angle, self.scale_position(pos), self.power)

	def draw_arrow(self, angle, pos, length):
		angle = (angle/180.0)*math.pi
		(dx, dy) = (-100*length*math.sin(angle), -100*length*math.cos(angle))
		pygame.draw.aaline(self.screen, Colors.red, pos, [pos[0]+dx,pos[1]+dy])

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

			clock.tick(Conf.FPS)
		pygame.quit ()
		sys.exit()



