# Class to store information on each ball
class BallInfo:
    def __init__(self, lower_bound, upper_bound, rgb, str_rep, min_contour):
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound
        self.bgr = (rgb[2], rgb[1], rgb[0])
        self.str_rep = str_rep
        self.min_contour = min_contour