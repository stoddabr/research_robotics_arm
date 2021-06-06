# modified from
#  https://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_gui/py_trackbar/py_trackbar.html
import cv2
import numpy as np
import params
from perception import Perception, label_scene

block_t = params.Perception.block_threshold
starfish_t = params.Perception.starfish_threshold

def nothing(x):
    pass

def main():
    global block_t, starfish_t

    cv2.namedWindow('image')

    perception_obj = Perception()

    # Make trackbars, with default values above
    cv2.createTrackbar('Block Threshold','image',block_t,255,nothing)
    cv2.createTrackbar('Starfish Threshold','image',starfish_t,255,nothing)
    print("Showing video. With the CV window in focus, press q to exit, p to pause.")
    while(1):

        # get current positions of trackbars
        block_t = cv2.getTrackbarPos('Block Threshold', 'image')
        starfish_t = cv2.getTrackbarPos('Starfish Threshold', 'image')
        
        perception_obj.block_t = block_t
        perception_obj.starfish_t = starfish_t

        scene = perception_obj.get_all_targets()
        img = perception_obj.frame
        img = label_scene(img, scene)
        if img is not None:
            cv2.imshow('image',img)
            key = cv2.waitKey(66)   # Delay for 66 ms
            if key == ord('q'): # Press q to exit, p to pause
                break
            if key == ord('p'):
                cv2.waitKey(-1) #wait until any key is pressed

    cv2.destroyAllWindows()

def detect_color(frame, lower, upper):
    lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
    mask = cv2.inRange(lab, lower, upper)
    return mask

if __name__=="__main__":
    main()