import cv2

import sys
sys.path.append('/Users/skim/ws/500')
sys.path.append('/Users/skim/ws/500/cv')
sys.path.append('/Users/skim/ws/500/pool')

from cv.test import init_ballinfo, getResizedFrame, find_cuestick, find_balls, ESC_KEY
from pool.src.gui import coords_from_pygame, TABLE_OFFSET_X, TABLE_OFFSET_Y, HEIGHT, TABLE_LENGTH, gui_update, gui_init
from pool.src.pool.pool_table import PoolTable


def main():
    screen = gui_init()

    print('in main...........')
    USING_CAMERA = False
    DISPLAY = False

    # Initialize pool table here
    nw = coords_from_pygame((TABLE_OFFSET_X, TABLE_OFFSET_Y), HEIGHT)
    se = coords_from_pygame((TABLE_OFFSET_X + TABLE_LENGTH, TABLE_OFFSET_Y + TABLE_LENGTH / 2), HEIGHT)
    table = PoolTable(nw, se)

    # Initialize CV info
    balls = init_ballinfo()
    if USING_CAMERA:
        cap = cv2.VideoCapture(1)
    running = True
    while running:
        print('running')

        frame = getResizedFrame()
        print('A')
        # CV
        hsv_img = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        cv_balls = find_balls(balls, hsv_img, frame)
        cuestick_info = find_cuestick(hsv_img, frame)
        print('B')

        # Pass parameters to pool
        table.place_cv_balls(cv_balls)
        table.set_cv_cue_stick(cuestick_info)
        print('C')

        if DISPLAY:
            cv2.imshow('frame', frame)

            while (1):
                k = cv2.waitKey(5) & 0xFF
                if k == ESC_KEY:
                    running = False
                    break

        # Here, update GUI
        gui_update(screen, table)

    # When everything done, release the capture
    if USING_CAMERA:
        cap.release()

    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()