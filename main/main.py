import sys

import cv2

import sys
import time

# sys.path.append('/Users/harryxu/Desktop/Harrys_Stuff/School/Carnegie_Mellon_Undergrad/08_Spring_2019/18500/integration')
# sys.path.append('/Users/harryxu/Desktop/Harrys_Stuff/School/Carnegie_Mellon_Undergrad/08_Spring_2019/18500/integration/cv')

sys.path.append('/Users/ouchristinah/Google Drive/CMU/S19/capstone/integration')
sys.path.append('/Users/ouchristinah/Google Drive/CMU/S19/capstone/integration/cv')
sys.path.append('/Users/ouchristinah/Google Drive/CMU/S19/capstone/integration/pool')

sys.path.append('/Users/skim/ws/500')
sys.path.append('/Users/skim/ws/500/cv')
sys.path.append('/Users/skim/ws/500/pool')

from cv.hsv_filtering import find_cuestick, get_resized_frame, norm_coordinates, run_hsv_filtering
from cv.hough_lines import compute_lines
from cv.cv_ball import CVBall
from cv.cv_cue_stick import CVCueStick
from cv.hough_circles import run_hough_circles
from cv.modules.color_classification import ColorClassification
from cv.cue_stick_detection import find_cuestick, find_cuestick_tip
import cv.constants as constants

from speed_detection.speed_detection import SpeedDetection

from pool.src.gui import coords_from_pygame, TABLE_OFFSET_X, TABLE_OFFSET_Y, HEIGHT, TABLE_WIDTH, TABLE_LENGTH, gui_update, gui_init, clear_screen
from pool.src.pool.pool_table import PoolTable

INIT_SLEEP = 3

def gui_main():
    """
    Main function for pygame to be run by itself.
    """
    screen = gui_init()

    # Create pool table
    # TABLE_LENGTH, TABLE_WIDTH

    nw = coords_from_pygame((TABLE_OFFSET_X, TABLE_OFFSET_Y), HEIGHT)
    se = coords_from_pygame((TABLE_OFFSET_X + TABLE_LENGTH, TABLE_OFFSET_Y + TABLE_WIDTH), HEIGHT)
    speed = SpeedDetection(gui_mode=True)
    table = PoolTable(nw, se, speed)

    while 1:
        # table.place_cv_balls(new_balls)
        # if cuestick_tip_res is not None and norm_mid_point is not None:
        #     table.set_cv_cue_stick([cuestick_tip_res, norm_mid_point])

        # table.place_cv_balls(None)

        # Cue stick on top of cue ball
        # table.set_cv_cue_stick(CVCueStick(tip=(0.3, 0.6), back=(0.1, 0.1)))

        # Striking would hit cue ball
        # table.set_cv_cue_stick(CVCueStick(tip=(0.175, 0.3)back=, (0.1, 0.1)))

        # Striking would miss cue ball
        # table.set_cv_cue_stick(CVCueStick(tip=(0.5, 0.3), back=(0.1, 0.1)))

        gui_update(screen, table, speed)


def main():
    # Initialize GUI
    screen = gui_init()
    clear_screen(screen)

    # Initialize SpeedDetection module
    speed_module = SpeedDetection()

    # Initialize pool table here
    nw = coords_from_pygame((TABLE_OFFSET_X, TABLE_OFFSET_Y), HEIGHT)
    se = coords_from_pygame((TABLE_OFFSET_X + TABLE_LENGTH, TABLE_OFFSET_Y + TABLE_WIDTH), HEIGHT)
    table = PoolTable(nw, se, speed_module)

    time.sleep(INIT_SLEEP)
    # Initialize CV info
    cap = cv2.VideoCapture(0)

    aggres = {}
    # cc = ColorClassification(epsilon=30, threshold=4)
    cc = ColorClassification(epsilon=20, threshold=6)
    cc.fill_color_ranges(d=constants.RGB_TARGETS)
    cc.fill_rgb_lookup(d=constants.DISPLAY_COLORS)

    while True:

        # resize frame according to constants
        ret, frame = cap.read()
        frame = get_resized_frame(frame)
        frame = cv2.flip(frame, 0) # Flips horizontally (hot dog)
        frame = cv2.flip(frame, 1) # Flips vertically (hamburger)
        frame_y1, frame_y2 = 53, 426
        frame_x1, frame_x2 = 13, 800
        frame = frame[int(frame_y1):int(frame_y2),int(frame_x1):int(frame_x2)]
        max_x = frame.shape[1]
        max_y = frame.shape[0]

        output = frame.copy()

        # CV
        cv_balls = run_hough_circles(frame, output, aggres, cc, display=True)
        # cv_balls = run_hsv_filtering(frame)

        cuestick_res = find_cuestick(frame, output)
        norm_mid_point = None
        if cuestick_res:
            norm_mid_point, norm_left_point, norm_right_point = cuestick_res
        cuestick_tip_res = find_cuestick_tip(frame, output)
        if cuestick_tip_res:
            cue_tip_x, cue_tip_y = cuestick_tip_res

        # HOUGH CIRCLES WAY
        new_balls = []
        for k in sorted(cv_balls.keys()):
            v = cv_balls[k]
            x,y = norm_coordinates(v[0],v[1],0,max_x,0,max_y)
            new_balls.append(CVBall(x, y, k))

        # hSV filtering
        # new_balls = cv_balls

        # print(new_balls)
        # Pass parameters to pool
        table.set_cv_balls(new_balls)
        speed_module.set_cv_balls(new_balls)

        cv_cue_stick = CVCueStick(tip=cuestick_tip_res, back=norm_mid_point)
        table.set_cv_cue_stick(cv_cue_stick)
        speed_module.set_cv_cue_stick(cv_cue_stick)

        cv2.imshow('output', output)

        # cv2.waitKey(0)
        # Here, update GUI
        gui_update(screen, table, speed_module)

    # When everything done, release the capture
    cap.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
    # gui_main()
