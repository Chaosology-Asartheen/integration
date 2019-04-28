
# This class will classify objects into color buckets, using HSV filtering
class ColorClassification(object):
    def __init__(self, epsilon=10, threshold=1):
        self.color_ranges = {}
        self.rgb_lookup = {}
        self.epsilon = epsilon
        self.threshold = threshold

    def fill_color_ranges(self, d=None, filename=""):
        if d == None:
            self.color_ranges = {}
        else:
            self.color_ranges = d

    def fill_rgb_lookup(self, d=None, filename=""):
        if d == None:
            self.rgb_lookup = {}
        else:
            self.rgb_lookup = d

    def is_color(self, p, color):
        v, s, h = p
        x, y, z = self.color_ranges[color]
        # print(color, x - self.epsilon, h, x + self.epsilon)
        # print(color, y - self.epsilon, s, y + self.epsilon)
        # print(color, z - self.epsilon, v, z + self.epsilon)
        res = ((x - self.epsilon <= h <= x + self.epsilon)
            and (y - self.epsilon <= s <= y + self.epsilon)
            and (z - self.epsilon <= v <= z + self.epsilon))
        return res

    # returns color string
    def determine_color(self, img, x, y, radius=15, step=1):
        x = int(x)
        y = int(y)

        votes = {}
        for color in self.color_ranges:
            votes[color] = 0
            for row in range(y - radius, y + radius, step):
                for col in range(x - radius, x + radius, step):
                    try:
                        pixel = img[row][col]
                        if self.is_color(pixel, color):
                            votes[color] += 1
                    except:
                        pass

        if len(votes) < 1:
            return "no color"

        majority_color = max(votes.keys(), key=(lambda k: votes[k]))
        majority_votes = votes[majority_color]

        if majority_votes > self.threshold:
            return majority_color

        return "no color"

    def get_rgb_value(self, col):
        if col in self.rgb_lookup:
            return self.rgb_lookup[col]
        # default value (black?)
        return (0, 0, 0)
