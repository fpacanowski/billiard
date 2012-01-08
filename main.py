#!/usr/bin/env python

import pygame

class Ball:
	def __init__(self):
		self.pos = [200,200]
		self.x_velocity = 2
		self.y_velocity = 2
	def next_step(self):
		(a,b) = self.pos
		self.pos = ((a+self.x_velocity)%400, (b+self.y_velocity)%400)
 
black    = (   0,   0,   0)
white    = ( 255, 255, 255)
green    = ( 100, 255,   100)
red      = ( 255,   0,   0)
 
pygame.init()
  
size = [640,480]
screen = pygame.display.set_mode(size)
 
pygame.display.set_caption("Bilard")
 
done=False
 
clock=pygame.time.Clock()
a = Ball()
b = Ball()
a.x_velocity *= -1 
while done==False:
	for event in pygame.event.get(): # User did something
		if event.type == pygame.QUIT: # If user clicked close
			done=True # Flag that we are done so we exit this loop 
	screen.fill(green)
	pygame.draw.circle(screen,red,a.pos,50)
	pygame.draw.circle(screen,black,b.pos,50) 
	a.next_step()
	b.next_step()
	clock.tick(60)
	pygame.display.flip()

pygame.quit ()
