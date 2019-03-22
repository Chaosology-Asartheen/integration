from typing import List

import numpy as np

from physics.collisions import check_ball_ball_collision, resolve_ball_ball_collision, resolve_ball_wall_collision, \
    check_ball_wall_collision
from physics.coordinates import Coordinates
from physics.utility import get_distance, get_line_endpoint_within_box, check_ray_circle_intersection, \
    get_parallel_line, get_point_on_line_distance_from_point, get_angle
from physics.vector import Vector
from pool.ball_type import BallType
from pool.game_type import GameType
from pool.pool_ball import PoolBall

LONG_DIAMONDS = 8
SHORT_DIAMONDS = 4
CUE_START_DIAMOND = 2
RACK_START_DIAMOND = 6

BALL_MASS = 5
BALL_RADIUS = 10


class PoolTable:
    def __init__(self, nw, se):
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
        self.balls = PoolTable.get_balls(GameType.NINE_BALL)
        self.rack_balls(GameType.NINE_BALL)
        assert (BallType.CUE in self.balls)
        self.cue_ball = self.balls[BallType.CUE]

        # Cue stick
        self.cue_angle = 0

        # Deflection lines
        self.object_deflect_line_start = None
        self.object_deflect_line_end = None

        # Cue deflect line start = cue line end (ghost ball location)
        self.cue_deflect_line_start = None
        self.cue_deflect_line_end = None

        # For drawing rail and pockets
        self.rail_width = 0

        self.hole_centers = self.get_pockets()
        self.hole_radius = 2.25 * self.cue_ball.radius

        self.corner_pocket_width = 5
        self.side_pocket_width = 5

        self.corner_pocket_angle = 5
        self.side_pocket_angle = 5

    def reset_cue_ball(self):
        self.cue_angle = 0.0
        self.cue_deflect_line_start = None
        self.cue_deflect_line_end = None

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

            for ball in self.balls.values():
                print('ball {} at {}'.format(ball.ball_type, ball.pos))

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
                    print("Ball {} is pocketed into {}".format(ball_name, pocket_pos))
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

                print("CUE BALL POCKETED...")
                print("CUE BALL POS: {}".format(self.cue_ball.pos))

    def set_lines(self):
        """
        Sets:
            object_deflect_line_start
            object_defect_line_end

            cue_line_end
            cue_deflect_line_end

        """

        # If cue ball is currently pocketed, skip
        if self.cue_ball is None:
            return

        # Reset lines
        self.object_deflect_line_start = self.object_deflect_line_end = self.cue_deflect_line_end = None

        angle = self.cue_angle
        nw = Coordinates(self.left, self.top)
        se = Coordinates(self.right, self.bottom)

        cue_mid_start = self.cue_ball.pos  # Line start is cue ball position
        cue_mid_end = self.cue_deflect_line_start = get_line_endpoint_within_box(cue_mid_start, angle, nw, se, self.cue_ball.radius)

        cue_top_start, cue_top_end = get_parallel_line(cue_mid_start, cue_mid_end, self.cue_ball.radius, True)
        cue_bot_start, cue_bot_end = get_parallel_line(cue_mid_start, cue_mid_end, self.cue_ball.radius, False)

        # Ghost ball computation
        balls_by_distance = list(self.balls.values())
        balls_by_distance.sort(key=lambda b: get_distance(cue_mid_start, b.pos))

        for ball in balls_by_distance:
            if ball.ball_type is BallType.CUE: continue  # Skip the cue ball

            if (check_ray_circle_intersection(cue_top_start, cue_top_end, ball.pos, ball.radius) or
                    check_ray_circle_intersection(cue_bot_start, cue_bot_end, ball.pos, ball.radius)):

                # print("CUE BALL INTERSECTING {}".format(ball))

                self.cue_deflect_line_start = get_point_on_line_distance_from_point(cue_mid_start, cue_mid_end, ball.pos,
                                                                                    2 * ball.radius)

                # Set object ball deflection line
                self.object_deflect_line_start = ball.pos
                object_ball_angle = get_angle(ball.pos, self.cue_deflect_line_start)
                self.object_deflect_line_end = get_line_endpoint_within_box(ball.pos, object_ball_angle, nw, se, self.cue_ball.radius)

                # Set cue ball deflection line
                cue_deflect_angle = get_angle(self.object_deflect_line_end, self.object_deflect_line_start)
                cue_object_angle = get_angle(ball.pos, self.cue_ball.pos)

                if self.cue_angle % 360 == 0:
                    # Edge case when perfectly to the right
                    cue_deflect_angle = (cue_deflect_angle + 90) % 360
                elif self.cue_angle < cue_object_angle:
                    # print("CUE BALL GOING RIGHT OF OBJECT BALl")
                    cue_deflect_angle = (cue_deflect_angle - 90) % 360
                else:
                    # print("CUE BALL GOING LEFT OF OBJECT BALl")
                    cue_deflect_angle = (cue_deflect_angle + 90) % 360

                self.cue_deflect_line_end = get_line_endpoint_within_box(self.cue_deflect_line_start, cue_deflect_angle, nw, se,
                                                                         self.cue_ball.radius)
                return

        # No ball collisions, wall collision

        # FIXME: HACKY - Create a pseudo-pool ball (where the ball would end up on the cushion)
        ghost_cue_ball = PoolBall(None, Coordinates(self.cue_deflect_line_start.x, self.cue_deflect_line_start.y),
                                  0.0, self.cue_ball.radius,
                                  vel=Vector(self.cue_deflect_line_start.x - self.cue_ball.pos.x,
                                             self.cue_deflect_line_start.y - self.cue_ball.pos.y).unit())


        ball_wall_collision = check_ball_wall_collision(ghost_cue_ball, self.top, self.left, self.bottom, self.right)
        assert ball_wall_collision is not None, "there should be a ball-wall collision, bc there were no ball-ball collisions"
        resolve_ball_wall_collision(ghost_cue_ball, ball_wall_collision)

        # The ghost cue ball now has a new velocity vector we can use to draw the deflection line
        deflection_angle = ghost_cue_ball.vel.get_angle()
        self.cue_deflect_line_end = get_line_endpoint_within_box(self.cue_deflect_line_start, deflection_angle, nw, se, self.cue_ball.radius)

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
                # print("BALL {}, WALL {}".format(balls[i], ball_wall_collision))
                resolve_ball_wall_collision(balls[i], ball_wall_collision)

            for j in range(i + 1, len(balls)):
                if check_ball_ball_collision(balls[i], balls[j]):
                    # print("BALL {}, BALL {}".format(balls[i], balls[j]))
                    resolve_ball_ball_collision(balls[i], balls[j])

        # Check pocketed balls
        self.pocket_balls()

        # Get lines
        self.set_lines()
