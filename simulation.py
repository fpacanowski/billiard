from math import sqrt

from conf import Conf

class Ball:
	def __init__(self,x,y,vx,vy):
		if type(x) != float or type(y) != float or \
		   type(vx) != float or type(vy) != float:
			raise TypeError
		self.pos = [x, y]
		self.x_velocity = vx
		self.y_velocity = vy

	def apply_friction(self, v):
		if abs(v) < Conf.FRICTION:
			v = 0.0
		else:
			v = (v/abs(v))*(abs(v)-Conf.FRICTION)
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
		self.balls.update({label: Ball(x,y,vx/Conf.FPS,vy/Conf.FPS)})

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
		r = float(Conf.RADIUS)/Conf.HEIGHT
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
		r = float(Conf.RADIUS)/Conf.HEIGHT
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
		r = float(Conf.POCKET_RADIUS)/Conf.HEIGHT
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
		for i in range(nr*Conf.FPS):
			res += self.next_iter()
		return res
	
	def is_stable(self):
		V = 0.0
		for b in self.balls.values():
			V += (b.x_velocity+b.y_velocity)
		return V == 0.0



