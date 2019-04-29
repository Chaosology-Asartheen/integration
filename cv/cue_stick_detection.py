"""cue_stick_detection utilizes RGB and HSV filtering to determine the
cue stick tip's position and angle.
"""

import argparse
import cv2
import imutils
import math
import numpy as np

import ball_initializer
import constants
import hsv_filtering

# Commandline global arguments
DISPLAY_INTERMEDIATE = False
DEBUG = False

# TODO: Requires tuning
# Min/max contour area for the cuestick tip
MIN_TIP_AREA = 170
MAX_TIP_AREA = 550
# Min/max contour area for the cuestick length
MIN_CUESTICK_AREA = 800
MAX_CUESTICK_AREA = 6000

# White cue stick rgb bounds
CUE_LOWER = np.array([230,230,230]) #cue stick, using rgb as bounds
CUE_UPPER = np.array([255,255,255])

CUE_TIP_LOWER = np.array([0,150,180])
CUE_TIP_UPPER = np.array([4,255,255])

# Threshold for cuestick area being either a ball or cuestick
IS_CIRCLE_THRESHOLD = 30

# Cuestick distance cutoff (lower than cutoff = 0 speed) and max cuestick speed
# for cuestick speed normalization
DIST_CUTOFF = 1
DIST_MAX = 15

"""find_cuestick utilizes RGB filtering to detect the cue stick position and angle.
Args:
    frame: image we want to perform cuestick detection on
Returns:
    [norm_mid_point, norm_left_point, norm_right_point]:
    normalized coordinates [0,1] of the cuestick. Mid_point is a point on the cue stick,
    left/right are points on the left/right edges of the frame where the cuestick line intersects.
"""
def find_cuestick(frame, output):
    table_pixel_length = frame.shape[1]
    table_pixel_width = frame.shape[0]
    mask = cv2.inRange(frame, CUE_LOWER, CUE_UPPER)
    mask = cv2.dilate(mask, None, iterations=1)

    if DISPLAY_INTERMEDIATE:
        # Bitwise-AND mask and original image
        res = cv2.bitwise_and(frame,frame, mask=mask)
        cv2.imshow('mask',mask)
        cv2.imshow('res',res)

    # find contours in the mask
    cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    for cnt in cnts:
        contour_area = cv2.contourArea(cnt)
        if DEBUG and contour_area > table_pixel_width * 1:
            print(str(contour_area) + " min: " + str(MIN_CUESTICK_AREA) + " max: " + str(MAX_CUESTICK_AREA))

        # Only use contour within predetermined min/max cuestick contour area
        if (MIN_CUESTICK_AREA < contour_area < MAX_CUESTICK_AREA):
            rows,cols = frame.shape[:2]
            # OpenCV's line-fitting algorithm
            [vx,vy,x,y] = cv2.fitLine(cnt, cv2.DIST_L2,0,0.01,0.01)
            # y coordinates of leftmost point on frame and rightmost point
            left_y = int((-x*vy/vx) + y)
            right_y = int(((cols-x)*vy/vx)+y)
            # mid_point is point on actual cuestick, left/right are points on the frame (left/right)
            # that help determine cuestick angle
            mid_point = (int(x), int(y))
            left_point = (int(0),int(left_y))
            right_point = (int(cols-1),int(right_y))
            try:
                cv2.circle(output, mid_point, 2, (0,0,255), 2)
                if DEBUG:
                    cv2.circle(output, left_point, 2, (0,0,255), 2)
                    cv2.circle(output, right_point, 2, (0,0,255), 2)
                    cv2.line(output,(cols-1,right_y),(0,left_y),(255,255,255),2)
            except:
                print("mid {} left {} right {}".format(mid_point, left_point, right_point))


            # Normalize coordinates for software backend
            norm_mid_point = hsv_filtering.norm_coordinates(mid_point[0], mid_point[1], 0, table_pixel_length, 0, table_pixel_width)
            norm_left_point = hsv_filtering.norm_coordinates(left_point[0], left_point[1], 0, table_pixel_length, 0, table_pixel_width)
            norm_right_point = hsv_filtering.norm_coordinates(right_point[0], right_point[1], 0, table_pixel_length, 0, table_pixel_width)
            return [norm_mid_point, norm_left_point, norm_right_point]

