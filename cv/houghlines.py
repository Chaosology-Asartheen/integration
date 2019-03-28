import cv2
import numpy as np

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
  num_lines = 5
  # Preprocess image
  gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
  lower_threshold = 70
  upper_threshold = 255
  ret, threshold_img = cv2.threshold(gray,lower_threshold,upper_threshold,
    cv2.THRESH_BINARY)

  # Perform canny edge detection
  edges = cv2.Canny(threshold_img,50,150,apertureSize = 3)

  # Run OpenCV's houghlines
  lines = cv2.HoughLines(edges,1,np.pi/180,100)
  print(lines)
  if lines.shape[0] < num_lines:
    return None
  # Initialize x/y's for min/max computations
  min_x = 2000
  max_x = -2000
  min_y = 2000
  max_y = -2000
  for i in range(num_lines):
    line = lines[i]
    for rho,theta in line:
        a = np.cos(theta)
        b = np.sin(theta)
        x0 = a*rho
        y0 = b*rho
        x1 = int(x0 + 1000*(-b))
        y1 = int(y0 + 1000*(a))
        x2 = int(x0 - 1000*(-b))
        y2 = int(y0 - 1000*(a))
        if x1 < -900 or x2 < -900:
          min_y = min(min_y, min(y1, y2))
        if x1 > 900 or x2 > 900:
          max_y = max(max_y, max(y1, y2))
        if y1 < -900 or y2 < -900:
          min_x = min(min_x, min(x1, x2))
        if y1 > 900 or y2 > 900:
          max_x = max(max_x, max(x1, x2))
        if display_hough_lines:
          cv2.line(img,(x1,y1),(x2,y2),(0,0,255),2)

  if display_hough_lines:
    cv2.imshow('threshold',threshold_img)
    cv2.imshow('edges',edges)
    cv2.imshow('houghlines.jpg',img)
    while(1):
        k = cv2.waitKey(5) & 0xFF
        if k == 27:
          break
  print("NW: (" + str(min_x) + "," + str(min_y) + ") SE: (" + str(max_x) + "," + str(max_y) + ")")
  return min_x, min_y, max_x, max_y


def resize_img(img):
  RESIZE_IMG_WIDTH = 800
  img_height = img.shape[0]
  img_width = img.shape[1]
  resize_img_height = int(img_height / img_width * RESIZE_IMG_WIDTH)
  img = cv2.resize(img, (RESIZE_IMG_WIDTH, resize_img_height))
  return img

# """ If running individually
def run():
  img = cv2.imread('1.jpg')
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

run()
# """
