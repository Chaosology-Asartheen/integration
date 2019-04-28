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
            "purple": (30, 0, 90),
            "orange": (240, 240, 0),
            "black": (50, 20, 20)}

# what to show when debugging
DISPLAY_COLORS = {"white": (255, 255, 255),
                #"green": (0, 255, 0),
                "purple": (128, 0, 128),
                "orange": (255, 255, 0),
                "black": (0, 0, 0)}

# pockets, usually
ignore_regions = [((0, 0), (50, 35)), # top left
                  ((400, 0), (460, 30)), # top middle
                  ((778, 0), (800, 50)), # top right
                  ((0, 335), (67, 448)), # bottom left
                  ((395, 346), (455, 450)), # bottom middle
                  ((752, 324), (800, 450)) # bottom right
                ]
