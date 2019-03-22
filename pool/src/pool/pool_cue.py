from physics.coordinates import Coordinates


class PoolCue:
    def __init__(self, angle: float):
        """
        Constructor for pool cue.

        :param angle: angle (degrees) of the pool cue
        """
        # FIXME No coordinates for position, because assumed to always be towards cue ball...
        self.ang = angle