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
RGB_TARGETS = {"white": (245, 245, 245),
            #"green": (10, 160, 160),
            "purple": (50, 30, 50),
            "orange": (240, 210, 20),
            "black": (40, 20, 20)}

# what to show when debugging
DISPLAY_COLORS = {"white": (255, 255, 255),
                #"green": (0, 255, 0),
                "purple": (128, 0, 128),
                "orange": (255, 255, 0),
                "black": (0, 0, 0)}

# pockets, usually
ignore_regions = [((0, 0), (60, 40)), # top left
                  ((360, 0), (433, 30)), # top middle
                  ((750, 0), (800, 50)), # top right
                  ((0, 325), (50, 448)), # bottom left
                  ((360, 346), (426, 450)), # bottom middle
                  ((747, 345), (800, 450)) # bottom right
                ]
