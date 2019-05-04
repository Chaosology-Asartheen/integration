import ball_initializer
import constants
import cv2
import hough_lines
import numpy as np
import imutils
import time
from cv_ball import CVBall
from datetime import datetime

from modules.average_queue import AverageQueue

cue_lower = np.array([180,240,240]) #cue ball, using rgb as bounds
cue_upper = np.array([255,255,255])

# Commandline arguments
DISPLAY = False
DISPLAY_INTERMEDIATE = False
DISPLAY_HOUGH = False
USING_CAMERA = True

aggres = {}

def wait_escape():
    while(1):
        k = cv2.waitKey(5) & 0xFF
        if k == constants.ESC_KEY:
            break

def init_ball_info(ball_list):
    ball_info = ball_initializer.init_balls(ball_list)
    return ball_info

def norm_coordinates(x, y, min_x, max_x, min_y, max_y):
    norm_x = (x - min_x) / (max_x - min_x)
    norm_y = (y - min_y) / (max_y - min_y)
    return (norm_x, norm_y)

def find_ball(ball, hsv, frame, cv_balls):
    table_pixel_length = frame.shape[1]
    table_pixel_width = frame.shape[0]

    # Threshold the HSV image to get only ball colors
    # print("Looking at " + ball.str_rep)
    # White and Black balls use RGB filtering instead of HSV filtering
    if ball.str_rep == "white" or ball.str_rep == "black":
        mask = cv2.inRange(frame, ball.lower_bound, ball.upper_bound)
    else:
        mask = cv2.inRange(hsv, ball.lower_bound, ball.upper_bound)

    # Expand mask through 1 iter of dilation
    mask = cv2.dilate(mask, None, iterations=1)

    # Bitwise-AND mask and original image
    res = cv2.bitwise_and(frame,frame, mask=mask)

    if DISPLAY_INTERMEDIATE:
        cv2.imshow('mask',mask)
        cv2.imshow('res',res)
        wait_escape()

    # find contours in the mask
    cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE)
    contours = imutils.grab_contours(cnts)
    center = None

    min_contour_area = table_pixel_width * ball.min_contour
    max_contour_area = 1000
    # if (ball.str_rep == "white"):
    #     max_contour_area = table_pixel_width * 3
    # if (ball.str_rep == "blue"):
    #     max_contour_area = table_pixel_width * 5
    min_yellow_contour_area = table_pixel_width * .4

    # only proceed if at least one contour was found
    for c in contours:
        # Find min enclosing circle around the contour
        ((x, y), radius) = cv2.minEnclosingCircle(c)
        # Compute normalized coordinates [0,1] for ball position
        (norm_x, norm_y) = norm_coordinates(x, y, 0, table_pixel_length, 0, table_pixel_width)
        # Compute table/irl coordinates for ball position
        (table_x, table_y) = norm_x * constants.TABLE_LENGTH, norm_y * constants.TABLE_WIDTH

        # Check that table coordinates are within right bounds (ball is indeed on the table)
        if (constants.BALL_RADIUS < table_x < constants.TABLE_LENGTH-constants.BALL_RADIUS and
            constants.BALL_RADIUS < table_y < constants.TABLE_WIDTH-constants.BALL_RADIUS):

            if (100 < cv2.contourArea(c) < 1000):
                print("cA={}, min={} max={}, radius={}".format(cv2.contourArea(c), min_contour_area, max_contour_area, radius))

            # Ensure that contour area is correct for a ball
            if (min_contour_area < cv2.contourArea(c) < max_contour_area):

                if (ball.str_rep != "white" and radius < constants.MAX_RADIUS or (2*constants.BALL_RADIUS < table_x < constants.TABLE_LENGTH-2*constants.BALL_RADIUS and
                    2*constants.BALL_RADIUS < table_y < constants.TABLE_WIDTH-2*constants.BALL_RADIUS)):

                    # if not (ball.str_rep in aggres):
                    #     aggres[ball.str_rep] = AverageQueue(limit=10)
                    # aggres[ball.str_rep].add(norm_x, norm_y)
                    # ave_x, ave_y = aggres[ball.str_rep].get_average()
                    # cv_balls.append(CVBall(ave_x, ave_y, ball.str_rep)) # Avg queue
                    cv_balls.append(CVBall(norm_x, norm_y, ball.str_rep)) # W/out avg queue
                    if DISPLAY:
                        # draw the circle and midpoint on the frame
                        cv2.circle(frame, (int(x), int(y)), int(radius), ball.bgr, 2)
                        cv2.circle(frame, (int(x), int(y)), 2, (0, 255, 0), -1)
            # Edge case for 9, yellow stripe ball
            elif (ball.str_rep == "yellow" and min_yellow_contour_area < cv2.contourArea(c) < min_contour_area):
                raise Exception("DONT GO HERE")
                # print("yellow stripe")
                #
                # cv_balls.append(CVBall(norm_x, norm_y, "nine"))
                # if DISPLAY:
                #     # draw the circle and midpoint on the frame
                #     cv2.circle(frame, (int(x), int(y)), int(radius), (0,153,153), 2)
                #     cv2.circle(frame, (int(x), int(y)), 2, (0, 255, 0), -1)

