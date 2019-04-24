from pool.src.physics.coordinates import Coordinates
from pool.src.physics.vector import Vector
from pool.src.pool.ball_type import BallType


class PoolBall:
    """
    Represents a single pool ball.
    """

    # MASS = 0.17  # kg
    # DIAMETER = 0.05715  # m

    def __init__(self,
                 ball_type: BallType,
                 pos: Coordinates,
                 mass: float,
                 radius: float,
                 vel=None):
        self.ball_type = ball_type
        self.pos = pos
        self.mass = mass
        self.radius = radius
        if vel is None:
            self.vel = Vector(0, 0)
        else:
            self.vel = vel

    def apply_force(self, force: Vector):
        """
        Apply x and y components of force to this ball.
        """

        # Acceleration = Force / Mass
        acc_x = force.x / self.mass
        acc_y = force.y / self.mass

        self.vel.x += acc_x
        self.vel.y += acc_y

    def time_step(self):
        """
        Update position after 1 second.
        """

        # TODO Hard-coded deadstop
        if abs(self.vel.x) < 0.1:
            self.vel.x = 0
        if abs(self.vel.y) < 0.1:
            self.vel.y = 0


        # Distance = Velocity * Time
        self.pos.x += self.vel.x
        self.pos.y += self.vel.y

        # TODO Velocity slowdown
        from pool.src.pool.pool_table import BALL_TABLE_ACC
        self.vel.x += BALL_TABLE_ACC
        self.vel.y += BALL_TABLE_ACC

    def __str__(self):
        return "PoolBall {} at ({},{})".format(self.ball_type.name, self.pos.x, self.pos.y)
