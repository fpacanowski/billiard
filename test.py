import unittest
import billiard

class TestSimulation(unittest.TestCase):
	def setUp(self):
		self.sim = billiard.Simulation()
		self.FPS = 100
	def test_adding_ball(self):
		self.sim.add_ball("ball", 0.0,0.0,0.0,0.0)
		with self.assertRaises(TypeError):
			self.sim.add_ball("ball", 0,0.0,0.0,0)
			self.sim.add_ball("ball", 0.0,'str',0.0,0)
	def test_ball_motion(self):
		(x, y) = (0.5, 0.5)
		self.sim.add_ball("ball", x, y, 0.01, 0.01)
		self.sim.step(2)
		self.assertNotEqual(x, self.sim.balls["ball"].pos[0])
	def test_collison_with_wall(self):
		self.sim.add_ball("ball", 0.5, 0.8, 0.0, 0.3)
		self.sim.step(3)
		self.assertTrue(self.sim.balls["ball"].y_velocity < 0)
		self.sim.add_ball("ball", 0.5, 0.2, 0.0, -0.3)
		self.sim.step(3)
		self.assertTrue(self.sim.balls["ball"].y_velocity > 0)
		self.sim.add_ball("ball", 1.8, 0.5, 0.3, 0.0)
		self.sim.step(3)
		self.assertTrue(self.sim.balls["ball"].x_velocity < 0)
		self.sim.add_ball("ball", 0.2, 0.5, -0.3, 0.0)
		self.sim.step(3)
		self.assertTrue(self.sim.balls["ball"].x_velocity > 0)
	def test_collision_with_two_balls(self):
		self.sim.add_ball("ball_1", 0.7, 0.5, 0.3, 0.0)
		self.sim.add_ball("ball_2", 0.9, 0.5, -0.3, 0.0)
		self.sim.step(3)
		self.assertTrue(self.sim.balls["ball_1"].x_velocity < 0)
		self.assertTrue(self.sim.balls["ball_2"].x_velocity > 0)
	def test_ball_escaping_bounds(self):
		self.sim.add_ball("ball", 0.5, 0.5, 0.1, 0.1)
		self.sim.step(50)
		(x, y) = self.sim.balls["ball"].pos
		self.assertTrue(0 < x < 2)
		self.assertTrue(0 < y < 1)
	def test_ball_stopping(self):
		self.sim.add_ball("ball", 0.5, 0.5, 0.1, 0.2)
		self.sim.step(20)
		self.assertEqual(self.sim.balls["ball"].x_velocity, 0.0)
		self.assertEqual(self.sim.balls["ball"].y_velocity, 0.0)
	def test_ball_disappearing_after_hitting_pocket(self):
		self.sim.add_ball("ball", 0.5, 0.5, -0.3, -0.3)
		self.sim.step(3)
		self.assertEqual(len(self.sim.balls), 0)
	def test_result_feedback(self):
		self.sim.add_ball("ball", 0.5, 0.5, -0.3, -0.3)
		result = self.sim.step(3)
		self.assertTrue(["ball",0] in result)
	def test_is_stable(self):
		self.sim.add_ball("ball", 0.25, 0.5, 0.0, 0.1)
		self.assertFalse(self.sim.is_stable())
		self.sim.step(10)
		self.assertTrue(self.sim.is_stable())

if __name__ == '__main__':
	unittest.main()
