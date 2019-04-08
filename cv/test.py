import cv2
import numpy as np
import imutils
from datetime import datetime
from houghlines import compute_lines

# HSV values for different color balls
# Range is 180,255,255
lower_yellow = np.array([25,75,200]) #1
upper_yellow = np.array([35,180,255])
yellow_min_contour = .75
yellow = (255,255,0)
lower_orange = np.array([10,70,150]) #2
upper_orange = np.array([24,180,255])
orange_min_contour = .7
orange = (255,140,0)
lower_blue = np.array([98,200,80]) #3
upper_blue = np.array([110,255,210])
blue_min_contour = 1.2
blue = (0,0,255)
lower_purple = np.array([107,125,20]) #4
upper_purple = np.array([130,190,140])
purple_min_contour = .7
purple = (138,43,226)
lower_red = np.array([177,0,80]) #5
upper_red = np.array([180,255,255])
red_min_contour = .5
red = (255,0,0)
lower_green = np.array([89,204,0]) #6
upper_green = np.array([92,230,255])
green_min_contour = .6
green = (0,128,0)
lower_brown = np.array([170,100,0]) #7, hard
upper_brown = np.array([179,180,180])
brown_min_contour = .38
brown = (165,42,42)
lower_white = np.array([230,245,245]) #cue ball, using rgb as bounds
upper_white = np.array([255,255,255])
white_min_contour = .5
white = (200,200,200)
black = (0,0,0)
lower_black = np.array([0,0,0])
upper_black = np.array([70,70,70])
black_min_contour = .7
# upper_black = np.array([180,255,35])

# cue_lower = np.array([14,10,200])
# cue_upper = np.array([18,128,255])
cue_lower = np.array([180,240,240]) #cue ball, using rgb as bounds
cue_upper = np.array([255,255,255])

BALL_RADIUS = .6
TABLE_LENGTH = 37.5
TABLE_WIDTH = 17.5625
ESC_KEY = 27
DISPLAY = False
DISPLAY_INTERMEDIATE = False
DISPLAY_HOUGH = True
MAX_CUE_AREA = 1000
USING_CAMERA = True
MIN_RADIUS = .035
# MAX_RADIUS = .05
MAX_RADIUS = .065
RESIZE_FRAME_WIDTH = 1400
ESC_KEY = 27

# Class to store information on each ball
class BallInfo:
    def __init__(self, lower_bound, upper_bound, rgb, str_rep, min_contour):
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound
        self.bgr = (rgb[2], rgb[1], rgb[0])
        self.str_rep = str_rep
        self.min_contour = min_contour

class CVBall:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color

    def __repr__(self):
        return "%s: (%f, %f)" % (self.color, self.x, self.y)

def wait_escape():
    while(1):
        k = cv2.waitKey(5) & 0xFF
        if k == ESC_KEY:
            break

def init_ballinfo():
    balls = []
    white_ball = BallInfo(lower_white, upper_white, white, 'white', white_min_contour)
    balls.append(white_ball)
    # yellow_ball = BallInfo(lower_yellow, upper_yellow, yellow, 'yellow', yellow_min_contour)
    # balls.append(yellow_ball) # issues w 9 ball
    # orange_ball = BallInfo(lower_orange, upper_orange, orange, 'orange', orange_min_contour)
    # balls.append(orange_ball # issues
    blue_ball = BallInfo(lower_blue, upper_blue, blue, 'blue', blue_min_contour)
    balls.append(blue_ball)
    purple_ball = BallInfo(lower_purple, upper_purple, purple, 'purple', purple_min_contour)
    balls.append(purple_ball)
    # red_ball = BallInfo(lower_red, upper_red, red, 'red', red_min_contour)
    # balls.append(red_ball) # looks at brown
    green_ball = BallInfo(lower_green, upper_green, green, 'green', green_min_contour)
    balls.append(green_ball)
    brown_ball = BallInfo(lower_brown, upper_brown, brown, 'brown', brown_min_contour)
    balls.append(brown_ball)
    # black_ball = BallInfo(lower_black, upper_black, black, 'black', black_min_contour)
    # balls.append(black_ball) # issues
    return balls

def norm_coordinates(x, y, min_x, max_x, min_y, max_y):
    norm_x = (x - min_x) / (max_x - min_x)
    norm_y = (y - min_y) / (max_y - min_y)
    return (norm_x, norm_y)

