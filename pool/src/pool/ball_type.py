from enum import Enum

from pool.src.pool import colors


class BallType(Enum):
    CUE = ('0', colors.DARK_WHITE)
    ONE = ('1', colors.YELLOW)
    TWO = ('2', colors.DARK_BLUE)
    THREE = ('3', colors.RED)
    FOUR = ('4', colors.DARK_PURPLE)
    FIVE = ('5', colors.ORANGE)
    SIX = ('6', colors.DARK_GREEN)
    SEVEN = ('7', colors.MAROON)
    EIGHT = ('8', colors.BLACK)
    NINE = ('9', colors.SILVER)
    # TODO: Colors for striped balls
    TEN = ('10', colors.WHITE)
    ELEVEN = ('11', colors.WHITE)
    TWELVE = ('12', colors.WHITE)
    THIRTEEN = ('13', colors.WHITE)
    FOURTEEN = ('14', colors.WHITE)
    FIFTEEN = ('15', colors.WHITE)

    def __init__(self, val, color):
        self.val = val
        self.color = color

    def __str__(self):
        return self.name
