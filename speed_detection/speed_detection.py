from collections import deque
from statistics import mean
from typing import List

from cv.cv_cue_stick import CVCueStick
from cv.cv_ball import CVBall
from pool.src.physics.coordinates import Coordinates
from pool.src.physics.utility import get_distance

MOVING_THRESHOLD = 0.01 # Position diff must be greater than this to be considered 'moving'
ITERATION_TIME = .220 # Time for each CV iteration in seconds (delta-T)
SPEED_SCALE = 2.0 # Hard-coded scale value to scale sped

"""
Module to do 2 things:
    1) Detect cue stick speed
    2) Detect whether the cue ball is moving

Data flow looks like:

CV -----------------------------> PoolTable
       |                     ^
       |--> SpeedDetection --|

Where CV gives PoolTable: static ball positions and cue stick position, as usual
And now, CV gives SpeedDetection the same positions, SpeedDetection computes speed, and gives to PoolTAble
"""
class SpeedDetection:
    def __init__(self, gui_mode=False):
        self.cue_stick_tip_locations = deque(maxlen=5) # List of Coordinates; only need prev loc to get distances
        self.cue_stick_tip_locations.append(Coordinates(0.5, 0.5))
        self.cue_stick_tip_distances = deque(maxlen=5) # List of floats (distances); to get speed
        self.cue_stick_speeds = deque(maxlen=5)        # Last elem is current speed

        self.cue_ball_locations = deque(maxlen=5) # List of Coordinates
        self.cue_ball_is_moving = False

        self.gui_mode = gui_mode # DEBUG

    # Public 'setters' (not really) to be called by CV
    def set_cv_cue_stick(self, cv_cue_stick: CVCueStick):
        if cv_cue_stick is None or cv_cue_stick.tip is None:
            self.cue_stick_speeds.clear() # Reset speed state
            return

        curr_loc = Coordinates(cv_cue_stick.tip[0], cv_cue_stick.tip[1])

        # Don't consider locations that are 'thrashing'
        if len(self.cue_stick_tip_locations) > 0:
            prev_loc = self.cue_stick_tip_locations[-1]
            dist = get_distance(prev_loc, curr_loc)
            if dist < MOVING_THRESHOLD:
                # Didn't move far enough (probably thrashing)
                return

            # Append to history
            self.cue_stick_tip_locations.append(curr_loc)
            self.cue_stick_tip_distances.append(dist)

            # Update cue stick speed (FIXME: Probably need to tune this 'formula')
            curr_speed = dist / ITERATION_TIME
            print('SpeedDetection.set_cv_balls says curr_speed:', curr_speed)
            self.cue_stick_speeds.append(curr_speed)


    def set_cv_balls(self, cv_balls: List[CVBall]):
        if cv_balls is None or cv_balls is []:
            return

        for cv_ball in cv_balls:
            if cv_ball.color is 'white':
                curr_loc = Coordinates(cv_ball.x, cv_ball.y)

                # Don't consider locations that are 'thrashing'
                if len(self.cue_ball_locations) > 0:
                    prev_loc = self.cue_ball_locations[-1]
                    dist = get_distance(prev_loc, curr_loc)
                    if dist < MOVING_THRESHOLD:
                        # Didn't move far enough (probably thrashing)
                        self.cue_ball_is_moving = False
                        return

                # Append to history
                self.cue_ball_locations.append(curr_loc)

                # Update whether cue ball is moving
                self.cue_ball_is_moving = True

    # Public 'getter' to be called by PoolTable
    def get_cue_stick_speed(self):
        if self.gui_mode: return 1.0 # DEBUG

        if len(self.cue_stick_speeds) > 0:
            # return self.cue_stick_speeds[-1]
            return mean(self.cue_stick_speeds) * SPEED_SCALE
        else:
            return 0.0

    # Public 'getter' to be called by PoolTable
    def get_cue_ball_is_moving(self):
        if self.gui_mode: return False # DEBUG

        return self.cue_ball_is_moving