def find_ball(ball, hsv, frame, cv_balls):
    table_pixel_length = frame.shape[1]
    table_pixel_width = frame.shape[0]

    # Threshold the HSV image to get only ball colors
    print("Looking at " + ball.str_rep)
    if ball.str_rep == "white" or ball.str_rep == "black":
        mask = cv2.inRange(frame, ball.lower_bound, ball.upper_bound)
    else:
        mask = cv2.inRange(hsv, ball.lower_bound, ball.upper_bound)
    # mask = cv2.erode(mask, None, iterations=1)
    mask = cv2.dilate(mask, None, iterations=1)
    
    # Bitwise-AND mask and original image
    res = cv2.bitwise_and(frame,frame, mask=mask)

    if DISPLAY_INTERMEDIATE:
        cv2.imshow('mask',mask)
        cv2.imshow('res',res)
        wait_escape()

    # find contours in the mask and initialize the current
    # (x, y) center of the ball
    circles = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE)
    circles = imutils.grab_contours(circles)
    center = None

    # print("table_pixel_width " + str(table_pixel_width))
    # min_contour_area = table_pixel_width * 1.15
    min_contour_area = table_pixel_width * ball.min_contour
    max_contour_area = table_pixel_width * 2.7
    if (ball.str_rep == "white"):
        max_contour_area = table_pixel_width * 3
    if (ball.str_rep == "blue"):
        max_contour_area = table_pixel_width * 5
    min_yellow_contour_area = table_pixel_width * .4
    # print("min: " + str(min_contour_area))
    # print("max: " + str(max_contour_area))
 
    # only proceed if at least one contour was found
    if len(circles) > 0:
        # find the largest contour in the mask, then use
        # it to compute the minimum enclosing circle and
        # centroid

        for c in circles:
            ((x, y), radius) = cv2.minEnclosingCircle(c)
            # print("min: " + str(MIN_RADIUS * table_pixel_width) + " max: " + str(MAX_RADIUS * table_pixel_width) + " actual: " + str(radius))
            # only proceed if the radius meets a minimum size
            # if (radius > MIN_RADIUS * table_pixel_width and 
            #     radius < MAX_RADIUS * table_pixel_width):
            (norm_x, norm_y) = norm_coordinates(x, y, 0, table_pixel_length, 0, table_pixel_width)
            table_x = norm_x * TABLE_LENGTH
            table_y = norm_y * TABLE_WIDTH
            
            
            if (BALL_RADIUS < table_x < TABLE_LENGTH-BALL_RADIUS and
                BALL_RADIUS < table_y < TABLE_WIDTH-BALL_RADIUS):
                # print("contour area: " + str(cv2.contourArea(c)) + " min: " + str(min_contour_area) + " max: " + str(max_contour_area))
                if (min_contour_area < cv2.contourArea(c) < max_contour_area):  
                    # print("tpw %d tpl %d" % (table_pixel_width, table_pixel_length))
                    # print("x: %f y: %f" % (x,y))
                    # print("norm_x: %f norm_y: %f" % (norm_x, norm_y))
                    
                    print("table_x: %f table_y: %f" % (table_x, table_y))
                    # print("mintx: %f minty: %f" % (2.5*BALL_RADIUS, TABLE_LENGTH-2.5*BALL_RADIUS))
                    if (ball.str_rep != "white" or (2*BALL_RADIUS < table_x < TABLE_LENGTH-2*BALL_RADIUS and
                        2*BALL_RADIUS < table_y < TABLE_WIDTH-2*BALL_RADIUS)):
                        # print("within contour_area")  
                        
                        cv_balls.append(CVBall(norm_x, norm_y, ball.str_rep))
                        print(cv2.contourArea(c))  
                        if DISPLAY:
                            # draw the circle and centroid on the frame,
                            # then update the list of tracked points
                            cv2.circle(frame, (int(x), int(y)), int(radius), ball.bgr, 2)
                            # Seems like using x,y from contour area is better
                            cv2.circle(frame, (int(x), int(y)), 2, (0, 255, 0), -1)
                elif (ball.str_rep == "yellow" and min_yellow_contour_area < cv2.contourArea(c) < min_contour_area):
                    print("yellow stripe")
                    
                    cv_balls.append(CVBall(norm_x, norm_y, "nine"))
                    if DISPLAY:
                        # draw the circle and centroid on the frame,
                        # then update the list of tracked points
                        cv2.circle(frame, (int(x), int(y)), int(radius), (0,153,153), 2)
                        # Seems like using x,y from contour area is better
                        cv2.circle(frame, (int(x), int(y)), 2, (0, 255, 0), -1)

def find_balls(balls, hsv_img, frame):
    cv_balls = []    
    
    for ball in balls:
        find_ball(ball, hsv_img, frame, cv_balls)
    return cv_balls

