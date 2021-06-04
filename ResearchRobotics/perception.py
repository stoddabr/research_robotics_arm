#!/usr/bin/env python3
import sys
import numpy as np
sys.path.append('/home/pi/ArmPi/')
import cv2
import time
import Camera
from math import log10
import params

DEBUG = False

class Perception:
    def __init__(self):
        #start capturing from camera
        self.my_camera = Camera.Camera()
        self.my_camera.camera_open()
        
        #always store current scene
        self.frame = None
        
        #define the shape of a block vs starfish
        self.block_shape_logscale = np.array([ 0.7827677 ,  5.01251839,  6.19969677,  7.33014752, 14.1640971, 10.04483551, 14.37753618])
        self.starfish_shape_logscale = np.array([0.64055716, 3.97346808, 4.47200431, 4.85410399, 9.66857547, 6.9555887 , 9.66677454])
        
        #define bounds for classification
        self.block_t = params.Perception.block_threshold
        self.starfish_t = params.Perception.starfish_threshold

        #define color ranges for thresholding
        self.color_ranges = params.Perception.color_ranges

    #update function for image of scene
    def get_frame(self):
        self.frame = self.my_camera.frame
    
    #converts humoments to logarithmic representation for comparison
    def to_logscale(self, moment):
        logscale = 7*[None]
        for i in range(0,7):
            if moment[i] != 0:
                logscale[i] =  log10(abs(moment[i]))
            else:
                logscale[i] = 0
                
        return abs(np.array(logscale))        
    
    #given an image, return processed binary image that contains only regions of the specified color
    def color_threshold(self, color, img):
        if DEBUG: show_image(img.copy(), 'img_prethreshold')
        #convert to LAB
        lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
        #mask image for the target color
        frame_mask = cv2.inRange(lab, self.color_ranges[color][0], self.color_ranges[color][1])
        if DEBUG: show_image(frame_mask.copy(), 'frame_mask_premorph')
        #smooth the image (erosion -> dilation -> dilation -> erosion)
        opened = cv2.morphologyEx(frame_mask, cv2.MORPH_OPEN, np.ones((6, 6), np.uint8)) 
        closed = cv2.morphologyEx(opened, cv2.MORPH_CLOSE, np.ones((6, 6), np.uint8))  
        #return the procesed image
        return closed
    
    #dumb function that makes getting cv2 contours less cumbersome by storing some settings
    def get_contours(self, img):
        contours = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)[-2]
        return contours
    
    #given the contours in a scene, return the hu moments of those contours
    def get_moments(self, contours):
        huMoments = []

        for i in range(len(contours)):
            # Calculate Moments 
            moments = cv2.moments(contours[i])
            # Calculate Hu Moments
            huMoments.append(cv2.HuMoments(moments))
        return huMoments
    
    # checks to see if a moment is L2-near enough to the platonic ideal of "box"
    def is_block(self, moment):
        shape_diff = abs(self.to_logscale(moment) - self.block_shape_logscale)
        if (shape_diff**2).sum() < self.block_t:
            return True
        else:
            return False

    # checks to see if a moment is L2-near enough to the platonic ideal of "starfish"        
    def is_starfish(self, moment):
        shape_diff = abs(self.to_logscale(moment) - self.starfish_shape_logscale)
        if (shape_diff**2).sum() < self.starfish_t:
            return True
        else:
            return False

    #finds all block and starfish blobs of one color
    def find_targets(self, image, color):
        blobs = []
        #copy the image so as not to overwrite self.frame
        processing_frame = image.copy()
        #smooth image 
        frame_gb = cv2.GaussianBlur(processing_frame, (11, 11), 11)
        #threshold to single color
        frame_mono = self.color_threshold(color, frame_gb)
        if DEBUG: show_image(frame_mono.copy(), 'frame_mono')
        #find contours and hu moments
        canny_output = cv2.Canny(frame_mono, 128, 255)
        if DEBUG: show_image(canny_output, 'canny_output')
        contours = self.get_contours(canny_output)
        contours = list(filter(
            lambda c: cv2.contourArea(c) > params.Perception.min_cnt_area,
            contours))
        hu_moments = self.get_moments(contours)
    
        if DEBUG:
            img_contours = image.copy()
            cv2.drawContours(img_contours, contours, -1, (0,255,0), 3)               
            show_image(img_contours)

        #for every found contour
        count = 0
        for cnt in contours:
            M = cv2.moments(cnt)
            if M['m00'] != 0:
                #find the location
                cx = int(M['m10']/M['m00'])
                cy = int(M['m01']/M['m00'])
                #classify blob and store as dictionary
                if self.is_block(hu_moments[count]):
                    rect = cv2.minAreaRect(cnt)
                    block_blob = {'x': cx, 'y': cy, 'color': color, 'type': 'block', 'angle': rect[2]}
                    blobs.append(block_blob)
                if self.is_starfish(hu_moments[count]) and color=='blue':
                    starfish_blob = {'x': cx, 'y': cy, 'color': color, 'type': 'starfish', 'angle': 0}
                    blobs.append(starfish_blob)
            count = count + 1
        
        return blobs

    #main function that updates the frame and returns all targets in scene
    def get_all_targets(self):
        #update image from camera
        self.get_frame()
        
        scene = []
        
        #check for empty image error
        if self.frame is not None:
            #find all blobs for each color
            for color in ['red', 'green', 'blue']:
                blobs = self.find_targets(self.frame, color)
                scene.extend(blobs)
            
        return scene
    
def label_scene(display_frame, scene):
    for obj in scene:
        display_frame = cv2.putText(display_frame, ". " + obj['type'] + " (" + obj['color'] + ")", (obj['x'], obj['y']), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 2, cv2.LINE_AA)
    return display_frame
        
def show_image(img, name='img'):
    cv2.imshow(name, img)
    key = cv2.waitKey(1)
    if key == 27:
        return

if __name__ == '__main__':
    count = 0
    perception_obj = Perception()
    while True:
        count = count + 1
        print()
        #perception_obj.get_frame()
        scene = perception_obj.get_all_targets()
        img = perception_obj.frame
        img = label_scene(img, scene)
        if img is not None:
            print(scene)
            show_image(img)
                
    perception_obj.my_camera.camera_close()
    cv2.destroyAllWindows()
