import sys
sys.path.append('/home/pi/ArmPi/')
import cv2
import time
import Camera
import threading
from LABConfig import *
from ArmIK.Transform import *
from ArmIK.ArmMoveIK import *
import HiwonderSDK.Board as Board
from CameraCalibration.CalibrationConfig import *

class Paw:
    """ controls the arm manipulator and joints """
    
    def __init__(self):
        """ """

        self.reset()
        self.resetPosition()


    def reset(self):
        """ Reset class variables """

        self.unreachable = False
        self.isRunning = False
        self.closeAngle = 500  # gipper angle when grabbing object (legacy:servo1)
        self.openAngle = (500 - 280)  # legacy magic number 
        self.neutralAngle = (500 - 50)  # legacy magic number
        self.AK = ArmIK()

    def resetPosition(self):  # legacy:initMove
        """ Move servo to neutral, initial position """

        Board.setBusServoPulse(1, self.neutralAngle, 300)
        Board.setBusServoPulse(2, 500, 500)
        self.AK.setPitchRangeMoving((0, 10, 10), -30, -30, -90, 1500)
        time.sleep(1.5)


    def setGoalXY(self, goal_x, goal_y):
        """ give a new x,y goal in camera space """


    def updateCloseAngle(self, newCloseAngle):
        """ Updates the default variable for closing the gripper (eg 500) """

        self.closeAngle = newCloseAngle


    def close(self, closeAngle=None):
        """ Close the gripper paw, optionally set a custom close angle int (eg 500) """

        if closeAngle == None:
            closeAngle = self.closeAngle

        Board.setBusServoPulse(1, closeAngle, 500)
        time.sleep(0.5)


    def open(self):
        """ Open the gripper paw """

        Board.setBusServoPulse(1, self.openAngle, 500)  # 
        time.sleep(0.5)


    def moveToXY(self, world_X, world_Y, world_Z=2):
        """ move arm to goal coordinates on mat using built-in inverse kinematics 
        
        world_Z (height) is optional, default 2
        """

        result = self.AK.setPitchRangeMoving((world_X, world_Y, world_Z), -90, -90, 0, 1000)
        if result == False:
            return False  # object is unreachable
        
        time.sleep(result[2]/1000) # The third item of the return parameter is time


    def rotateGripper(self, world_angle):
        """ turn the gripper """

        Board.setBusServoPulse(2, world_angle, 500)
        time.sleep(0.5)


    def grabAtXY(self, world_X, world_Y, rotation_angle):
        """ grab object at coordinate goal location of the object """

        world_angle = getAngle(world_X, world_Y, rotation_angle)

        self.resetPosition()
        self.open()
        self.rotateGripper(world_angle)
        self.moveToXY(world_X, world_Y)
        self.close()
        self.resetPosition()


    def placeAtXY(self, world_X, world_Y, angle):
        """ place grabbed object at coordinate gooal location"""

        world_angle = getAngle(world_X, world_Y, rotation_angle)

        self.resetPosition()
        self.rotateGripper(world_angle)
        self.moveToXY(world_X, world_Y)
        self.open()
        self.resetPosition()

    def partyTime(self):
        """ spin 'n wave yo arm like you just dont care -  """

        self.resetPosition()
        Board.setBusServoPulse(1, 100, 1000)
        time.sleep(1)
        Board.setBusServoPulse(1, 800, 1000)
        time.sleep(1)
        Board.setBusServoPulse(1, 100, 1000)
        time.sleep(1)


if __name__ == '__main__':

    # will pick up a block on the red square, wave around, and put it back

    paw = Paw()
    red_block_home_coords = (-15 + 0.5, 12 - 0.5, 1.5) # x, y, angle on mat plane
    
    paw.grabAtXY(*red_block_home_coords)
    paw.partyTime()
    paw.placeAtXY(*red_block_home_coords)

