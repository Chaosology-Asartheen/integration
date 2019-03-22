import unittest
import sys

sys.path.append('../../src')

from physics.coordinates import Coordinates


class CoordinatesTest(unittest.TestCase):

    def test_init(self):
        c = Coordinates(0, 0)

        self.assertEqual(c.x, 0.0)
        self.assertEqual(c.y, 0.0)

        # Check type
        self.assertIsInstance(c.x, float)
        self.assertIsInstance(c.y, float)

    def test_equals(self):
        c0 = Coordinates(0, 0)
        c1 = Coordinates(0, 0)

        self.assertEqual(c0, c1)

    def test_not_equals(self):
        c0 = Coordinates(0, 0)
        c1 = Coordinates(0, 1)

        self.assertNotEqual(c0, c1)


if __name__ == '__main__':
    unittest.main()