def find_balls(balls, hsv_img, frame):
    cv_balls = []
    for ball in balls:
        find_ball(ball, hsv_img, frame, cv_balls)
    return cv_balls

def find_cuestick(hsv, frame):
    table_pixel_length = frame.shape[1]
    table_pixel_width = frame.shape[0]
    mask = cv2.inRange(frame, cue_lower, cue_upper)
    # mask = cv2.inRange(frame, LOWER_WHITE, UPPER_WHITE)
    # Bitwise-AND mask and original image
    res = cv2.bitwise_and(frame,frame, mask=mask)

    if DISPLAY_INTERMEDIATE:
        cv2.imshow('mask',mask)
        cv2.imshow('res',res)

    # find contours in the mask
    cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    for cnt in cnts:
        min_cuestick_area = table_pixel_width * 3
        max_cuestick_area = table_pixel_width * 5
        # if (cv2.contourArea(cnt) > table_pixel_width * 2):
        #     print("under: " + str(cv2.contourArea(cnt)))
        if (min_cuestick_area < cv2.contourArea(cnt) < max_cuestick_area):
            print(cv2.contourArea(cnt))
            rows,cols = hsv.shape[:2]
            [vx,vy,x,y] = cv2.fitLine(cnt, cv2.DIST_L2,0,0.01,0.01)
            left_y = int((-x*vy/vx) + y)
            right_y = int(((cols-x)*vy/vx)+y)

            mid_point = (int(x), int(y))
            left_point = (int(0),int(left_y))
            right_point = (int(cols-1),int(right_y))
            if DISPLAY:
                cv2.line(frame,(cols-1,right_y),(0,left_y),(255,255,255),2)
                cv2.circle(frame, mid_point, 2, (0,0,255), 2)
                cv2.circle(frame, left_point, 2, (0,0,255), 2)
                cv2.circle(frame, right_point, 2, (0,0,255), 2)

            norm_mid_point = norm_coordinates(mid_point[0], mid_point[1], 0, table_pixel_length, 0, table_pixel_width)
            norm_left_point = norm_coordinates(left_point[0], left_point[1], 0, table_pixel_length, 0, table_pixel_width)
            norm_right_point = norm_coordinates(right_point[0], right_point[1], 0, table_pixel_length, 0, table_pixel_width)
            return [norm_mid_point, norm_left_point, norm_right_point]

def get_resized_frame(frame):
    frame_height = frame.shape[0]
    frame_width = frame.shape[1]
    resize_frame_height = int(frame_height / frame_width * constants.RESIZE_FRAME_WIDTH)
    frame = cv2.resize(frame, (constants.RESIZE_FRAME_WIDTH, resize_frame_height))
    return frame

def run_hsv_filtering(frame):
    ball_list = ["orange"]
    # "white","orange","purple","black"
    #
    balls = init_ball_info(ball_list)
    hsv_img = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    cv_balls = find_balls(balls, hsv_img, frame)
    return cv_balls

def main():
    # show_edges()
    ball_list = ["white","orange","purple","black"]
    # "white","orange","purple","black"
    #
    balls = init_ball_info(ball_list)

    if USING_CAMERA:
        cap = cv2.VideoCapture(1)
        # cap.set(cv2.CV_CAP_PROP_BRIGHTNESS, 50)

    count = 0
    times = []
    running = True
    while running:
        frame = None

        # Take each frame
        if USING_CAMERA:
            ret, frame = cap.read()
        else:
            filename = "/Users/ouchristinah/Google Drive/CMU/S19/capstone/integration/test_imgs/2.jpg"
            # filename = "/Users/skim/ws/500/cv/pool.jpg"
            frame = cv2.imread(filename)

        if frame is None:
            print("no frame")
            continue
        frame = get_resized_frame(frame)
        frame = cv2.flip(frame, 0) # Flips horizontally (hot dog)
        frame = cv2.flip(frame, 1) # Flips vertically (hamburger)
        frame_y1, frame_y2 = 53, 426
        frame_x1, frame_x2 = 13, 800
        frame = frame[int(frame_y1):int(frame_y2),int(frame_x1):int(frame_x2)]

        if DISPLAY_INTERMEDIATE:
            print('disp')
            cv2.imshow('frame', frame)
            wait_escape()

        # table_coords = hough_lines.compute_lines(frame, DISPLAY_HOUGH)
        # table_coords = 76,24,642,282

        # table_coords = 188,107,1148,554
        # if not table_coords:
        #     continue
        # x1,y1,x2,y2 = table_coords
        # frame = frame[int(y1):int(y2),int(x1):int(x2)]

        # Convert BGR to HSV
        hsv_img = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        cv_balls = find_balls(balls, hsv_img, frame)

        print("*******************************")
        print(cv_balls)
        # print("cuestick " + str(find_cuestick(hsv_img, frame)))

        # Pass parameters to pool

        if DISPLAY:
          cv2.imshow('frame', frame)
          wait_escape()

    # When everything done, release the capture
    if USING_CAMERA:
        cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    DISPLAY = True
    main()
