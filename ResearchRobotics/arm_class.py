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
from ResearchRobotics.paws_class import Paw


if sys.version_info.major == 2:
    print('Please run this program with python3!')
    sys.exit(0)


class Arm:

    def __init__(self) -> None:
        self.AK = ArmIK()
        self.__target_color = ('red',)
        self.servo1 = 500  # The angle at which the gripper is closed when gripping
        
        # initialize variables for planning
        self.count = 0
        self.track = False
        self._stop = False
        self.get_roi = False
        self.center_list = []
        self.first_move = True
        self.detect_color = 'None'
        self.action_finish = True
        self.start_pick_up = False
        self.start_count_t1 = True
        self.__isRunning = False
        # initialize encapsulated classes
        self.eye = Perception()
        self.paw = Paw()


    def colorTracking(self):
        """ app initialization call """

        print("ColorTracking Init")
        self.arm.initMove()


    def start(self):
        """ App start playing method call """

        self.reset()
        self.__isRunning = True
        print("ColorTracking Start")


    def stop(self):
        """ App stop gameplay call """

        self._stop = True
        self.__isRunning = False
        print("ColorTracking Stop")


    def exit(self):
        """ App exit gameplay call """

        self._stop = True
        self.__isRunning = False
        print("ColorTracking Exit")


    def reset(self):
        """ Reset class variables """

        self.count = 0
        self._stop = False
        self.track = False
        self.get_roi = False
        self.center_list = []
        self.first_move = True
        self.__target_color = ()
        self.action_finish = True
        self.start_pick_up = False
        self.start_count_t1 = True
        self.detect_color = 'None'

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

    eye = Perception()

    init()
    start()
    __target_color = ('red', )
    my_camera = Camera.Camera()
    my_camera.camera_open()
    while True:
        img = my_camera.frame
        if img is not None:
            frame = img.copy()
            Frame = run(frame)           
            cv2.imshow('Frame', Frame)
            key = cv2.waitKey(1)
            if key == 27:
                break
    my_camera.camera_close()
    cv2.destroyAllWindows()