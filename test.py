import unittest
import biliard

class TestSimulation(unittest.TestCase):
	def setUp(self):
		self.sim = biliard.Simulation()
		self.FPS = 100
	def test_adding_ball(self):
		self.sim.add_ball("ball", 0.0,0.0,0.0,0.0)
		with self.assertRaises(TypeError):
			self.sim.add_ball("ball", 0,0.0,0.0,0)
			self.sim.add_ball("ball", 0.0,'str',0.0,0)
	def test_ball_motion(self):
		(x, y) = (0.5, 0.5)
		self.sim.add_ball("ball", x, y, 0.01, 0.01)
		self.sim.step(10)
		self.assertNotEqual(x, self.sim.balls["ball"].pos[0])
	def test_collison_with_wall(self):
		self.sim.add_ball("ball", 0.5, 0.8, 0.0, 0.05)
		self.sim.step(10)
		self.assertTrue(self.sim.balls["ball"].y_velocity < 0)
		self.sim.add_ball("ball", 0.5, 0.2, 0.0, -0.05)
		self.sim.step(10)
		self.assertTrue(self.sim.balls["ball"].y_velocity > 0)
		self.sim.add_ball("ball", 1.8, 0.5, 0.05, 0.0)
		self.sim.step(10)
		self.assertTrue(self.sim.balls["ball"].x_velocity < 0)
		self.sim.add_ball("ball", 0.2, 0.5, -0.05, 0.0)
		self.sim.step(10)
		self.assertTrue(self.sim.balls["ball"].x_velocity > 0)
	def test_collision_with_two_balls(self):
		self.sim.add_ball("ball_1", 0.5, 0.5, 0.1, 0.0)
		self.sim.add_ball("ball_2", 0.9, 0.5, -0.1, 0.0)
		self.sim.step(10)
		self.assertTrue(self.sim.balls["ball_1"].x_velocity < 0)
		self.assertTrue(self.sim.balls["ball_2"].x_velocity > 0)


if __name__ == '__main__':
	unittest.main()
