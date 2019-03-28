import sys

import numpy as np

sys.path.append('/Users/skim/ws/500')
sys.path.append('/Users/skim/ws/500/cv')
sys.path.append('/Users/skim/ws/500/pool')

from pool.src.physics.coordinates import Coordinates
from pool.src.physics.direction import Direction


class Vector:
    """
    2-D vector with x and y components.
    """

    def __init__(self, x: float, y: float):
        self.x = float(x)
        self.y = float(y)

    @staticmethod
    def get_normal_vector(direction: Direction):
        """
        Returns the normal vector pointing towards the given direction.

        :param direction: Compass direction of the normal vector.
        :return: Normal vector
        """
        if direction == Direction.NORTH:
            return Vector(0, 1)
        elif direction == Direction.EAST:
            return Vector(1, 0)
        elif direction == Direction.SOUTH:
            return Vector(0, -1)
        else:  # Direction.WEST
            return Vector(-1, 0)

    def unit(self):
        """
        Get this vector's unit vector.
        TODO TEST THIS
        """
        return Vector(self.x / self.get_magnitude(), self.y / self.get_magnitude())

    def get_magnitude(self):
        """
        Get the magnitude for this vector.
        """

        return np.sqrt(self.x**2 + self.y**2)
        # return get_distance(Coordinates(self.x, self.y))

    def get_angle(self):
        """
        Get the angle for this vector.
        """

        x, y = self.x, self.y

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

    def dot_product(self, other):
        """
        Dot product dot product of this vector * other vector.
        :return: scalar dot product
        """
        return self.x * other.x + self.y * other.y

    def __add__(self, other):
        """
        Add another vector to this vector.

        :param other:
        :return: new vector representing sum
        """

        return Vector(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        """
        Subtract another vector from this vector.

        :param other:
        :return: new vector representing difference
        """

        return Vector(self.x - other.x, self.y - other.y)

    def __mul__(self, other: 'Vector' or float or int):
        """
        Multiply this vector by another vector OR a scalar.

        :param other: either another vector OR a scalar
        :return: dot product OR scaled vector
        """

        if type(other) == type(self):
            return self.dot_product(other)
        elif type(other) == int or type(other) == float:
            return Vector(self.x * other, self.y * other)

    def __rmul__(self, scalar: float):
        """
        Multiply this vector by a scalar.

        :param scalar: value to scale vector by
        :return: new, scaled vector
        """

        return Vector(self.x * scalar, self.y * scalar)

    def __str__(self):
        return "Vector ({}, {})".format(self.x, self.y)

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __ne__(self, other):
        return not self.__eq__(other)
