import sys
from typing import List

import numpy as np

from cv.cv_cue_stick import CVCueStick
from pool.src.physics.collisions import check_ball_wall_collision, resolve_ball_wall_collision, \
    check_ball_ball_collision, resolve_ball_ball_collision
from pool.src.physics.coordinates import Coordinates
from pool.src.physics.utility import get_angle, get_distance, get_line_endpoint_within_box, get_parallel_line, \
    check_ray_circle_intersection, get_point_on_line_distance_from_point, solve_vf_or_d, get_distance_before_stop, \
    get_vf_after_distance
from pool.src.physics.vector import Vector
from pool.src.pool.ball_type import BallType
from pool.src.pool.game_type import GameType
from pool.src.pool.pool_ball import PoolBall

# from pool.physics.collisions import check_ball_ball_collision, resolve_ball_ball_collision, resolve_ball_wall_collision, \
#     check_ball_wall_collision
# from physics.coordinates import Coordinates
# from physics.utility import get_distance, get_line_endpoint_within_box, check_ray_circle_intersection, \
#     get_parallel_line, get_point_on_line_distance_from_point, get_angle
# from physics.vector import Vector
# from pool.ball_type import BallType
# from pool.game_type import GameType
# from pool.pool_ball import PoolBall

sys.path.append('/Users/skim/ws/500')
sys.path.append('/Users/skim/ws/500/cv')
from cv.cv_ball import CVBall

LONG_DIAMONDS = 8
SHORT_DIAMONDS = 4
CUE_START_DIAMOND = 2
RACK_START_DIAMOND = 6

# TODO: Get these from a config file
BALL_MASS = 5
BALL_RADIUS = 30

# Physics properties
# For now, taken from: https://billiards.colostate.edu/faq/physics/physical-properties/
BALL_TABLE_FRICTION_COEFFICIENT = 0.2
BALL_BALL_FRICTION_RESTITUTION = 0.95
BALL_WALL_FRICTION_RESTITUTION = 0.75

# BALL_TABLE_ACC = -0.0005 # Decent value for demo
BALL_TABLE_ACC = -0.0000001 # Debug value


