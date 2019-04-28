import sys

import cv2

import sys
import time

# sys.path.append('/Users/harryxu/Desktop/Harrys_Stuff/School/Carnegie_Mellon_Undergrad/08_Spring_2019/18500/integration')
# sys.path.append('/Users/harryxu/Desktop/Harrys_Stuff/School/Carnegie_Mellon_Undergrad/08_Spring_2019/18500/integration/cv')
sys.path.append('/Users/ouchristinah/Google Drive/CMU/S19/capstone/integration')
sys.path.append('/Users/ouchristinah/Google Drive/CMU/S19/capstone/integration/cv')
sys.path.append('/Users/ouchristinah/Google Drive/CMU/S19/capstone/integration/pool')
# print(sys.path)
# sys.path.append('/Users/skim/ws/500')
# sys.path.append('/Users/skim/ws/500/cv')
# sys.path.append('/Users/skim/ws/500/pool')

from cv.hsv_filtering import find_cuestick, get_resized_frame, norm_coordinates
from cv.hough_lines import compute_lines
from cv.cv_ball import CVBall
from cv.hough_circles import run_hough_circles
from cv.modules.color_classification import ColorClassification
from cv.cue_stick_detection import find_cuestick, find_cuestick_tip
import cv.constants as constants

from pool.src.gui import coords_from_pygame, TABLE_OFFSET_X, TABLE_OFFSET_Y, HEIGHT, TABLE_WIDTH, TABLE_LENGTH, gui_update, gui_init
from pool.src.pool.pool_table import PoolTable


def gui_main():
    """
    Main function for pygame to be run by itself.
    """
    screen = gui_init()

    # Create pool table
    # TABLE_LENGTH, TABLE_WIDTH
    nw = coords_from_pygame((TABLE_OFFSET_X, TABLE_OFFSET_Y), HEIGHT)
    se = coords_from_pygame((TABLE_OFFSET_X + TABLE_LENGTH, TABLE_OFFSET_Y + TABLE_WIDTH), HEIGHT)
    table = PoolTable(nw, se)

    while 1:
        gui_update(screen, table)


def main():
    # Initialize GUI
    screen = gui_init()

    # Initialize pool table here
    nw = coords_from_pygame((TABLE_OFFSET_X, TABLE_OFFSET_Y), HEIGHT)
    se = coords_from_pygame((TABLE_OFFSET_X + TABLE_LENGTH, TABLE_OFFSET_Y + TABLE_LENGTH / 2), HEIGHT)
    table = PoolTable(nw, se)

    # Initialize CV info
    cap = cv2.VideoCapture(1)

    aggres = {}
    cc = ColorClassification(epsilon=30, threshold=4)
    cc.fill_color_ranges(d=constants.RGB_TARGETS)
    cc.fill_rgb_lookup(d=constants.DISPLAY_COLORS)

    while True:
        # time.sleep(.5)

        # resize frame according to constants
        ret, frame = cap.read()
        frame = get_resized_frame(frame)
        frame = cv2.flip(frame, 0) # Flips horizontally (hot dog)
        frame = cv2.flip(frame, 1) # Flips vertically (hamburger)
        max_x = frame.shape[1]
        max_y = frame.shape[0]

        output = frame.copy()

        # CV
        cv_balls = run_hough_circles(frame, output, aggres, cc, display=True)
        cuestick_res = find_cuestick(frame, output)
        norm_mid_point = None
        if cuestick_res:
            norm_mid_point, norm_left_point, norm_right_point = cuestick_res
        cuestick_tip_res = find_cuestick_tip(frame, output)
        if cuestick_tip_res:
            cue_tip_x, cue_tip_y = cuestick_tip_res

        new_balls = []
        for k, v in cv_balls.items():
            x,y = norm_coordinates(v[0],v[1],0,max_x,0,max_y)
            new_balls.append(CVBall(x, y, k))

        print(new_balls)

        # Pass parameters to pool
        table.place_cv_balls(new_balls)
        if cuestick_tip_res is not None and norm_mid_point is not None:
            table.set_cv_cue_stick([cuestick_tip_res, norm_mid_point])

        cv2.imshow('output', output)

        # cv2.waitKey(0)
        # Here, update GUI
        gui_update(screen, table)

    # When everything done, release the capture
    cap.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
    # gui_main()
