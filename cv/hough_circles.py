# import the necessary packages
import numpy as np
import argparse
import cv2
import sys
from datetime import datetime

# sys.path.append('/Users/ouchristinah/Google Drive/CMU/S19/capstone/integration')
# sys.path.append('/Users/ouchristinah/Google Drive/CMU/S19/capstone/integration/cv')
#
# from cv.average_queue import AverageQueue

DP = 1.1
MIN_DIST = 20
USING_CAMERA = True
RESIZE_FRAME_WIDTH = 800
HIGH_THRESHOLD = 50
LOW_THRESHOLD = 25
MIN_RADIUS = 7
MAX_RADIUS = 20

WHITE = (255,255,255)
BLACK = ()
COLORS = [(WHITE,"white")]

def color_almost_equals(expected, actual, epsilon):
  return (abs(expected[0] - actual[0] <= epsilon) and
          abs(expected[1] - actual[1] <= epsilon) and
          abs(expected[2] - actual[2] <= epsilon))

def determine_color(image, xy):
  STEP = 3
  COLOR_EPSILON = 15
  VOTE_THRESHOLD = 4
  x, y = int(xy[0]), int(xy[1])
  for expected_color,color_str in COLORS:
    vote = 0
    for row in range(y-STEP,y+STEP,STEP):
      for col in range(x-STEP,x+STEP,STEP):
        actual_color = image[row][col]
        if color_almost_equals(expected_color, actual_color, COLOR_EPSILON):
          vote += 1
    if vote >= VOTE_THRESHOLD:
      return (expected_color,color_str)
  return ((0,0,0),"black")

def run_hough_circles(image):
  output = image.copy()
  gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

  # detect circles in the image
  circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, DP, MIN_DIST, param1=HIGH_THRESHOLD,
    param2=LOW_THRESHOLD, minRadius=MIN_RADIUS, maxRadius=MAX_RADIUS)

  # ensure at least some circles were found
  if circles is not None:
    print("Found circles")
    # convert the (x, y) coordinates and radius of the circles to integers
    circles = np.round(circles[0, :]).astype("int")

    # loop over the (x, y) coordinates and radius of the circles
    for (x, y, r) in circles:
      # TODO: filter out x/y's that lie outside table edges or on pockets. Requires getting table coords
      color_val,color_str = determine_color(image, (x,y))
      print(color_str)
      # draw the circle in the output image, then draw a rectangle
      # corresponding to the center of the circle
      # cv2.circle(output, (x, y), r, (0, 255, 0), 4)
      cv2.rectangle(output, (x - 2, y - 2), (x + 2, y + 2), (20,255,57), -1)
      cv2.rectangle(output, (x - 1, y - 1), (x + 1, y + 1), color_val, -1)

    # show the output image
    cv2.imshow("output", output)
    cv2.waitKey(0)
  else:
    print("No circles :(")

def main():
  if USING_CAMERA:
    cap = cv2.VideoCapture(0)

  while True:
    if USING_CAMERA:
      ret, frame = cap.read()
    else:
      frame = cv2.imread("/Users/ouchristinah/Google Drive/CMU/S19/capstone/integration/test_imgs/2.jpg")
    frame_height = frame.shape[0]
    frame_width = frame.shape[1]
    resize_frame_height = int(frame_height / frame_width * RESIZE_FRAME_WIDTH)
    frame = cv2.resize(frame, (RESIZE_FRAME_WIDTH, resize_frame_height))
    cv_balls = run_hough_circles(frame)


if __name__ == "__main__":
    main()
