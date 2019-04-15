# import the necessary packages
import numpy as np
import argparse
import cv2
from datetime import datetime

DP = 1.1
MIN_DIST = 20
USING_CAMERA = True
RESIZE_FRAME_WIDTH = 800
HIGH_THRESHOLD = 50
LOW_THRESHOLD = 25
MIN_RADIUS = 7
MAX_RADIUS = 20
 
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
      print(r)
      # draw the circle in the output image, then draw a rectangle
      # corresponding to the center of the circle
      # cv2.circle(output, (x, y), r, (0, 255, 0), 4)
      cv2.rectangle(output, (x - 2, y - 2), (x + 2, y + 2), (0, 128, 255), -1)
   
    # show the output image
    cv2.imshow("output", output)
    cv2.waitKey(0)
  else:
    print("No circles :(")

def main():
  if USING_CAMERA:
    cap = cv2.VideoCapture(1)
  
  while True:
    if USING_CAMERA:
      ret, frame = cap.read()
    else:
      frame = cv2.imread("/Users/ouchristinah/Google Drive/CMU/S19/capstone/integration/test_imgs/2.jpg")
    frame_height = frame.shape[0]
    frame_width = frame.shape[1]
    resize_frame_height = int(frame_height / frame_width * RESIZE_FRAME_WIDTH)
    frame = cv2.resize(frame, (RESIZE_FRAME_WIDTH, resize_frame_height))
    run_hough_circles(frame)


if __name__ == "__main__":
    main()