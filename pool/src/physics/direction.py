from enum import Enum


class Direction(Enum):
    """
    Cardinal compass directions
    """

    NORTH = 'NORTH'
    EAST = 'EAST'
    SOUTH = 'SOUTH'
    WEST = 'WEST'
    NORTHWEST = 'NORTHWEST'
    NORTHEAST = 'NORTHEAST'
    SOUTHEAST= 'SOUTHEAST'
    SOUTHWEST = 'SOUTHWEST'

    def __str__(self):
        return self.value

    def opposite(self):
        if self == self.NORTH:
            return self.SOUTH
        elif self == self.EAST:
            return self.WEST
        elif self == self.SOUTH:
            return self.NORTH
        elif self ==  self.WEST:
            return self.EAST
        elif self == self.NORTHWEST:
            return self.SOUTHEAST
        elif self == self.NORTHEAST:
            return self.SOUTHWEST
        elif self == self.SOUTHEAST:
            return self.NORTHWEST
        elif self == self.SOUTHWEST:
            return self.NORTHEAST
        else:
            return None
