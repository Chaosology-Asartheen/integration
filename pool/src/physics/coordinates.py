class Coordinates():
    """
    Cartesian coordinates.
    """

    def __init__(self, x: float, y: float):
        self.x = float(x)
        self.y = float(y)

    def __add__(self, other):
        return Coordinates(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Coordinates(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar: float):
        """
        Multiply this vector by a scalar.

        :param scalar: value to scale vector by
        :return: new, scaled vector
        """

        return Coordinates(self.x*scalar, self.y*scalar)

    def __rmul__(self, scalar: float):
        """
        Multiply this vector by a scalar.

        :param scalar: value to scale vector by
        :return: new, scaled vector
        """

        return Coordinates(self.x*scalar, self.y*scalar)

    def __str__(self):
        return "Coordinates ({}, {})".format(self.x, self.y)

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __ne__(self, other):
        return not self.__eq__(other)
