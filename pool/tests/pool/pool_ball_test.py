import unittest
import sys

sys.path.append('../../src')

from pool.pool_ball import PoolBall
from physics.coordinates import Coordinates
from physics.vector import Vector


class PoolBallTest(unittest.TestCase):

    def test_init(self):
        name = '1'
        pos = Coordinates(0, 0)
        mass = 1.0
        radius = 1.0

        p = PoolBall(name, pos, mass, radius)

        self.assertEqual(p.type, name)
        self.assertEqual(p.pos, pos)
        self.assertEqual(p.mass, mass)
        self.assertEqual(p.radius, radius)
        self.assertEqual(p.vel, Vector(0, 0))  # Default should be 0


if __name__ == '__main__':
    unittest.main()
