import ball_initializer
import constants
import cv2
import numpy as np
import imutils
from datetime import datetime
from houghlines import compute_lines

ball_list

# cue_upper = np.array([18,128,255])
cue_lower = np.array([180,240,240]) #cue ball, using rgb as bounds
cue_upper = np.array([255,255,255])

# Commandline arguments
DISPLAY = False
DISPLAY_INTERMEDIATE = False
DISPLAY_HOUGH = True
USING_CAMERA = True


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
        if k == constants.ESC_KEY:
            break

def init_ball_info(ball_list):
    ball_info = ball_initializer.init_balls(ball_list)
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
            # print("min: " + str(constants.MIN_RADIUS * table_pixel_width) + " max: " + str(constants.MAX_RADIUS * table_pixel_width) + " actual: " + str(radius))
            # only proceed if the radius meets a minimum size
            # if (radius > constants.MIN_RADIUS * table_pixel_width and 
            #     radius < constants.MAX_RADIUS * table_pixel_width):
            (norm_x, norm_y) = norm_coordinates(x, y, 0, table_pixel_length, 0, table_pixel_width)
            table_x = norm_x * constants.TABLE_LENGTH
            table_y = norm_y * constants.TABLE_WIDTH
            
            
            if (constants.BALL_RADIUS < table_x < constants.TABLE_LENGTH-constants.BALL_RADIUS and
                constants.BALL_RADIUS < table_y < constants.TABLE_WIDTH-constants.BALL_RADIUS):
                # print("contour area: " + str(cv2.contourArea(c)) + " min: " + str(min_contour_area) + " max: " + str(max_contour_area))
                if (min_contour_area < cv2.contourArea(c) < max_contour_area):  
                    # print("tpw %d tpl %d" % (table_pixel_width, table_pixel_length))
                    # print("x: %f y: %f" % (x,y))
                    # print("norm_x: %f norm_y: %f" % (norm_x, norm_y))
                    
                    print("table_x: %f table_y: %f" % (table_x, table_y))
                    # print("mintx: %f minty: %f" % (2.5*constants.BALL_RADIUS, constants.TABLE_LENGTH-2.5*constants.BALL_RADIUS))
                    if (ball.str_rep != "white" or (2*constants.BALL_RADIUS < table_x < constants.TABLE_LENGTH-2*constants.BALL_RADIUS and
                        2*constants.BALL_RADIUS < table_y < constants.TABLE_WIDTH-2*constants.BALL_RADIUS)):
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
    # mask = cv2.inRange(frame, LOWER_WHITE, UPPER_WHITE)
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
    resize_frame_height = int(frame_height / frame_width * constants.RESIZE_FRAME_WIDTH)
    frame = cv2.resize(frame, (constants.RESIZE_FRAME_WIDTH, resize_frame_height))

    return frame

def show_edges():
    # cap = cv2.VideoCapture(0)
    while True:
        # ret, img = cap.read()
        # img = getResizedFrame(cap)
        # cv2.imwrite('test_imgs/4.jpg', img)
        print('lol')
        img = cv2.imread('../test_imgs/3.jpg')
        table_coords = 160,130,1200,550
        if not table_coords:
            continue
        x1,y1,x2,y2 = table_coords
        img = img[int(y1):int(y2),int(x1):int(x2)]
        gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
        kernel_size = 5
        blur_gray = cv2.GaussianBlur(gray,(kernel_size, kernel_size),0)

        low_threshold = 400
        high_threshold = 400
        edges = cv2.Canny(img, low_threshold, high_threshold)
        cv2.imshow('edges', edges)
        wait_escape()

def main():
    # show_edges()
    ball_list = 
    balls = init_ball_info(ball_list)

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
        # resize_frame_height = int(frame_height / frame_width * constants.RESIZE_FRAME_WIDTH)
        # frame = cv2.resize(frame, (constants.RESIZE_FRAME_WIDTH, resize_frame_height))
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
