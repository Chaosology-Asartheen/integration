
# This class adds items to a queue if they are within an epsilon of the average
# otherwise it rejects them
#
# The purpose of this class is to reduce jitter in our detection and
# allow for accurate detection of static objects
# Moving objects is harder to detect
class AverageQueue(object):
  def __init__(self, limit=10):
    self.sum_x = [0] * limit
    self.sum_y = [0] * limit
    self.index = 0

    self.count = 0
    self.limit = limit

    self.adds = 0

  def add(self, x, y):
    if x == None or y == None:
      return None

    if self.count < self.limit:
      self.count += 1

    self.sum_x[self.index] = x
    self.sum_y[self.index] = y
    self.index = (self.index + 1) % self.limit

    self.adds += 1
    return True

  def get_average(self):
    if self.count == 0:
      raise Exception("Count should never be 0; add should be called before")
    else:
      return (sum(self.sum_x)/self.count, sum(self.sum_y)/self.count)