"""find_cuestick_tip utilizes HSV filtering to locate the red tip of the cue stick.
Args:
    frame: image we want to perform cuestick tip detection on
Returns:
    (norm_x, norm_y): normalized x,y coordinates of the cue stick tip
"""
def find_cuestick_tip(frame, output):
    table_pixel_length = frame.shape[1]
    table_pixel_width = frame.shape[0]

    # Convert img to hsv colorspace
    hsv_img = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    # Generating mask based on lower/upper red values for HSV filtering
    mask = cv2.inRange(hsv_img, CUE_TIP_LOWER, CUE_TIP_UPPER)
    mask = cv2.dilate(mask, None, iterations=4)

    res = cv2.bitwise_and(frame,frame, mask=mask)
    if DISPLAY_INTERMEDIATE:
        cv2.imshow('mask',mask)
        cv2.imshow('res',res)

    # find contours in the mask
    cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE)
    contours = imutils.grab_contours(cnts)
    for contour in contours:
        if DEBUG:
            print("Cuestick Tip contourArea={} min={} max={}".format(cv2.contourArea(contour), MIN_TIP_AREA, MAX_TIP_AREA))
        if (MIN_TIP_AREA < cv2.contourArea(contour) < MAX_TIP_AREA):
            # Find min enclosing circle around the contour
            ((x, y), radius) = cv2.minEnclosingCircle(contour)
            cv2.circle(output, (int(x), int(y)), 2, (0, 255, 0), -1)
            # Compute normalized coordinates [0,1] for ball position
            (norm_x, norm_y) = hsv_filtering.norm_coordinates(x, y, 0, table_pixel_length, 0, table_pixel_width)
            # Compute table/irl coordinates for ball position
            (table_x, table_y) = norm_x * constants.TABLE_LENGTH, norm_y * constants.TABLE_WIDTH
            # cv2.circle(frame, (int(x), int(y)), int(radius), (0,0,0), 2)
            if DEBUG:
                print("FOUND TIP: area={}".format(cv2.contourArea(contour)))
            return norm_x, norm_y

"""Computes Euclidean distance between 2 points.
Args:
    a: (x,y) point 1
    b: (x,y) point 2
Returns:
    distance between two points
"""
def distance_beween(a, b):
    x1,y1 = a
    x2,y2 = b
    return math.sqrt((x2-x1)**2 + (y2-y1)**2)

"""Computes cuestick speed based on current and past cue tip positions.
Args:
    current_position: (x,y) position of cue tip
    past_position: previous (x,y) position of cue tip
Returns:
    speed normalized between [0,1] based on positions.
"""
def compute_cuestick_speed(current_position, past_position):
    past_x, past_y = past_position
    x, y = current_position
    distance = distance_beween(past_position, (x,y))
    print("Dist: " + str(distance))
    speed = 0
    # Use cutoff in case of CV position detection jitter
    if distance > DIST_CUTOFF:
        # Normalize speed based on the DIST_MAX and DIST_CUTOFF aka min
        speed = (distance - DIST_CUTOFF) / (DIST_MAX - DIST_CUTOFF)
    return speed


if __name__ == "__main__":
    # Two commandline arguments for setting global flags
    parser = argparse.ArgumentParser(description="Cue stick detector")
    parser.add_argument("--display_intermediate", action="store_true",
                        help="display intermediate cv results")
    parser.add_argument('--debug', action='store_true', help='print debug messages')
    args = parser.parse_args()
    if (args.display_intermediate):
        DISPLAY_INTERMEDIATE = True
    if args.debug:
        DEBUG = True

    # Continuously read video camera input
    cap = cv2.VideoCapture(1)
    cuestick_past_pos = None
    while True:
        ret, frame = cap.read()
        # Commented lines below are for static images
        # filename = "/Users/ouchristinah/Google Drive/CMU/S19/capstone/integration/test_imgs/2.jpg"
        # frame = cv2.imread(filename)
        
        # cv2.imwrite("red.png", frame)
        frame = hsv_filtering.get_resized_frame(frame)
        frame_y1, frame_y2 = 37, 414
        frame_x1, frame_x2 = 0, 800
        frame = frame[int(frame_y1):int(frame_y2),int(frame_x1):int(frame_x2)]
        output = frame.copy()
        cuestick_tip_res = None
        cuestick_res = None
        cuestick_res = find_cuestick(frame, output)
        if cuestick_res:
            norm_mid_point, norm_left_point, norm_right_point = cuestick_res
        cuestick_tip_res = find_cuestick_tip(frame, output)
        if cuestick_tip_res:
            cue_tip_x, cue_tip_y = cuestick_tip_res

        if cuestick_tip_res and cuestick_res:
            norm_mid_point, norm_left_point, norm_right_point = cuestick_res
            cue_tip_x, cue_tip_y = cuestick_tip_res
            cv2.line(output,(int(cue_tip_x),int(cue_tip_y)),(int(norm_mid_point[0]),int(norm_mid_point[1])),(0,0,0),2)
        else:
            print("************************************************************")
        #     speed = compute_cuestick_speed(cuestick_tip_res, cuestick_past_pos)
        #     # print(speed)
        # cuestick_past_pos = cuestick_tip_res

        cv2.imshow('output', output) # Display the frame results
        hsv_filtering.wait_escape() # Wait for escape key to view next frame

    cap.release()
    cv2.destroyAllWindows()
