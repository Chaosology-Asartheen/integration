from typing import Optional

from pool.src.physics.coordinates import Coordinates
from pool.src.physics.direction import Direction
from pool.src.physics.utility import get_distance
from pool.src.physics.vector import Vector
from pool.src.pool.pool_ball import PoolBall


def check_ball_ball_collision(a: PoolBall, b: PoolBall) -> bool:
    """
    Check if two balls have collided.

    :param a: ball A
    :param b: ball B
    :return: whether these two balls are in collision
    """
    a_pos = Coordinates(a.pos.x + a.vel.x, a.pos.y + a.vel.y)
    b_pos = Coordinates(b.pos.x + b.vel.x, b.pos.y + b.vel.y)

    d = get_distance(a_pos, b_pos)
    is_colliding = d <= (a.radius + b.radius)

    return is_colliding


def resolve_ball_ball_collision(a: PoolBall, b: PoolBall):
    """
    Sets new velocity vectors after a ball-ball collision.

    :param a: ball A
    :param b: ball B
    """

    # Taken from https://en.wikipedia.org/wiki/Elastic_collision#Two-dimensional_collision_with_two_moving_objects

    a_vel_new = a.vel - (2 * b.mass) / (a.mass + b.mass) * ((a.vel - b.vel).dot_product(a.pos - b.pos)) / get_distance(
        a.pos - b.pos) ** 2 * (a.pos - b.pos)
    b_vel_new = b.vel - (2 * a.mass) / (a.mass + b.mass) * ((b.vel - a.vel).dot_product(b.pos - a.pos)) / get_distance(
        b.pos - a.pos) ** 2 * (b.pos - a.pos)

    a.vel, b.vel = a_vel_new, b_vel_new


def check_ball_wall_collision(ball: PoolBall, top, left, bottom, right) -> Optional[Direction]:
    """
    Check if a ball has collided with a wall.
    Assuming PyGame origin of upper-left.

    :param ball: pool ball
    :param nw: coordinates of northwest corner of pool table
    :param se: coordinates of southeast corner of pool table
    :return: the wall this ball has collided with OR None
    """



    # Add velocity to avoid 'sticking' to walls
    if ball.pos.y + ball.vel.y + ball.radius >= top:
        return Direction.NORTH
    elif ball.pos.x + ball.vel.x - ball.radius <= left:
        return Direction.EAST
    elif ball.pos.y + ball.vel.y - ball.radius <= bottom:
        return Direction.SOUTH
    elif ball.pos.x + ball.vel.x + ball.radius >= right:
        return Direction.WEST
    else:
        return None

# TODO: Just make these take in PoolBall, lol
def resolve_ball_wall_collision(ball: PoolBall, wall: Direction):
    """
    Sets the new velocity for this ball after it has collided with a wall.
    *Assumes wall is in one of 4 directions: N, E, S, or W*

    :param ball: pool ball
    :param wall: which wall (N, E, S, W)
    """

    if wall == Direction.NORTH or wall == Direction.SOUTH:
        ball.vel = Vector(ball.vel.x, -ball.vel.y)  # Reverse y-direction
    else:  # EAST or WEST
        ball.vel = Vector(-ball.vel.x, ball.vel.y)  # Reverse x-direction
