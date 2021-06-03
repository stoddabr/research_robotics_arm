"""
test_motion.py

Script to test the reliability of motion. Picks up the red square and repeatedly moves it to a new spot.
"""

from paw_class import Paw
from perception_class import Perception
import numpy as np
from ArmIK.Transform import getAngle

class RandomMover:
    def __init__(self):
        self.eye = Perception()
        self.paw = Paw()

    def randomly_move_block(self, color):
        is_not_blind = self.eye.see()
        if is_not_blind:
            # find block
            loc, found_color = self.eye.detect(target_color=color, print_loc=True)
            print('loc', loc, 'color', found_color)
            
            # see result in window and arm led
            key = self.eye.display()
            if key == 27:  # ??
                return
            
            if loc:
                # grab block
                print("Grabbing!")
                self.paw.grabAtXY(*loc)
                # place block at random coord

                print("Placing!")
                angle = np.random.uniform(-180, 180)
                world_angle = getAngle(loc[0], loc[1], angle)
                self.paw.placeAtXY(*randomCoord(loc[0], loc[1]), world_angle)

def randomCoord(x, y, min_dist=5, limits=[-10, 10, 12, 25]):
    """ get random coordinate at least min_dist from x,y """
    while True:
        rx = np.random.uniform(*limits[:2])
        ry = np.random.uniform(*limits[2:])

        if (x-rx)**2 + (y-ry)**2 > min_dist**2:
            return rx, ry

if __name__ == "__main__":
    rm = RandomMover()
    
    for _ in range(10):
        rm.randomly_move_block('red')