# import the necessary packages
import numpy as np
import argparse
import cv2

DP = 1.2
MIN_DIST = 100
USING_CAMERA = True
 
def run_hough_circles(image):
  output = image.copy()
  gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
  # kernel_size = 5
  # blur_gray = cv2.GaussianBlur(gray,(kernel_size, kernel_size),0)

  # low_threshold = 400
  # high_threshold = 400
  # edges = cv2.Canny(blur_gray, low_threshold, high_threshold)

  # detect circles in the image
  circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, DP, MIN_DIST, param1=50, param2=30, minRadius=10, maxRadius=25)
   
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
      cv2.circle(output, (x, y), r, (0, 255, 0), 4)
      cv2.rectangle(output, (x - 5, y - 5), (x + 5, y + 5), (0, 128, 255), -1)
   
    # show the output image
    cv2.imshow("output", output)
    cv2.waitKey(0)
  else:
    print("No circles :(")

def main():
  if USING_CAMERA:
        cap = cv2.VideoCapture(0)
  
  while True:

  # # construct the argument parser and parse the arguments
  # ap = argparse.ArgumentParser()
  # ap.add_argument("-i", "--image", required = True, help = "Path to the image")
  # args = vars(ap.parse_args())

  # # load the image, clone it for output, and then convert it to grayscale
  # image = cv2.imread(args["image"])

if __name__ == "__main__":
    main()