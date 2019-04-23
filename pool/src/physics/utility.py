"""
Utility class to hold various functions.
"""
from typing import Optional

import numpy as np

from pool.src.physics.coordinates import Coordinates
from pool.src.physics.vector import Vector


def get_distance(a: Coordinates, b=Coordinates(0, 0)) -> float:
    """
    Calculate the distance between two points.

    :param a: point a
    :param b: point b, default is origin (0, 0)
    :return: distance
    """

    return np.sqrt((a.x - b.x) ** 2 + (a.y - b.y) ** 2)


def get_angle(a: Coordinates, b=Coordinates(0, 0)) -> float:
    """
    Calculate the angle (relative to positive x-axis) of a relative to b.
    i.e. b becomes the origin

    :param a: point a
    :param b: point b, default is origin (0, 0)
    :return: angle of a to b (degrees)
    """

    y = a.y - b.y
    x = a.x - b.x

    # print('get_angle, relative point is ({}, {})'.format(x, y))

    if x == y == 0:
        return None  # FIXME: Best return value for 'no angle'?
    elif x == 0:
        if y > 0:
            return 90.0
        elif y < 0:
            return 270.0
    elif y == 0:
        if x > 0:
            return 0.0
        else:
            return 180.0

    # Compute raw angle (between -90 and 90)
    raw_angle = np.degrees(np.arctan(y / x))

    if x > 0 and y > 0:  # Quadrant 1
        return raw_angle
    elif x < 0 and y > 0:  # Quadrant 2
        return 180.0 + raw_angle
    elif x < 0 and y < 0:  # Quadrant 3
        return 180.0 + raw_angle
    else:  # Quadrant 4
        return (360.0 + raw_angle) % 360.0


def check_ray_circle_intersection(p1: Coordinates, p2: Coordinates, c_mid: Coordinates, c_radius: float):
    """
    Check whether a ray intersects a circle.

    :param p1: starting point of ray
    :param p2: end point of ray
    :param c_mid: coordinates for the center of the circle
    :param c_radius: radius of the circle
    :return: True if intersection; False otherwise
    """

    # Source: https://stackoverflow.com/a/1084899

    # d is direction vector of ray, from start to end
    # f is direction Vector from center sphere to ray start
    d = Vector(p2.y - p1.y, p2.x - p1.x)
    f = Vector(p1.y - c_mid.y, p1.x - c_mid.x)

    a = d.dot_product(d)
    b = 2 * f.dot_product(d)
    c = f.dot_product(f) - c_radius ** 2

    discriminant = b * b - 4 * a * c

    if discriminant < 0:
        return False
    else:
        discriminant = np.sqrt(discriminant)

        t1 = (-b - discriminant) / (2 * a)
        t2 = (-b + discriminant) / (2 * a)

        return (0 <= t1 <= 1) or (0 <= t2 <= 1)


def check_point_on_line_segment(x, y, p1, p2):
    return p1.x <= x <= p2.x and p1.y <= y <= p2.y

def check_ray_line_intersection(p1: Coordinates, p2: Coordinates,
                                p3: Coordinates, p4: Coordinates) -> Optional[Coordinates]:
    """
    Check whether a ray intersections a line.

    Source: https://stackoverflow.com/a/19550879

    :param p1: point A of line segment A
    :param p2: point B of line segment A
    :param p3: point A of line segment B
    :param p4: point B of line segment B

    :return: the point of intersection; None otherwise
    """

    s10_x = p2.x - p1.x
    s10_y = p2.y - p1.y
    s32_x = p4.x - p3.x
    s32_y = p4.y - p3.y

    denom = s10_x * s32_y - s32_x * s10_y

    if denom == 0: return None  # collinear

    denom_is_positive = denom > 0

    s02_x = p1.x - p3.x
    s02_y = p1.y - p3.y

    s_numer = s10_x * s02_y - s10_y * s02_x

    if (s_numer < 0) == denom_is_positive:
        return None  # no collision

    t_numer = s32_x * s02_y - s32_y * s02_x

    if (t_numer < 0) == denom_is_positive:
        return None  # no collision

    if (s_numer > denom) == denom_is_positive or (t_numer > denom) == denom_is_positive:
        return None  # no collision

    # collision detected
    t = t_numer / denom
    intersection_point = Coordinates(p1.x + (t * s10_x), p1.y + (t * s10_y))
    return intersection_point


