#!/usr/bin/python3
# coding=utf8

import sys
sys.path.append('/home/pi/ArmPi/')
import cv2
import time
import Camera
import threading
# from LABConfig import *
from ArmIK.Transform import *
from ArmIK.ArmMoveIK import *
import HiwonderSDK.Board as Board
from CameraCalibration.CalibrationConfig import *

from ResearchRobotics.perception_class import Perception
from ResearchRobotics.paw_class import Paw


if sys.version_info.major == 2:
    print('Please run this program with python3!')
    sys.exit(0)


## TODO combine paw and color classes.
0

class Arm:

    def __init__(self) -> None:

        # initialize encapsulated classes
        self.eye = Perception()
        self.paw = Paw()

        # (x, y, z) Place coordinates of different colors
        # color them
        self.color_goal_coordinate = {
            'red':   (-15 + 0.5, 12 - 0.5, 1.5),
            'green': (-15 + 0.5, 6 - 0.5,  1.5),
            'blue':  (-15 + 0.5, 0 - 0.5,  1.5),
        }
        # in a stack


    def colorSorting(self):
        """ grab colors and place them onto their spaces """

        # TODO multithread with Rossros
        target_colors = [('red','green','blue')]

        while True:
            self.setBuzzer(0.1)
            is_not_blind = self.eye.see()
            if is_not_blind:
                # find block
                loc, found_color = self.eye.detect(target_color=target_colors, print_loc=True)
                
                # see result in window and arm led
                if found_color:
                    self.paw.set_rgb(color)
                key = self.eye.display()
                if key == 27:  # ??
                    break
                
                # grab block
                self.paw.grabAtXY(*loc)
                
                # place block at cooresponding coordinate
                self.paw.placeAtXY(*self.color_goal_coordinate[found_color])
        self.eye.close()


    def exit(self):
        """ App exit gameplay call """
        # may be necessary for threading
        pass 


    def reset(self):
        """ Reset class variables """

        # reset encapsulated classes
        self.paw.reset()
        self.eye.reset()



    def setBuzzer(self, timer):
        """ Activate buzzer to sound for 'timer' seconds """

        Board.setBuzzer(0)
        Board.setBuzzer(1)
        time.sleep(timer)
        Board.setBuzzer(0)


    
    def set_rgb(color):
        """ Set the RGB light color of the expansion board to make it consistent with the color to be tracked """

        if color == "red":
            Board.RGB.setPixelColor(0, Board.PixelColor(255, 0, 0))
            Board.RGB.setPixelColor(1, Board.PixelColor(255, 0, 0))
            Board.RGB.show()
        elif color == "green":
            Board.RGB.setPixelColor(0, Board.PixelColor(0, 255, 0))
            Board.RGB.setPixelColor(1, Board.PixelColor(0, 255, 0))
            Board.RGB.show()
        elif color == "blue":
            Board.RGB.setPixelColor(0, Board.PixelColor(0, 0, 255))
            Board.RGB.setPixelColor(1, Board.PixelColor(0, 0, 255))
            Board.RGB.show()
        else:
            Board.RGB.setPixelColor(0, Board.PixelColor(0, 0, 0))
            Board.RGB.setPixelColor(1, Board.PixelColor(0, 0, 0))
            Board.RGB.show()


if __name__ == '__main__':
    # Identifies locations of a block and labels it in the camera video display

    arm = Arm()
    arm.colorSorting()