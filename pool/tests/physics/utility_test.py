import sys
import unittest

sys.path.append('../../src')

from physics.coordinates import Coordinates
from physics.utility import check_ray_circle_intersection, get_distance, check_ray_line_intersection, \
    get_ray_circle_intersection, get_line_endpoint_within_box, get_angle, get_parallel_line

FLOAT_PLACES = 7  # Rounding error for floating point equality

class CoordinatesTest(unittest.TestCase):

    def assertCoordinatesAlmostEqual(self, c_result: Coordinates, c_expected: Coordinates):
        """
        Custom test method to test if 2 vectors are almost equal.

        :param c_result: second coordinates to compare
        :param c_expected: first coordinates to compare
        :raises: AssertionError if not almost equal
        """
        self.assertAlmostEqual(c_result.x, c_expected.x,
                               msg='X-component: Result = {}, Expected = {}'.format(c_expected.x, c_result.x),
                               places=FLOAT_PLACES)
        self.assertAlmostEqual(c_result.y, c_expected.y,
                               msg='Y-component: Result = {}, Expected = {}'.format(c_expected.y, c_result.y),
                               places=FLOAT_PLACES)

    def test_check_ray_circle_intersection_straight(self):
        p1 = Coordinates(0, 0)
        p2 = Coordinates(0, 1)

        circle_mid = Coordinates(1, 0)

        # Test no intersecting
        circle_r = 0.99
        self.assertFalse(check_ray_circle_intersection(p1, p2, circle_mid, circle_r))

        # Test touching
        circle_r = 1.0
        self.assertTrue(check_ray_circle_intersection(p1, p2, circle_mid, circle_r))

        # Test intersecting
        circle_r = 1.1
        self.assertTrue(check_ray_circle_intersection(p1, p2, circle_mid, circle_r))

    def test_check_ray_circle_intersection_angled(self):
        p1 = Coordinates(0, 0)
        p2 = Coordinates(1, 1)

        circle_mid = Coordinates(1, 0)

        dist = get_distance(Coordinates(0.5, 0.5), circle_mid)

        # Test no intersecting
        circle_r = dist - 0.1
        self.assertFalse(check_ray_circle_intersection(p1, p2, circle_mid, circle_r))

        # Test touching
        circle_r = dist
        self.assertTrue(check_ray_circle_intersection(p1, p2, circle_mid, circle_r))

        # Test intersecting
        circle_r = dist + 0.1
        self.assertTrue(check_ray_circle_intersection(p1, p2, circle_mid, circle_r))

    def test_check_ray_line_intersection(self):
        # Parallel, vertical lines
        p1 = Coordinates(0, 0)
        p2 = Coordinates(0, 10)
        p3 = Coordinates(1, 0)
        p4 = Coordinates(1, 10)

        self.assertEqual(check_ray_line_intersection(p1, p2, p3, p4), None)

        # Perpendicular lines
        p1 = Coordinates(0, -10)
        p2 = Coordinates(0, 10)
        p3 = Coordinates(-10, 0)
        p4 = Coordinates(10, 0)

        self.assertEqual(check_ray_line_intersection(p1, p2, p3, p4), Coordinates(0, 0))

    def test_get_ray_circle_intersection(self):
        # Miss
        p1 = Coordinates(0, 0)
        p2 = Coordinates(10, 0)
        c = Coordinates(10, 1)
        r = 0.9

        result = get_ray_circle_intersection(p1, p2, c, r)

        self.assertEqual(result, None)

        # Tangent
        p1 = Coordinates(0, 0)
        p2 = Coordinates(10, 0)
        c = Coordinates(10, 1)
        r = 1

        result = get_ray_circle_intersection(p1, p2, c, r)

        self.assertEqual(result, Coordinates(10, 0))


        # Intersect
        p1 = Coordinates(0, 0)
        p2 = Coordinates(10, 0)
        c = Coordinates(10, 0)
        r = 1

        result = get_ray_circle_intersection(p1, p2, c, r)

        self.assertEqual(result, Coordinates(9, 0))

    def test_get_line_endpoint_within_box(self):
        # def get_line_endpoint_within_box(p1: Coordinates, angle: float, nw, se):

        # Establish box
        nw = Coordinates(0, 0)
        se = Coordinates(100, 100)

        # Point at the middle
        p1 = Coordinates(50, 50)

        # Test with different angles
        angle = 0
        result = get_line_endpoint_within_box(p1, angle, nw, se)
        expected = Coordinates(100, 50)
        # DEBUG
        print('For angle {}, got endpoint: {}'.format(angle, result))
        self.assertCoordinatesAlmostEqual(result, expected)

        angle = 45
        result = get_line_endpoint_within_box(p1, angle, nw, se)
        expected = Coordinates(100, 100)
        # DEBUG
        print('For angle {}, got endpoint: {}'.format(angle, result))
        self.assertCoordinatesAlmostEqual(result, expected)

        angle = 90
        result = get_line_endpoint_within_box(p1, angle, nw, se)
        expected = Coordinates(50, 100)
        # DEBUG
        print('For angle {}, got endpoint: {}'.format(angle, result))
        self.assertCoordinatesAlmostEqual(result, expected)

        angle = 135
        result = get_line_endpoint_within_box(p1, angle, nw, se)
        expected = Coordinates(0, 100)
        # DEBUG
        print('For angle {}, got endpoint: {}'.format(angle, result))
        self.assertCoordinatesAlmostEqual(result, expected)

        angle = 180
        result = get_line_endpoint_within_box(p1, angle, nw, se)
        expected = Coordinates(0, 50)
        # DEBUG
        print('For angle {}, got endpoint: {}'.format(angle, result))
        self.assertCoordinatesAlmostEqual(result, expected)

        angle = 225
        result = get_line_endpoint_within_box(p1, angle, nw, se)
        expected = Coordinates(0, 0)
        # DEBUG
        print('For angle {}, got endpoint: {}'.format(angle, result))
        self.assertCoordinatesAlmostEqual(result, expected)

        angle = 270
        result = get_line_endpoint_within_box(p1, angle, nw, se)
        expected = Coordinates(50, 0)
        # DEBUG
        print('For angle {}, got endpoint: {}'.format(angle, result))
        self.assertCoordinatesAlmostEqual(result, expected)

        angle = 315
        result = get_line_endpoint_within_box(p1, angle, nw, se)
        expected = Coordinates(100, 0)
        # DEBUG
        print('For angle {}, got endpoint: {}'.format(angle, result))
        self.assertCoordinatesAlmostEqual(result, expected)

        angle = 360
        result = get_line_endpoint_within_box(p1, angle, nw, se)
        expected = Coordinates(100, 50)
        # DEBUG
        print('For angle {}, got endpoint: {}'.format(angle, result))
        self.assertCoordinatesAlmostEqual(result, expected)

    def test_get_parallel_line(self):
        # def get_parallel_line(p1: Coordinates, p2: Coordinates, dist: float, top: bool) -> (Coordinates, Coordinates):

        ######################
        # Parallel to x-axis #
        ######################
        p1 = Coordinates(-1, 0)
        p2 = Coordinates(1, 0)
        dist = 1.0

        expected_angle = get_angle(p2, p1)

        result_top = get_parallel_line(p1, p2, dist, True)
        result_bot = get_parallel_line(p1, p2, dist, False)
        result_top_angle = get_angle(result_top[1], result_top[0])
        result_bot_angle = get_angle(result_bot[1], result_bot[0])

        # Check angles are the same
        self.assertEqual(expected_angle, result_top_angle)
        self.assertEqual(expected_angle, result_bot_angle)

        # Check distance apart
        self.assertAlmostEqual(dist, get_distance(p1, result_top[0]), FLOAT_PLACES)
        self.assertAlmostEqual(dist, get_distance(p2, result_top[1]), FLOAT_PLACES)

        ######################
        # Parallel to y-axis #
        ######################
        p1 = Coordinates(0, -1)
        p2 = Coordinates(0, 1)
        dist = 1.0

        expected_angle = get_angle(p2, p1)

        result_top = get_parallel_line(p1, p2, dist, True)
        result_bot = get_parallel_line(p1, p2, dist, False)

        result_top_angle = get_angle(result_top[1], result_top[0])
        result_bot_angle = get_angle(result_bot[1], result_bot[0])

        # Check angles are the same
        self.assertEqual(expected_angle, result_top_angle)
        self.assertEqual(expected_angle, result_bot_angle)

        # Check distance apart
        self.assertAlmostEqual(dist, get_distance(p1, result_top[0]), FLOAT_PLACES)
        self.assertAlmostEqual(dist, get_distance(p2, result_top[1]), FLOAT_PLACES)

        #####################
        # Parallel to y = x #
        #####################
        p1 = Coordinates(-1, -1)
        p2 = Coordinates(1, 1)
        dist = 1.0

        expected_angle = get_angle(p2, p1)

        result_top = get_parallel_line(p1, p2, dist, True)
        result_bot = get_parallel_line(p1, p2, dist, False)

        result_top_angle = get_angle(result_top[1], result_top[0])
        result_bot_angle = get_angle(result_bot[1], result_bot[0])

        # Check angles are the same
        self.assertEqual(expected_angle, result_top_angle)
        self.assertEqual(expected_angle, result_bot_angle)

        # Check distance apart
        self.assertAlmostEqual(dist, get_distance(p1, result_top[0]), FLOAT_PLACES)
        self.assertAlmostEqual(dist, get_distance(p2, result_top[1]), FLOAT_PLACES)



if __name__ == '__main__':
    unittest.main()
