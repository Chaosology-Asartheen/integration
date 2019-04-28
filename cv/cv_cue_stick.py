class CVCueStick:
    def __init__(self, tip: (float, float), back: (float, float)):
        self.tip = tip
        self.back = back

    def __repr__(self):
        return "CV Cue stick, tip: {}, back: {}".format(self.tip, self.back)