def get_line_endpoint_within_box(p1: Coordinates, angle: float, nw: Coordinates, se: Coordinates,
                                 offset: float) -> Coordinates:
    """
    For the given box (given by NW and SE coordinates), find the endpoint for a given point and angle,
    'radius' distance away.

    :param p1: start point of the line
    :param angle: angle of line, north of x-axis, in degrees
    :param nw: upper-left border of the box
    :param se: lower-right border of the box
    :param offset: offset; usually radius of ball
    :return: end point of the line
    """

    # assert angle > 0, "provided angle is 0!"

    # Angle to degrees
    angle_rad = np.radians(angle)

    # North, East, South, West
    n, e, s, w = nw.y, se.x, se.y, nw.x

    # Quadrant angles of rectangle
    top_start = np.degrees(np.arctan((n - p1.y) / (e - p1.x))) if (e - p1.x) > 0 else np.radians(90)
    left_start = np.degrees(np.arctan((n - p1.y) / (p1.x - w))) if (p1.x - w) > 0 else np.radians(90)
    bottom_start = np.degrees(np.arctan((p1.y - s) / (p1.x - w))) if (p1.x - w) > 0 else np.radians(90)
    right_start = np.degrees(np.arctan((p1.y - s) / (e - p1.x))) if (e - p1.x) > 0 else np.radians(90)

    # Calculate length of the line, limited by the containing box
    if top_start < angle < 180 - left_start:
        # Top quadrant
        y = n - p1.y - offset
        x = y / np.tan(angle_rad)

        # assert x > 0.0, "x is 0!"
        # assert y > 0.0, "y is 0!"
    elif 180 - left_start <= angle < 180 + bottom_start:
        # Left quadrant
        x = p1.x - w - offset
        y = x * np.tan(angle_rad)

        # assert x > 0.0, "x is 0!"
        # assert y > 0.0, "y is 0!"
    elif 180 + bottom_start <= angle < 360 - right_start:
        # Bottom quadrant
        y = p1.y - s - offset
        x = y / np.tan(angle_rad)

        # assert x > 0.0, "x is 0!"
        # assert y > 0.0, "y is 0!"
    else:
        # Right quadrant
        x = e - p1.x - offset
        y = x * np.tan(angle_rad)

        # assert x > 0.0, "x is 0!"
        # assert y > 0.0, "y is 0!"

    if x == 0.0:
        x = p1.x
    if y == 0.0:
        y = p1.y

    line_length = np.sqrt(x ** 2 + y ** 2)

    # print("line_length = {}".format(line_length))


    result = Coordinates(p1.x + line_length * np.cos(angle_rad),
                       p1.y + line_length * np.sin(angle_rad))

    # print("get_line_endpoint_within_box(p1={}, angle={}, offset={} ...) returning {}".format(p1, angle, offset, result))

    return result


def get_parallel_line(p1: Coordinates, p2: Coordinates, dist: float, top: bool) -> (Coordinates, Coordinates):
    """
    Get the line parallel to a given line for a certain distance away.

    :param p1: point 1 of original line
    :param p2: point 2 of original line
    :param dist: distance between lines
    :param top: top or bottom parallel line
    :return: pair of points representing the new, parallel line
    """

    # Get perpendicular angle
    normal_angle = get_angle(p2, p1) + 90

    if top:
        p3 = Coordinates(
            p1.x + dist * np.cos(np.radians(normal_angle)),
            p1.y - dist * np.sin(np.radians(normal_angle))
        )
        p4 = Coordinates(
            p2.x + dist * np.cos(np.radians(normal_angle)),
            p2.y - dist * np.sin(np.radians(normal_angle))
        )

    else:
        p3 = Coordinates(
            p1.x - dist * np.cos(np.radians(normal_angle)),
            p1.y + dist * np.sin(np.radians(normal_angle))
        )
        p4 = Coordinates(
            p2.x - dist * np.cos(np.radians(normal_angle)),
            p2.y + dist * np.sin(np.radians(normal_angle))
        )

    return p3, p4


def get_point_on_line_distance_from_point(line_start, line_end, point, distance) -> Coordinates:
    print('get_point_on_line_distance_from_point called with: line_start={}, line_end={}, point={}, distance={}'.format(
        line_start, line_end, point, distance
    ))
    a_side = distance
    c_side = get_distance(line_start, point)

    v_point = Vector(point.x - line_start.x, point.y - line_start.y)
    v_line = Vector(line_end.x - line_start.x, line_end.y - line_start.y)
    dot = v_point.dot_product(v_line)

    a_angle = np.arccos(dot / v_point.get_magnitude() / v_line.get_magnitude())

    from pool.src.physics.trianglesolver import solve
    (a_side, b_side, c_side, a_angle, b_angle, c_angle) = solve(a=a_side, c=c_side, A=a_angle, ssa_flag='obtuse')
    assert a_angle + b_angle + c_angle == np.radians(180), 'a_angle: {} \nb_angle: {}\nc_angle: {}\n'.format(a_angle,
                                                                                                             b_angle,
                                                                                                             c_angle)
    # Compute exact point
    angle = np.radians(get_angle(line_end, line_start))
    x = line_start.x + b_side * np.cos(angle)
    y = line_start.y + b_side * np.sin(angle)

    return Coordinates(x, y)