def find_cuestick(hsv, frame):

    table_pixel_length = frame.shape[1]
    table_pixel_width = frame.shape[0]
    mask = cv2.inRange(frame, cue_lower, cue_upper)
    # mask = cv2.inRange(frame, lower_white, upper_white)
    # Bitwise-AND mask and original image
    res = cv2.bitwise_and(frame,frame, mask=mask)

    if DISPLAY_INTERMEDIATE:
        cv2.imshow('mask',mask)
        cv2.imshow('res',res)

    # find contours in the mask and initialize the current
    # (x, y) center of the ball
    cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    for cnt in cnts:
        min_cuestick_area = table_pixel_width * 4
        # max_cuestick_area = table_pixel_width * 15
        # print(cv2.contourArea(cnt))
        # print(min_cuestick_area)
        if (min_cuestick_area < cv2.contourArea(cnt)):
            
            rows,cols = hsv.shape[:2]
            [vx,vy,x,y] = cv2.fitLine(cnt, cv2.DIST_L2,0,0.01,0.01)
            left_y = int((-x*vy/vx) + y)
            right_y = int(((cols-x)*vy/vx)+y)

            mid_point = (int(x), int(y))
            left_point = (int(0),int(left_y))
            right_point = (int(cols-1),int(right_y))
            if DISPLAY:
                cv2.line(frame,(cols-1,right_y),(0,left_y),white,2)
                cv2.circle(frame, mid_point, 2, red, 2)
                cv2.circle(frame, left_point, 2, red, 2)
                cv2.circle(frame, right_point, 2, red, 2)

            norm_mid_point = norm_coordinates(mid_point[0], mid_point[1], 0, table_pixel_length, 0, table_pixel_width)
            norm_left_point = norm_coordinates(left_point[0], left_point[1], 0, table_pixel_length, 0, table_pixel_width)
            norm_right_point = norm_coordinates(right_point[0], right_point[1], 0, table_pixel_length, 0, table_pixel_width)
            # print("find cuestick")
            return [norm_mid_point, norm_left_point, norm_right_point]

def getResizedFrame(cap):
    if USING_CAMERA:
        ret, frame = cap.read()
    else:
        filename = "purple.jpg"
        # filename = "/Users/skim/ws/500/cv/pool.jpg"
        frame = cv2.imread(filename)
    frame_height = frame.shape[0]
    frame_width = frame.shape[1]
    resize_frame_height = int(frame_height / frame_width * RESIZE_FRAME_WIDTH)
    frame = cv2.resize(frame, (RESIZE_FRAME_WIDTH, resize_frame_height))

    return frame

def show_edges():
    # cap = cv2.VideoCapture(0)
    while True:
        # ret, img = cap.read()
        # img = getResizedFrame(cap)
        # cv2.imwrite('test_imgs/4.jpg', img)
        print('lol')
        img = cv2.imread('../test_imgs/3.jpg')
        table_coords = 188,107,1148,554
        if not table_coords:
            continue
        x1,y1,x2,y2 = table_coords
        img = img[int(y1):int(y2),int(x1):int(x2)]
        gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
        kernel_size = 5
        blur_gray = cv2.GaussianBlur(gray,(kernel_size, kernel_size),0)

        low_threshold = 50
        high_threshold = 100
        edges = cv2.Canny(img, low_threshold, high_threshold)
        cv2.imshow('edges', edges)
        wait_escape()

def main():
    show_edges()
    balls = init_ballinfo()

    if USING_CAMERA:
        cap = cv2.VideoCapture(0)
        # cap.set(cv2.CV_CAP_PROP_BRIGHTNESS, 50)
    running = True
    while running:
        frame = None

        # Take each frame
        # if USING_CAMERA:
        #     ret, frame = cap.read()
        # else:
        #     filename = "purple.jpg"
        #     # filename = "/Users/skim/ws/500/cv/pool.jpg"
        #     frame = cv2.imread(filename)

        # frame_height = frame.shape[0]
        # frame_width = frame.shape[1]
        # resize_frame_height = int(frame_height / frame_width * RESIZE_FRAME_WIDTH)
        # frame = cv2.resize(frame, (RESIZE_FRAME_WIDTH, resize_frame_height))
        frame = getResizedFrame(cap)
        # cv2.imwrite()

        if DISPLAY_INTERMEDIATE:
            # ret, frame = cap.read()
            cv2.imshow('frame', frame)
            wait_escape()

        # table_coords = compute_lines(frame, DISPLAY_HOUGH)
        # table_coords = 76,24,642,282
        
        table_coords = 188,107,1148,554
        if not table_coords:
            continue
        x1,y1,x2,y2 = table_coords
        frame = frame[int(y1):int(y2),int(x1):int(x2)]
        
        # cv2.imwrite('purple.jpg', frame)
        # Convert BGR to HSV
        hsv_img = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        cv_balls = find_balls(balls, hsv_img, frame)

        print(cv_balls)
        print("cuestick " + str(find_cuestick(hsv_img, frame)))

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
