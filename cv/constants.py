BALL_RADIUS = .6
TABLE_LENGTH = 37.5
TABLE_WIDTH = 17.5625
ESC_KEY = 27
# MIN_RADIUS = .035
# MAX_RADIUS = .065

DP = 1.1
MIN_DIST = 20
RESIZE_FRAME_WIDTH = 800
HIGH_THRESHOLD = 50
LOW_THRESHOLD = 25
MIN_RADIUS = 7
MAX_RADIUS = 20

RGB_EPSILON = 30

# target values, will hit within EPSILON
RGB_TARGETS = {"white": (255, 255, 255),
            "green": (15, 160, 160),
            "purple": (40, 60, 140)}

# what to show when debugging
DISPLAY_COLORS = {"white": (255, 255, 255),
                "green": (0, 255, 0),
                "purple": (128, 0, 128)}

# pockets, usually
ignore_regions = [((0, 0), (151, 108)), # top left
                ((431, 0), (457, 104)), # top middle
                ((736, 0), (900, 120)), # top right
                ((0, 351), (154, 600)), # bottom left
                ((428, 368), (456, 600)), # bottom middle
                ((727, 361), (900, 600)) # bottom right
                ]
