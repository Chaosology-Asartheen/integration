import cv2
import imutils
import numpy as np

import ball_initializer
import constants
import hsv_filtering

DISPLAY_INTERMEDIATE = True
# White cue stick
CUE_LOWER = np.array([230,230,230]) #cue stick, using rgb as bounds
CUE_UPPER = np.array([255,255,255])

MIN_TIP_AREA = 130
MAX_TIP_AREA = 250

def find_cuestick(frame):
    table_pixel_length = frame.shape[1]
    table_pixel_width = frame.shape[0]
    mask = cv2.inRange(frame, CUE_LOWER, CUE_UPPER)


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
        min_cuestick_area = table_pixel_width * 5
        max_cuestick_area = table_pixel_width * 120
        # if (cv2.contourArea(cnt) > table_pixel_width):
        #     print(str(cv2.contourArea(cnt)) + " min: " + str(min_cuestick_area) + " max: " + str(max_cuestick_area) )
        if (min_cuestick_area < cv2.contourArea(cnt) < max_cuestick_area):
            rows,cols = frame.shape[:2]
            [vx,vy,x,y] = cv2.fitLine(cnt, cv2.DIST_L2,0,0.01,0.01)
            left_y = int((-x*vy/vx) + y)
            right_y = int(((cols-x)*vy/vx)+y)

            mid_point = (int(x), int(y))
            left_point = (int(0),int(left_y))
            right_point = (int(cols-1),int(right_y))
            cv2.circle(frame, mid_point, 2, (0,0,255), 2)
            cv2.circle(frame, left_point, 2, (0,0,255), 2)
            cv2.circle(frame, right_point, 2, (0,0,255), 2)
            cv2.line(frame,(cols-1,right_y),(0,left_y),(255,255,255),2)

            norm_mid_point = hsv_filtering.norm_coordinates(mid_point[0], mid_point[1], 0, table_pixel_length, 0, table_pixel_width)
            norm_left_point = hsv_filtering.norm_coordinates(left_point[0], left_point[1], 0, table_pixel_length, 0, table_pixel_width)
            norm_right_point = hsv_filtering.norm_coordinates(right_point[0], right_point[1], 0, table_pixel_length, 0, table_pixel_width)
            return [norm_mid_point, norm_left_point, norm_right_point]

def find_cuestick_tip(frame):
    table_pixel_length = frame.shape[1]
    table_pixel_width = frame.shape[0]

    # Convert img to hsv colorspace
    hsv_img = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    # Generating mask based on lower/upper red values for HSV filtering
    mask = cv2.inRange(hsv_img, ball_initializer.LOWER_RED, ball_initializer.UPPER_RED)
    mask = cv2.dilate(mask, None, iterations=2)

    res = cv2.bitwise_and(frame,frame, mask=mask)
    if DISPLAY_INTERMEDIATE:
        cv2.imshow('mask',mask)
        cv2.imshow('res',res)

    # find contours in the mask
    cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE)
    contours = imutils.grab_contours(cnts)
    for contour in contours:
        print(cv2.contourArea(contour))
        if (MIN_TIP_AREA < cv2.contourArea(contour) < MAX_TIP_AREA):
            print(cv2.contourArea(contour))
            # Find min enclosing circle around the contour
            ((x, y), radius) = cv2.minEnclosingCircle(contour)
            cv2.circle(frame, (int(x), int(y)), 2, (0, 255, 0), -1)
            # Compute normalized coordinates [0,1] for ball position
            (norm_x, norm_y) = hsv_filtering.norm_coordinates(x, y, 0, table_pixel_length, 0, table_pixel_width)
            # Compute table/irl coordinates for ball position
            (table_x, table_y) = norm_x * constants.TABLE_LENGTH, norm_y * constants.TABLE_WIDTH
            # cv2.circle(frame, (int(x), int(y)), int(radius), (0,0,0), 2)
            return x, y



def display_results(img, cuestick_res, cuestick_tip_res):
    table_pixel_length = img.shape[1]
    table_pixel_width = img.shape[0]
    if cuestick_res:
        (norm_mid_point, norm_left_point, norm_right_point) = cuestick_res
        cv2.circle(img, mid_point, 2, (0,0,255), 2)
        cv2.circle(img, left_point, 2, (0,0,255), 2)
        cv2.circle(img, right_point, 2, (0,0,255), 2)
        cv2.line(img,(cols-1,right_y),(0,left_y),(255,255,255),2)
    if cuestick_tip_res:
        x,y = cuestick_tip_res
        cv2.circle(img, (int(x), int(y)), 2, (0, 255, 0), -1)
    cv2.imshow('img', img)
    hsv_filtering.wait_escape()


if __name__ == "__main__":
    cap = cv2.VideoCapture(1)
    while True:
        ret, frame = cap.read()
        # filename = "/Users/ouchristinah/Google Drive/CMU/S19/capstone/integration/test_imgs/2.jpg"
        # frame = cv2.imread(filename)

        if frame is None:
            print("no frame")
            continue
        frame = hsv_filtering.getResizedFrame(frame)
        cuestick_res = find_cuestick(frame)
        cuestick_tip_res = find_cuestick_tip(frame)
        cv2.imshow('frame', frame)
        hsv_filtering.wait_escape()

    cap.release()
    cv2.destroyAllWindows()
