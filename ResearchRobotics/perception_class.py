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


if sys.version_info.major == 2:
    print('Please run this program with python3!')
    sys.exit(0)


class Perception:

    def __init__(self) -> None:

        print('Initializing perception')
        self.camera = Camera.Camera()
        self.camera.camera_open()

        # initialize frame variables
        self.latest_raw_img = np.zeros((5,5))  # blank 5x5 img
        self.latest_display_img = np.zeros((5,5)) 

        # constants used for preception
        self.color_range = { 
            'red': [(0, 151, 100), (255, 255, 255)], 
            'green': [(0, 0, 0), (255, 115, 255)], 
            'blue': [(0, 0, 0), (255, 255, 110)], 
            'black': [(0, 0, 0), (56, 255, 255)], 
            'white': [(193, 0, 0), (255, 250, 255)], 
        }
        self.range_rgb = {
            'red': (0, 0, 255),
            'blue': (255, 0, 0),
            'green': (0, 255, 0),
            'black': (0, 0, 0),
            'white': (255, 255, 255),
        }
        self.size = (640, 480)
        self.window_name = "Arm View"
        print('Finished initializing perception')


    def reset(self):
        """ Reset class variables and other important stuff """

        pass


    def set_rgb(self, color):
        """ Set the RGB light color of the expansion board 
        
        useful to make it consistent with the color to be tracked 
        """
        
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


    def setTargetColor(self, target_color):
        """ Update detection color for gripper to grab """

        self.__target_color = target_color
        return (True, ())


    def getAreaMaxContour(self, contours):
        """ Find the contour with the largest area
        
        'contours' is a list of contours to be compared
        """

        contour_area_temp = 0
        contour_area_max = 0
        area_max_contour = None

        for c in contours:  # Traverse all contours
            contour_area_temp = math.fabs(cv2.contourArea(c))  # Calculate the contour area
            if contour_area_temp > contour_area_max:
                contour_area_max = contour_area_temp
                # Only when the area is greater than 300, the contour of the largest area is effective to filter interference
                if contour_area_temp > 300: 
                    area_max_contour = c

        return area_max_contour, contour_area_max  # Return the largest contour

    def display_img(self, img, wname='default window name'):
        """ show image in window with name """

        img_disp = img.copy()
        cv2.imshow(wname, img_disp)
        key = cv2.waitKey(0)
        return key


    def testFind(self, color_range):
        """ find objects in color range
        
        useful for prototpying other colors or objects
        color_range is a 2d tuple of 3d tuples: [(0, 151, 100), (255, 255, 255)]
        returns location and if a color was found
        updates the display image used in self.display
        """

        img = self.latest_raw_img.copy()  # img to transform in search for block
        img_copy = img.copy()
        frame_resize = cv2.resize(img_copy, self.size, interpolation=cv2.INTER_NEAREST)
        frame_gb = cv2.GaussianBlur(frame_resize, (11, 11), 11)
        frame_lab = cv2.cvtColor(frame_gb, cv2.COLOR_BGR2LAB)  # Convert image to LAB space
        self.display_img(frame_lab, 'lab frame')

        frame_mask = cv2.inRange(frame_lab, color_range[0], color_range[1])  # Perform bit operations on the original image and mask
        self.display_img(frame_mask, 'mask range frame')

        # process imag  e to reduce noise and find contours
        opened = cv2.morphologyEx(frame_mask, cv2.MORPH_OPEN, np.ones((6, 6), np.uint8))  # Open operation
        closed = cv2.morphologyEx(opened, cv2.MORPH_CLOSE, np.ones((6, 6), np.uint8))  # Closed operation
        contours = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)[-2]  # Find the outline
        areaMaxContour, area_max = self.getAreaMaxContour(contours)  # Find the largest contour
        
        found_color = False
        loc = False
        if area_max > 2500:  # Have found the largest area
            # identify rectangular region around blob and blob center
            rect = cv2.minAreaRect(areaMaxContour)
            box = np.int0(cv2.boxPoints(rect))
            roi = getROI(box) # Get roi area
            img_centerx, img_centery = getCenter(rect, roi, self.size, square_length)  # Get the center coordinates of the block
            world_x, world_y = convertCoordinate(img_centerx, img_centery, self.size) # Convert to real world coordinates
            # draw outline of object
            red_color = (0, 151, 100)
            cv2.drawContours(img, [box], -1, red_color, 2)  # draw with red
            cv2.putText(img, '(' + str(world_x) + ',' + str(world_y) + ')', (min(box[0, 0], box[2, 0]), box[2, 1] - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, red_color, 1) # Draw center point in red     
            # save values to return
            loc = (world_x, world_y,rect[2])
            found_color = True

        self.latest_display_img = img  # save image for display with overlays
        return loc, found_color


    def findBlock(self):
        """ using an image, return expected block location and frame overlay 
        
        if no block was found, will return False as location
        """

        img_copy = self.latest_raw_img.copy()  # img to transform in search for block
        img = img_copy.copy()  # img to display
        img_h, img_w = img_copy.shape[:2]
        
        # draw calibration overlay 
        cv2.line(img, (0, int(img_h / 2)), (img_w, int(img_h / 2)), (0, 0, 200), 1)
        cv2.line(img, (int(img_w / 2), 0), (int(img_w / 2), img_h), (0, 0, 200), 1)

        # resize, blur, and convert to lab colorspace
        frame_resize = cv2.resize(img_copy, self.size, interpolation=cv2.INTER_NEAREST)
        frame_gb = cv2.GaussianBlur(frame_resize, (11, 11), 11)
        frame_lab = cv2.cvtColor(frame_gb, cv2.COLOR_BGR2LAB)  # Convert image to LAB space

        areaMaxContour, area_max = (0,0)
        found_color = False
        for i in self.color_range:
            if i in self.__target_color:
                # mask color range for targeted color
                detect_color = i
                frame_mask = cv2.inRange(frame_lab, self.color_range[detect_color][0], self.color_range[detect_color][1])  # Perform bit operations on the original image and mask
                # process image to reduce noise and find contours
                opened = cv2.morphologyEx(frame_mask, cv2.MORPH_OPEN, np.ones((6, 6), np.uint8))  # Open operation
                closed = cv2.morphologyEx(opened, cv2.MORPH_CLOSE, np.ones((6, 6), np.uint8))  # Closed operation
                contours = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)[-2]  # Find the outline
                areaMaxContour, area_max = self.getAreaMaxContour(contours)  # Find the largest contour
                if area_max > 2500:
                    found_color = i
                    break  # found color, move on

        if area_max > 2500:  # Have found the largest area
            rect = cv2.minAreaRect(areaMaxContour)
            box = np.int0(cv2.boxPoints(rect))

            roi = getROI(box) # Get roi area
            get_roi = True

            img_centerx, img_centery = getCenter(rect, roi, self.size, square_length)  # Get the center coordinates of the block
            world_x, world_y = convertCoordinate(img_centerx, img_centery, self.size) # Convert to real world coordinates
            
            cv2.drawContours(img, [box], -1, self.range_rgb[detect_color], 2)
            cv2.putText(img, '(' + str(world_x) + ',' + str(world_y) + ')', (min(box[0, 0], box[2, 0]), box[2, 1] - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, self.range_rgb[detect_color], 1) # Draw center point
            world_angle = rect[2]
            loc = (world_x, world_y, world_angle)
        
        else:
            loc = False
        
        self.latest_display_img = img  # save image for display with overlays
        return loc, found_color


    def detect(self, target_color=None, print_loc=False):
        """ detect cube from camera
        
        optionally pass new target color, and print location
        """

        if target_color:  # if new target passed
            self.__target_color = target_color

        loc = self.findBlock()

        if print_loc:
            print('Found block at location: ', loc)
        return loc

    
    def display(self):
        """  display last image """

        cv2.imshow(self.window_name, self.latest_display_img)
        #waits for user to press any key 
        #(this is necessary to avoid Python kernel form crashing)
        key = cv2.waitKey(1)  # will show for 1ms
        return key


    def save(self):
        """  save last image 
        
        useful for streaming images in flask request in another thread
        uses window name to set filename 
        """

        cv2.imwrite(self.latest_display_img + '.jpg', self.latest_display_img)


    def see(self):
        """ find new frame, will return True if valid """

        img = self.camera.frame
        if img is None:
            return False
        
        self.latest_raw_img = img.copy()
        return True

    def close(self):
        """ shutdown gracefully """

        self.camera.camera_close()
        cv2.destroyAllWindows()

if __name__ == '__main__':
    # Identifies locations of a block and labels it in the camera video display

    eye = Perception()

    target_color = ('red', )
    eye.setTargetColor(target_color)

    while True:
        is_not_blind = eye.see()
        if is_not_blind:
            eye.detect()
            key = eye.display()
            # eye.save()
            if key == 27:  # ??
                break
    eye.close()