class PoolTable:
    def __init__(self, nw, se, cv_ball_locations=None, cv_cue_points=None):
        # Table dimensions
        self.nw = nw
        self.se = se

        self.top = nw.y
        self.right = se.x
        self.bottom = se.y
        self.left = nw.x

        self.length = self.right - self.left
        self.width = self.top - self.bottom

        # Pool table balls
        if cv_ball_locations is None:
            self.balls = PoolTable.get_balls(GameType.NINE_BALL)
            self.rack_balls(GameType.NINE_BALL)
            assert (BallType.CUE in self.balls)
            self.cue_ball = self.balls[BallType.CUE]
        else:
            self.set_cv_balls(cv_cue_points)

        # Cue stick
        if cv_cue_points is None: # Nothing given from CV input
            self.cue_stick_tip = self.cue_stick_back = None
            self.floating_cue_stick = False
            self.cue_angle = None
            self.floating_cue_stick_line_end = None
        else:
            self.set_cv_cue_stick(cv_cue_points)

        # Cue ball starting velocity
        self.cue_ball_vel = Vector(0.0, 0.0)

        # Deflection lines
        self.ghost_ball_lines = {}  # Dict from Ball -> (ghost-ball-start, ghost-ball-end)

        # For drawing rail and pockets
        self.rail_width = 0

        self.hole_centers = self.get_pockets()
        self.hole_radius = 2.25 * self.cue_ball.radius

        self.corner_pocket_width = 5
        self.side_pocket_width = 5

        self.corner_pocket_angle = 5
        self.side_pocket_angle = 5

    def convert_cv_coords(self, cv_x, cv_y) -> Coordinates:
        """
        Convert coordinates (cv_ball coordinates go from [0, 1.0])

        :param cv_coords: tuple of cv coordinates as floats
        :return: proper Coordinates for the pool table
        """

        # print("convert_cv_coords input: ({}, {})".format(cv_x, cv_y))

        # Hard-coded offsets to align projector output
        if cv_x < 0.6:
            X_OFFSET = -5
            X_SCALE = 1.025
        else:
            X_OFFSET = 10
            X_SCALE = 1.0
        Y_OFFSET = -13
        Y_SCALE = 1.0

        new_x = self.left + X_OFFSET + self.length * cv_x * X_SCALE
        new_y = self.bottom - Y_OFFSET + self.width * (1.0 - cv_y) * Y_SCALE
        return Coordinates(new_x, new_y)

    def convert_cv_color(self, color):
        if color is 'white':
            return BallType.CUE
        elif color is 'yellow':
            return BallType.ONE
        elif color is 'blue':
            return BallType.TWO
        elif color is 'red':
            return BallType.THREE
        elif color is 'purple':
            return BallType.FOUR
        elif color is 'orange':
            return BallType.FIVE
        elif color is 'green':
            return BallType.SIX
        elif color is 'brown':
            return BallType.SEVEN
        elif color is 'black':
            return BallType.EIGHT
        # TODO: nine-ball
        else:
            return BallType.EIGHT
            # raise Exception('unknown cv ball color -- find Tina and throw saas at her')

    def set_cv_balls(self, cv_balls: List[CVBall]):
        """
        Place pool balls from locations given by CV module.

        self.balls and self.cue_ball will be set
        """

        """
        class CVBall:
            def __init__(self, x, y, color):
                self.x = x
                self.y = y
                self.color = color
        """

        # Initialize empty ball list
        self.balls = {}

        # If CV detected no balls
        if cv_balls is None or cv_balls is []:
            return

        # Convert each CVBall to a PoolBall
        for cv_ball in cv_balls:
            pos = self.convert_cv_coords(cv_ball.x, cv_ball.y)
            ball_type = self.convert_cv_color(cv_ball.color)

            ball = PoolBall(ball_type, pos, BALL_MASS, BALL_RADIUS)

            self.balls[ball_type] = ball

            if ball_type is BallType.CUE:
                self.cue_ball = ball

    def set_cv_cue_stick(self, cv_cue_stick: CVCueStick):
        """
        Use 2 points to get the cue stick angle.

        :return:
        """

        if cv_cue_stick is None or cv_cue_stick.tip is None or cv_cue_stick.back is None:
            self.cue_stick_tip = self.cue_stick_back = None
            self.floating_cue_stick = False
            self.cue_angle = None
            self.floating_cue_stick_line_end = None
            return

        # Check if cue stick line intersects the cue ball
        self.cue_stick_tip = self.convert_cv_coords(cv_cue_stick.tip[0], cv_cue_stick.tip[1])
        self.cue_stick_back = self.convert_cv_coords(cv_cue_stick.back[0], cv_cue_stick.back[1])


        # ¯\_(ツ)_/¯
        self.cue_angle = get_angle(self.cue_stick_tip, self.cue_stick_back)

        nw = Coordinates(self.left, self.top)
        se = Coordinates(self.right, self.bottom)
        cue_stick_line_extended_end = get_line_endpoint_within_box(self.cue_stick_back, self.cue_angle, nw, se, 1.0)

        if check_ray_circle_intersection(self.cue_stick_tip, cue_stick_line_extended_end, self.cue_ball.pos, self.cue_ball.radius):
            self.floating_cue_stick = False
            self.floating_cue_stick_line_end = None
        else:
            self.floating_cue_stick = True
            self.floating_cue_stick_line_end = cue_stick_line_extended_end




    def reset_cue_ball(self):
        self.cue_angle = 0.0

    @staticmethod
    def get_balls(game: GameType):
        m = BALL_MASS
        r = BALL_RADIUS

        ball_c = PoolBall(BallType.CUE, Coordinates(0, 0), m, r)
        ball_1 = PoolBall(BallType.ONE, Coordinates(0, 0), m, r)
        ball_2 = PoolBall(BallType.TWO, Coordinates(0, 0), m, r)
        ball_3 = PoolBall(BallType.THREE, Coordinates(0, 0), m, r)
        ball_4 = PoolBall(BallType.FOUR, Coordinates(0, 0), m, r)
        ball_5 = PoolBall(BallType.FIVE, Coordinates(0, 0), m, r)
        ball_6 = PoolBall(BallType.SIX, Coordinates(0, 0), m, r)
        ball_7 = PoolBall(BallType.SEVEN, Coordinates(0, 0), m, r)
        ball_8 = PoolBall(BallType.EIGHT, Coordinates(0, 0), m, r)
        ball_9 = PoolBall(BallType.NINE, Coordinates(0, 0), m, r)

        balls = {
            BallType.CUE: ball_c,
            BallType.ONE: ball_1,
            BallType.TWO: ball_2,
            BallType.THREE: ball_3,
            BallType.FOUR: ball_4,
            BallType.FIVE: ball_5,
            BallType.SIX: ball_6,
            BallType.SEVEN: ball_7,
            BallType.EIGHT: ball_8,
            BallType.NINE: ball_9,
        }

        return balls

    def get_pockets(self) -> List[Coordinates]:
        """
        Get 6 coordinates for the center of the pockets.
        """

        return [
            Coordinates(self.left, self.top),
            Coordinates(self.left + self.length / 2, self.top),
            Coordinates(self.left + self.length, self.top),
            Coordinates(self.right, self.bottom),
            Coordinates(self.right - self.length / 2, self.bottom),
            Coordinates(self.right - self.length, self.bottom),
        ]

    def rack_balls(self, game: GameType):
        """
        Set the position of balls for racking position.
        *All balls assumed to have the same radius.*

        :param game: type of game to be racked for
        """

        # TODO: Need random/shuffling of balls except for fixed balls (ONE, NINE)
        balls = self.balls
        r = balls[BallType.ONE].radius

        # Set cue ball position
        balls[BallType.CUE].pos.x = self.left + (CUE_START_DIAMOND / LONG_DIAMONDS) * self.length
        balls[BallType.CUE].pos.y = self.bottom + self.width / 2 + 19

        if game == GameType.ONE_BALL:
            # Coordinates of leading 1 ball
            balls[BallType.ONE].pos.x = self.left + (RACK_START_DIAMOND / LONG_DIAMONDS) * self.length
            balls[BallType.ONE].pos.y = self.bottom + self.width / 2

            # DEBUG: Demonstrate imprecision because of ints/pixels
            # self.cue_angle = 270
            # balls[BallType.CUE].pos.x = balls[BallType.ONE].pos.x + 19
            # balls[BallType.CUE].pos.y = balls[BallType.ONE].pos.y + 50
        elif game == GameType.THREE_BALL:
            # Coordinates of leading 1 ball
            balls[BallType.ONE].pos.x = self.left + (RACK_START_DIAMOND / LONG_DIAMONDS) * self.length
            balls[BallType.ONE].pos.y = self.bottom + self.width / 2

            balls[BallType.TWO].pos.x = balls[BallType.ONE].pos.x + np.sqrt(3) * r
            balls[BallType.TWO].pos.y = balls[BallType.ONE].pos.y + r

            balls[BallType.THREE].pos.x = balls[BallType.ONE].pos.x + np.sqrt(3) * r
            balls[BallType.THREE].pos.y = balls[BallType.ONE].pos.y - r

        elif game == GameType.NINE_BALL:
            # Coordinates of leading 1 ball
            balls[BallType.ONE].pos.x = self.left + (RACK_START_DIAMOND / LONG_DIAMONDS) * self.length
            balls[BallType.ONE].pos.y = self.bottom + self.width / 2

            balls[BallType.TWO].pos.x = balls[BallType.ONE].pos.x + np.sqrt(3) * r
            balls[BallType.TWO].pos.y = balls[BallType.ONE].pos.y + r

            balls[BallType.THREE].pos.x = balls[BallType.ONE].pos.x + np.sqrt(3) * r
            balls[BallType.THREE].pos.y = balls[BallType.ONE].pos.y - r

            balls[BallType.FOUR].pos.x = balls[BallType.TWO].pos.x + np.sqrt(3) * r
            balls[BallType.FOUR].pos.y = balls[BallType.TWO].pos.y + r

            balls[BallType.NINE].pos.x = balls[BallType.TWO].pos.x + np.sqrt(3) * r
            balls[BallType.NINE].pos.y = balls[BallType.TWO].pos.y - r

            balls[BallType.FIVE].pos.x = balls[BallType.THREE].pos.x + np.sqrt(3) * r
            balls[BallType.FIVE].pos.y = balls[BallType.THREE].pos.y - r

            balls[BallType.SIX].pos.x = balls[BallType.NINE].pos.x + np.sqrt(3) * r
            balls[BallType.SIX].pos.y = balls[BallType.NINE].pos.y + r

            balls[BallType.SEVEN].pos.x = balls[BallType.NINE].pos.x + np.sqrt(3) * r
            balls[BallType.SEVEN].pos.y = balls[BallType.NINE].pos.y - r

            balls[BallType.EIGHT].pos.x = balls[BallType.SEVEN].pos.x + np.sqrt(3) * r
            balls[BallType.EIGHT].pos.y = balls[BallType.SEVEN].pos.y + r

    def pocket_balls(self):
        """
        Call this method to check if any balls should be pocketed and remove them from play.

        :return:
        """

        pocketed_ball_names = []

        for ball_name in self.balls:
            ball = self.balls[ball_name]
            for pocket_pos in self.hole_centers:
                d = get_distance(ball.pos, pocket_pos)
                pocketed = d < self.hole_radius
                if pocketed:
                    pocketed_ball_names.append(ball_name)

        # Remove these balls from play
        for ball_name in pocketed_ball_names:
            if ball_name is not BallType.CUE:  # Don't pocket cue ball
                del self.balls[ball_name]
            else:
                self.reset_cue_ball()

                # Restart cue ball position
                self.balls[ball_name].pos.x = self.left + (CUE_START_DIAMOND / LONG_DIAMONDS) * self.length
                self.balls[ball_name].pos.y = self.bottom + self.width / 2 + 20
                self.balls[ball_name].vel.x = self.balls[ball_name].vel.y = 0

    def get_balls_by_distance(self, ball_pos: Coordinates) -> List[PoolBall]:
        """
        Return the ball locations, by least to greatest distance of ball_pos.

        :param ball_pos: Given ball position.
        :return: Sorted list of pool balls from closest to farthest.
        """
        balls_by_distance = list(self.balls.values())
        balls_by_distance.sort(key=lambda b: get_distance(ball_pos, b.pos))

        return balls_by_distance

    @staticmethod
    def check_ball_intersects_ball(ball_a: PoolBall, ball_a_end: Coordinates, ball_b: PoolBall):
        """
        Given the line of Ball A (start and end position), determine if it will collide with Ball B.

        :param ball_a: The moving PoolBall
        :param ball_a_end: End position of moving PoolBall
        :param ball_b: Static PoolBall
        :return: True if A will collide with B, False otherwise
        """

        mid_start, mid_end = ball_a.pos, ball_a_end
        top_start, top_end = get_parallel_line(mid_start, mid_end, ball_a.radius, True)
        bot_start, bot_end = get_parallel_line(mid_start, mid_end, ball_a.radius, False)

        return (check_ray_circle_intersection(top_start, top_end, ball_b.pos, ball_b.radius) or
                check_ray_circle_intersection(bot_start, bot_end, ball_b.pos, ball_b.radius))

    @staticmethod
    def get_angle_after_ball_collision(ball_a, angle, ball_b):
        """

        :param ball_a: Moving ball
        :param angle: Angle that ball A collided into ball B
        :param ball_b: Static ball
        :return:
        """
        # TODO: Refactor ball_hit angle stuff here... or just delete this
        return

    @staticmethod
    def check_enough_speed(start: Coordinates, end: Coordinates, vel: Vector) -> (float, float):
        """

        :param start: position of ball
        :param end: target position of ball
        :param vel: velocity of ball
        :return: 0 - distance if not enough velocity, None otherwise
                 1 - final speed if enough velocity, None otherwise
        """

        dist_traveled = get_distance_before_stop(abs(vel.get_magnitude()), BALL_TABLE_ACC)
        dist_required = get_distance(start, end)

        if dist_traveled < dist_required:
            return dist_traveled, None

        # Final velocity of struck ball after collision
        vf = get_vf_after_distance(abs(vel.get_magnitude()), BALL_TABLE_ACC, dist_required)
        return None, vf

    def ball_hit(self, v_start: Vector, struck_ball: PoolBall) -> (Coordinates, Coordinates, PoolBall, Vector):
        """
        Take in the starting position of a ball and the Force it will be struck with.
        Output is where the ghost ball will begin and end to be displayed.
        If there was another ball hit along the way, that ball will also be returned with the expectation
        that this function will be called for that ball again, for as many iterations desired.

        :param v_start: velocity that struck_ball starts with
        :param struck_ball: PoolBall being struck
        :return: 0 - Ghost ball start
                 1 - Ghost ball end
                 2 - Collided pool ball if there was one, None otherwise
                 3 - Collided pool ball velocity if there was one, None otherwise
        """

        assert all(param is not None for param in [v_start, struck_ball]), 'None param passed in'
        assert self.cue_angle is not None, 'self.cue_angle is None'

        if v_start is None or v_start.get_magnitude() == 0.0:
            return

        # Return values
        ghost_start, ghost_end, collided_ball, collided_vel = None, None, None, None

        radius = struck_ball.radius
        nw = Coordinates(self.left, self.top)
        se = Coordinates(self.right, self.bottom)

        mid_start = struck_ball.pos
        mid_end = ghost_start = get_line_endpoint_within_box(mid_start, v_start.get_angle(), nw, se, radius)

        # Iterate through pool balls, from closest to farthest
        for object_ball in self.get_balls_by_distance(mid_start):
            if object_ball.ball_type is struck_ball.ball_type: continue  # Skip self

            # Found a ball-ball collision
            if PoolTable.check_ball_intersects_ball(struck_ball, mid_end, object_ball):
                # TODO: Check if enough there's velocity to make it to the ball
                d, vf_mag = PoolTable.check_enough_speed(struck_ball.pos, object_ball.pos, v_start)
                if d is not None: # Not enough speed
                    ghost_start = ghost_end = Coordinates(
                        struck_ball.pos.x + d * np.cos(np.radians(v_start.get_angle())),
                        struck_ball.pos.y + d * np.sin(np.radians(v_start.get_angle())))
                    return ghost_start, ghost_end, None, None

                # Ghost line start
                ghost_start = get_point_on_line_distance_from_point(mid_start,
                                                                    mid_end,
                                                                    object_ball.pos,
                                                                    2 * object_ball.radius)
                ##########################################
                # Calculate struck ball deflection angle #
                ##########################################

                # Need to calculate object ball angle to get struck ball deflection angle
                object_ball_angle = get_angle(object_ball.pos, ghost_start)
                object_ball_ghost_end = get_line_endpoint_within_box(object_ball.pos, object_ball_angle, nw, se,
                                                                     object_ball.radius)

                # 90 degrees will be added or subtracted to this to get the final result
                struck_deflect_angle = get_angle(object_ball_ghost_end, object_ball.pos)

                # Used to see if struck ball is hit to the left or right of object ball
                struck_object_angle = get_angle(object_ball.pos, self.cue_ball.pos)

                # Hotfix
                if struck_object_angle is None:
                    struck_object_angle = 0.0

                if self.cue_angle % 360 == 0:  # Edge case when perfectly to the right
                    struck_deflect_angle = (struck_deflect_angle + 90) % 360
                elif self.cue_angle < struck_object_angle:  # Struck ball to the RIGHT of object ball
                    struck_deflect_angle = (struck_deflect_angle - 90) % 360
                else:  # Struck ball to the LEFT of object ball
                    struck_deflect_angle = (struck_deflect_angle + 90) % 360

                # Update return values and return
                ghost_cushion = get_line_endpoint_within_box(ghost_start, struck_deflect_angle, nw, se, struck_ball.radius)

                # Check if deflected struck ball will reach the cushion
                vf = Vector(vf_mag * np.cos(np.radians(struck_deflect_angle)),
                            vf_mag * np.sin(np.radians(struck_deflect_angle)))

                d, vf_mag = PoolTable.check_enough_speed(ghost_start, ghost_cushion, vf)
                if d is not None: # Didn't make it to the cushion
                    ghost_end = Coordinates(
                        ghost_start.x + d * np.cos(np.radians(struck_deflect_angle)),
                        ghost_start.y + d * np.sin(np.radians(struck_deflect_angle))
                    )
                    collided_vel = Vector(v_start.x/2, v_start.y/2) # FIXME: What to return here?
                else:
                    ghost_end = ghost_cushion
                    collided_vel = Vector(vf_mag * np.cos(np.radians(object_ball_angle)),
                                          vf_mag * np.sin(np.radians(object_ball_angle)))

                assert ghost_start is not None
                assert ghost_end is not None
                assert object_ball is not None
                assert object_ball_angle is not None

                return ghost_start, ghost_end, object_ball, collided_vel

        # No ball collisions, wall collision

        # FIXME: HACKY - Create a pseudo-pool ball (where the ball would end up on the cushion)
        struck_ball_on_cushion = PoolBall(None, Coordinates(ghost_start.x, ghost_start.y),
                                          0.0, struck_ball.radius,
                                          vel=Vector(ghost_start.x - struck_ball.pos.x,
                                                     ghost_start.y - struck_ball.pos.y).unit())

        # Check if struck ball makes it to the cushion
        d, vf_mag = PoolTable.check_enough_speed(struck_ball.pos, struck_ball_on_cushion.pos, v_start)
        if d is not None:  # Not enough speed
            ghost_start = ghost_end = Coordinates(
                struck_ball.pos.x + d * np.cos(np.radians(v_start.get_angle())),
                struck_ball.pos.y + d * np.sin(np.radians(v_start.get_angle())))
            return ghost_start, ghost_end, None, None

        # Otherwise, struck ball makes it to the cushion
        ball_wall_collision = check_ball_wall_collision(struck_ball_on_cushion, self.top, self.left, self.bottom,
                                                        self.right)
        assert ball_wall_collision is not None, "there should be a ball-wall collision, bc there were no ball-ball collisions"
        resolve_ball_wall_collision(struck_ball_on_cushion, ball_wall_collision)

        # The ghost cue ball now has a new velocity vector we can use to draw the deflection line
        deflection_angle = struck_ball_on_cushion.vel.get_angle()
        ghost_end = get_line_endpoint_within_box(ghost_start, deflection_angle, nw, se, self.cue_ball.radius)

        # Check if deflected struck ball will reach the cushion
        vf = Vector(vf_mag * np.cos(np.radians(deflection_angle)),
                    vf_mag * np.sin(np.radians(deflection_angle)))
        d, vf_mag = PoolTable.check_enough_speed(ghost_start, ghost_end, vf)

        if d is not None:  # Didn't make it to the cushion
            ghost_end = Coordinates(
                ghost_start.x + d * np.cos(np.radians(deflection_angle)),
                ghost_start.y + d * np.sin(np.radians(deflection_angle))
            )
            return ghost_start, ghost_end, None, None


        return ghost_start, ghost_end, None, None

    def set_lines(self):
        """
        Sets:
            object_deflect_line_start
            object_defect_line_end

            cue_line_end
            cue_deflect_line_end

        """

        # If cue ball is currently pocketed OR if cue stick not lined up with cue ball, skip
        if self.cue_ball is None or self.cue_angle is None or self.floating_cue_stick:
            self.ghost_ball_lines = {} # Reset all the lines
            return

        # Reset lines
        self.ghost_ball_lines = {}

        # First, strike the cue ball
        self.cue_ball_vel = Vector(np.cos(np.radians(self.cue_angle)), np.sin(np.radians(self.cue_angle)))
        cue_ghost_start, cue_ghost_end, collided_ball, collided_ball_vel = self.ball_hit(self.cue_ball_vel,
                                                                                         self.cue_ball)

        # Update map for cue ball
        self.ghost_ball_lines[self.cue_ball] = (cue_ghost_start, cue_ghost_end)

        # Iteration 1: First collided ball
        if collided_ball is not None:
            assert collided_ball_vel is not None, "collided_ball is not None, but collided_ball_vel is None!"
            ghost_start, ghost_end, collided_ball_2, collided_ball_vel_2 = self.ball_hit(
                collided_ball_vel,
                collided_ball)
            self.ghost_ball_lines[collided_ball] = (ghost_start, ghost_end)

            # # Iteration 2: First collided ball
            # if collided_ball_2 is not None:
            #     assert collided_ball_vel_2 is not None, "collided_ball_2 is not None, but collided_ball_vel_2 is None!"
            #     ghost_start, ghost_end, collided_ball_3, collided_ball_vel_3 = self.ball_hit(collided_ball_vel_2, collided_ball_2)
            #     self.ghost_ball_lines[collided_ball_2] = (ghost_start, ghost_end)

        return

    def time_step(self):
        balls = list(self.balls.values())

        # Update ball positions
        for ball in balls:
            ball.time_step()

        # Check/resolve collisions
        for i in range(len(balls)):
            # Check ball-wall collision
            ball_wall_collision = check_ball_wall_collision(balls[i], self.top, self.left, self.bottom, self.right)
            if ball_wall_collision is not None:
                resolve_ball_wall_collision(balls[i], ball_wall_collision)

            for j in range(i + 1, len(balls)):
                if check_ball_ball_collision(balls[i], balls[j]):
                    resolve_ball_ball_collision(balls[i], balls[j])

        # Check pocketed balls
        self.pocket_balls()

        # Get lines
        self.set_lines()
