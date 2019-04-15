import cv2

import sys
import time

sys.path.append('/Users/ouchristinah/Google Drive/CMU/S19/capstone/integration')
sys.path.append('/Users/ouchristinah/Google Drive/CMU/S19/capstone/integration/cv')
sys.path.append('/Users/ouchristinah/Google Drive/CMU/S19/capstone/integration/pool')
# print(sys.path)
# sys.path.append('/Users/skim/ws/500')
# sys.path.append('/Users/skim/ws/500/cv')
# sys.path.append('/Users/skim/ws/500/pool')

from cv.hsv_filtering import init_ballinfo, getResizedFrame, find_cuestick, find_balls, ESC_KEY
from cv.houghlines import compute_lines
from cv.average_queue import AverageQueue
from pool.src.gui import coords_from_pygame, TABLE_OFFSET_X, TABLE_OFFSET_Y, HEIGHT, TABLE_LENGTH, gui_update, gui_init
from pool.src.pool.pool_table import PoolTable


def main():
    # Initialize GUI
    screen = gui_init()

    USING_CAMERA = True
    DISPLAY = False

    # Initialize pool table here
    nw = coords_from_pygame((TABLE_OFFSET_X, TABLE_OFFSET_Y), HEIGHT)
    se = coords_from_pygame((TABLE_OFFSET_X + TABLE_LENGTH, TABLE_OFFSET_Y + TABLE_LENGTH / 2), HEIGHT)
    table = PoolTable(nw, se)

    # Initialize CV info
    ball_list = ["white","blue","purple","green","brown"]
    balls = init_ball_info(ball_list)
    if USING_CAMERA:
        cap = cv2.VideoCapture(0)
    running = True
    i = 0

    averages = [AverageQueue(limit=10, xepsilon=50, yepislon=50) for _ in range(len(balls))]

    while running:
        # time.sleep(.5)
        frame = getResizedFrame(cap)
        # CV
        # table_coords = compute_lines(frame, False)
        # frame = cv2.imread("purple.jpg")
        table_coords = 188,107,1148,554
        if not table_coords:
            continue
        x1,y1,x2,y2 = table_coords
        frame = frame[int(y1):int(y2),int(x1):int(x2)]


        hsv_img = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        cv_balls = find_balls(balls, hsv_img, frame)
        cuestick_info = find_cuestick(hsv_img, frame)
        if not cuestick_info:
            print("LOREMS:FOINSD:OIASDFO:EINFOIENF:OIENF:OINE:OSFINW:AOIRFSLNK:OEISNFOINLFKSD")

        # cv_balls : ball_info (x, y, color) : list
        for ball in cv_balls:
            if ball == None:
                continue

            fit = False
            for ave in averages:
                success = ave.add(ball.x, ball.y, ball.color)
                if success:
                    if fit:
                        print("Doubly added ball, this will be harry")
                    fit = True

        new_balls = []
        for ave in averages:
            x, y, col = ave.get_average()
            new_balls.append(CVBall(x, y, col))
            if ave.adds > 1:
                print("2 balls added to this average")
            if ave.adds < 1:
                print("Didn't find any balls this cycle")
            ave.adds = 0
        cv_balls = new_balls

        # Pass parameters to pool
        table.place_cv_balls(cv_balls)
        table.set_cv_cue_stick(cuestick_info)

        if DISPLAY:
            cv2.imshow('frame', frame)

            while (1):
                k = cv2.waitKey(5) & 0xFF
                if k == ESC_KEY:
                    break
        # Here, update GUI
        gui_update(screen, table)
        i += 1

    # When everything done, release the capture
    if USING_CAMERA:
        cap.release()

    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()
