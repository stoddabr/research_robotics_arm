

class Paw:
    """ controls the arm manipulator and joints """
    
    def __init__(self):
        pass


    def initMove(self):
        """ Move servo to initial position """

        Board.setBusServoPulse(1, self.servo1 - 50, 300)
        Board.setBusServoPulse(2, 500, 500)
        self.AK.setPitchRangeMoving((0, 10, 10), -30, -30, -90, 1500)

    def reset(self):
        """ Reset class variables """

        pass
