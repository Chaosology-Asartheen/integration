
# This class adds items to a queue if they are within an epsilon of the average
# otherwise it rejects them
class AverageQueue(object):
  def __init__(self, limit=50, xepsilon=50, yepsilon=None):
    self.sum_x = [0] * limit
    self.sum_y = [0] * limit
    self.color = None
    self.index = 0

    self.count = 0
    self.limit = limit
    self.xeps = xepsilon
    if yepsilon == None:
        self.yeps = xepsilon

    self.adds = 0

  def add(self, x, y, color):
    if x == None or y == None:
      return None

    if self.count > 0:
        curr_x, curr_y = self.get_average()
        if not (curr_x - self.xeps <= x <= curr_x + self.xeps) or
            not (curr_y - self.yeps <= y <= curr_y + self.yeps):
            return False

    if self.count < self.limit:
      self.count += 1

    self.sum_x[self.index] = x
    self.sum_y[self.index] = y
    self.index = (self.index + 1) % self.limit

    self.color = color
    self.adds += 1
    return True

  def get_average(self):
    if self.count == 0:
      raise Exception("Count should never be 0; add should be called before")
    else:
      return (sum(self.sum_x)/self.count, sum(self.sum_y)/self.count, self.color)
