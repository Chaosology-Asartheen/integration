# import the necessary packages
import numpy as np
import argparse
import cv2
import sys
from datetime import datetime

import time
import sys
# sys.path.append('/Users/harryxu/Desktop/Harrys_Stuff/School/Carnegie_Mellon_Undergrad/08_Spring_2019/18500/integration')
# sys.path.append('/Users/harryxu/Desktop/Harrys_Stuff/School/Carnegie_Mellon_Undergrad/08_Spring_2019/18500/integration/cv')
sys.path.append('/Users/ouchristinah/Google Drive/CMU/S19/capstone/integration')
sys.path.append('/Users/ouchristinah/Google Drive/CMU/S19/capstone/integration/cv')
from cv.cv_ball import CVBall
from cv.modules.average_queue import AverageQueue
from cv.modules.color_classification import ColorClassification
from cv.hsv_filtering import get_resized_frame, norm_coordinates, wait_escape
import cv.constants as constants


def run_hough_circles(image, output, aggres, cc, display=False):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # detect circles in the image
    circles = cv2.HoughCircles(image=gray, method=cv2.HOUGH_GRADIENT, dp=constants.DP,
        minDist=constants.MIN_DIST, param1=constants.HIGH_THRESHOLD,
        param2=constants.LOW_THRESHOLD, minRadius=constants.MIN_RADIUS,
        maxRadius=constants.MAX_RADIUS)

    # ensure at least some circles were found
    if (circles is None) or (len(circles) <= 0):
        print("Can't find any circles")
        return {}

    # convert the (x, y) coordinates and radius of the circles to integers
    circles = np.round(circles[0, :]).astype("int")

    circles = list(circles)

    def in_range(coord):
        x, y = coord[0], coord[1]
        for ((ux, uy), (lx, ly)) in constants.ignore_regions:
            if (ux <= x <= lx) and (uy <= y <= ly):
                return False
        return True

    circles = list(filter(lambda x: in_range(x), circles))

    colors = []

    # debug print of all circles found
    # print(np.sort(circles, axis=0))

    result2 = {}

    # loop over the (x, y) coordinates and radius of the circles
    for (x, y, r) in circles:
        x = int(x + constants.X_CROP_OFFSET)
        y = int(y + constants.Y_CROP_OFFSET)

        # TODO: filter out x/y's that lie outside table edges or on pockets. Requires getting table coords
        color_str = cc.determine_color(image, x, y)
        colors.append(color_str)

        result2[color_str] = (x, y)

        if len(aggres) == 0:
            for k in constants.RGB_TARGETS.keys():
                aggres[k] = AverageQueue(limit=10)

        if color_str in aggres:
            aggres[color_str].add(x, y)

            # else:
            # print("Can't find a bucket for this", x, y, color_str)
            rgb = cc.get_rgb_value(color_str)
            bgr = rgb[2],rgb[1],rgb[0]
            # cv2.rectangle(output, (x - 2, y - 2), (x + 2, y + 2),bgr, -1)
            # cv2.rectangle(output, (x - 3, y - 3), (x + 3, y + 3),(0,0,0), 1)

            if True: # change me to stop using this average queue
                ave_x, ave_y = aggres[color_str].get_average()
                ave_x = int(ave_x)
                ave_y = int(ave_y)

                # draw the circle in the output image, then draw a rectangle
                # corresponding to the center of the circle
                # cv2.circle(output, (x, y), r, (0, 255, 0), 4)
                cv2.rectangle(output, (ave_x - 2, ave_y - 2), (ave_x + 2, ave_y + 2), (20,255,57), -1)
                cv2.rectangle(output, (x - 1, y - 1), (x + 1, y + 1), bgr, -1)



    for ((x, y), (w, z)) in constants.ignore_regions:
        cv2.rectangle(output, (x, y), (w, z), (255, 255, 255), 1)


    result = {}
    for k, v in aggres.items():
        try:
            result[k] = v.get_average()
        except:
            pass

    # show the output image, if prompted to by display flag
    # if display:
    #     print(circles, colors)
    # for k in sorted(aggres.keys()):
    #     print(k, aggres[k].get_average(), result2[k])

    return result

def main(display):
    cap = cv2.VideoCapture(1)

    aggres = {}
    cc = ColorClassification(epsilon=20, threshold=6)
    # identification colors
    cc.fill_color_ranges(d=constants.RGB_TARGETS)
    # display colors
    cc.fill_rgb_lookup(d=constants.DISPLAY_COLORS)

    count = 0
    times = []
    curr = time.time()
    while True:
        if count < 100:
            new_time = time.time()
            times.append((new_time - curr) * 1000)
            curr = new_time
            count += 1
            print(count)
        else:
            import statistics
            print('LAST 100 AVG: ', statistics.mean(times))

        ret, frame = cap.read()
        frame = get_resized_frame(frame)
        frame = cv2.flip(frame, 0) # Flips horizontally (hot dog)
        frame = cv2.flip(frame, 1) # Flips vertically (hamburger)
        frame_y1, frame_y2 = 53, 426
        frame_x1, frame_x2 = 13, 800
        frame = frame[int(frame_y1):int(frame_y2),int(frame_x1):int(frame_x2)]
        frame_height = frame.shape[0]
        frame_width = frame.shape[1]
        output = frame.copy()
        cv_balls = run_hough_circles(frame, output,aggres, cc, display=display)
        norm_balls = []
        for k in sorted(cv_balls.keys()):
            v = cv_balls[k]
            x,y = norm_coordinates(v[0],v[1],0,frame_width,0,frame_height)
            norm_balls.append(CVBall(x, y, k))
        print("*******************************************")
        print(norm_balls)
        cv2.imshow("output", output)
        wait_escape()

    # When everything done, release the capture
    if USING_CAMERA:
        cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main(display=True)
