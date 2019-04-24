"""ball_initializer initializes ball constants for each ball for use with hsv_filtering.
"""

from ball_info import BallInfo
import numpy as np

# HSV values for different color balls
# Range is H [0,180], S [0,255], V [0,255]
LOWER_YELLOW = np.array([25,75,200]) #1
UPPER_YELLOW = np.array([35,180,255])
YELLOW_MIN_CONTOUR = .75
YELLOW = (255,255,0)
LOWER_ORANGE = np.array([10,70,150]) #2
UPPER_ORANGE = np.array([24,180,255])
ORANGE_MIN_CONTOUR = .7
ORANGE = (255,140,0)
LOWER_BLUE = np.array([98,200,80]) #3
UPPER_BLUE = np.array([110,255,210])
BLUE_MIN_CONTOUR = 1.2
BLUE = (0,0,255)
LOWER_PURPLE = np.array([107,125,20]) #4
UPPER_PURPLE = np.array([130,190,140])
PURPLE_MIN_CONTOUR = .7
PURPLE = (138,43,226)
LOWER_RED = np.array([175,150,150]) #5, red sometimes overflows into 177-180
UPPER_RED = np.array([180,255,255])
RED_MIN_CONTOUR = .5
RED = (255,0,0)
LOWER_GREEN = np.array([89,204,0]) #6
UPPER_GREEN = np.array([92,230,255])
GREEN_MIN_CONTOUR = .6
GREEN = (0,128,0)
LOWER_BROWN = np.array([170,100,0]) #7, hard
UPPER_BROWN = np.array([179,180,180])
BROWN_MIN_CONTOUR = .38
BROWN = (165,42,42)
LOWER_WHITE = np.array([230,245,245]) #cue ball, using rgb as bounds
UPPER_WHITE = np.array([255,255,255])
WHITE_MIN_CONTOUR = .5
WHITE = (200,200,200)
BLACK = (0,0,0)
LOWER_BLACK = np.array([0,0,0])
UPPER_BLACK = np.array([70,70,70])
BLACK_MIN_CONTOUR = .7

"""init_all_balls initalizes and stores BallInfo objects with their respective constants.
Returns:
    ball_dict: ball string representation to its respective BallInfo object
"""
def init_all_balls():
  white_ball = BallInfo(LOWER_WHITE, UPPER_WHITE, WHITE, 'white', WHITE_MIN_CONTOUR)
  yellow_ball = BallInfo(LOWER_YELLOW, UPPER_YELLOW, YELLOW, 'yellow', YELLOW_MIN_CONTOUR)
  orange_ball = BallInfo(LOWER_ORANGE, UPPER_ORANGE, ORANGE, 'orange', ORANGE_MIN_CONTOUR)
  blue_ball = BallInfo(LOWER_BLUE, UPPER_BLUE, BLUE, 'blue', BLUE_MIN_CONTOUR)
  purple_ball = BallInfo(LOWER_PURPLE, UPPER_PURPLE, PURPLE, 'purple', PURPLE_MIN_CONTOUR)
  red_ball = BallInfo(LOWER_RED, UPPER_RED, RED, 'red', RED_MIN_CONTOUR)
  green_ball = BallInfo(LOWER_GREEN, UPPER_GREEN, GREEN, 'green', GREEN_MIN_CONTOUR)
  brown_ball = BallInfo(LOWER_BROWN, UPPER_BROWN, BROWN, 'brown', BROWN_MIN_CONTOUR)
  black_ball = BallInfo(LOWER_BLACK, UPPER_BLACK, BLACK, 'black', BLACK_MIN_CONTOUR)
  ball_dict = dict()
  ball_dict['white'] = white_ball
  ball_dict['yellow'] = yellow_ball
  ball_dict['orange'] = orange_ball
  ball_dict['blue'] = blue_ball
  ball_dict['purple'] = purple_ball
  ball_dict['red'] = red_ball
  ball_dict['green'] = green_ball
  ball_dict['brown'] = brown_ball
  ball_dict['black'] = black_ball
  return ball_dict

"""init_balls returns specified BallInfo objects.
Args:
    ball_list: String[] with string representations of ball colors the user wants returned
Retruns:
    balls: BallInfo[] of all the balls listed in ball_list
"""
def init_balls(ball_list):
  balls = []
  all_ball_info = init_all_balls()
  for ball_str in ball_list:
    if ball_str in all_ball_info:
      balls.append(all_ball_info[ball_str])
    else:
      print("Invalid ball string: " + ball_str)
  return balls
