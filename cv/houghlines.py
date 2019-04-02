import cv2
import numpy as np

# CONSTANTS
BORDER_WIDTH = 1.25

"""compute_lines computes lines of the pool table edges.

Args:
  img: input image
  display_hough_lines: boolean repr whether debug images will be displyaed

Returns:
  (min_x, min_y, max_x, max_y) tuple of (x,y) coordinates of NW and SE corner
  of the pool table edges
"""
def compute_lines(img, display_hough_lines):
  # Number of lines we want to detect, ideally 4 for the 4 pool edges,
  # however, some lines are duplicated so this parameter can increase
  num_lines = 4
  # Preprocess image
  gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
  kernel_size = 5
  blur_gray = cv2.GaussianBlur(gray,(kernel_size, kernel_size),0)

  low_threshold = 150
  high_threshold = 250
  edges = cv2.Canny(blur_gray, low_threshold, high_threshold)

  # Run OpenCV's houghlines
  rho = 1  # distance resolution in pixels of the Hough grid
  theta = np.pi / 180  # angular resolution in radians of the Hough grid
  threshold = 15  # minimum number of votes (intersections in Hough grid cell)
  min_line_length = 50  # minimum number of pixels making up a line
  max_line_gap = 20  # maximum gap in pixels between connectable line segments
  line_image = np.copy(img)  # creating a copy of the image to draw lines on

  # Run Hough on edge detected image
  # Output "lines" is an array containing endpoints of detected line segments
  lines = cv2.HoughLinesP(edges, rho, theta, threshold, np.array([]),
                      min_line_length, max_line_gap)

  if not lines.shape or lines.shape[0] < num_lines:
    return None
  # Initialize x/y's for min/max computations
  # TODO account for tilted angles
  min_x = None
  max_x = None
  min_y = None
  max_y = None
  for i in range(num_lines):
    line = lines[i]
  # for line in lines:
    for x1,y1,x2,y2 in line:
      

      if not min_x:
        min_x = x1
        max_x = x2
        min_y = y1
        max_y = y2

      min_x = min(min_x, min(x1,x2))
      max_x = max(max_x, max(x1,x2))
      min_y = min(min_y, min(y1,y2))
      max_y = max(max_y, max(y1,y2))

  if display_hough_lines:
    cv2.line(line_image,(min_x,min_y),(max_x,min_y),(0,0,255),2)
    cv2.line(line_image,(min_x,min_y),(min_x,max_y),(0,0,255),2)
    cv2.line(line_image,(min_x,max_y),(max_x,max_y),(0,0,255),2)
    cv2.line(line_image,(max_x,min_y),(max_x,max_y),(0,0,255),2)
    cv2.imshow('edges',edges)
    cv2.imshow('houghlines.jpg',line_image)
  print("NW: (" + str(min_x) + "," + str(min_y) + ") SE: (" + str(max_x) + "," + str(max_y) + ")")
  return min_x+BORDER_WIDTH, min_y+BORDER_WIDTH, max_x-BORDER_WIDTH, max_y-BORDER_WIDTH


def resize_img(img):
  RESIZE_IMG_WIDTH = 800
  img_height = img.shape[0]
  img_width = img.shape[1]
  resize_img_height = int(img_height / img_width * RESIZE_IMG_WIDTH)
  img = cv2.resize(img, (RESIZE_IMG_WIDTH, resize_img_height))
  return img

# """ If running individually
def run():
  img = cv2.imread('cv/img/8.jpg')
  img = resize_img(img)

  display_hough_lines = True

  res = compute_lines(img, display_hough_lines)
  if not res:
    print("None :(")
    return
  x1, y1, x2, y2 = res
  print("Returns (" + str(x1) + ", " + str(y1) + ")  " + "(" + str(x2) + ", " + str(y2) + ")")
  while(1):
    ESC_KEY = 27
    k = cv2.waitKey(5) & 0xFF
    if k == ESC_KEY:
        running = False
        break

# run()
# """
