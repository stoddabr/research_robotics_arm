"""
final_project.py

script for the final project logic main loop
"""

import sys
import numpy as np
sys.path.append('/home/pi/ArmPi/')
from paw_class import Paw
from perception import Perception, show_image, label_scene
import numpy as np
from ArmIK.Transform import getAngle
import db_txt as db




if __name__ == '__main__':
    count = 0
    
    perception_obj = Perception()
    paw_obj = Paw()
    final_pos = (-15 + 0.5, 12 - 0.5, 1.5)  # x block home

    while True:
        # perception code
        count = count + 1
        #perception_obj.get_frame()
        scene = perception_obj.get_all_targets()
        img = perception_obj.frame
        img = label_scene(img, scene)
        if img is not None:
            print(scene)
            show_image(img)

        # arm code
        graspInfo = db.getGraspDB()
        if 'x' in graspInfo:  # if grasp info updated
            # pick up object from set position
            x_pos = graspInfo['x']
            y_pos = graspInfo['y']
            a_pos = graspInfo['angle']
            print("Grabbing!")
            paw_obj.grabAtXY(x_pos,y_pos,a_pos)

            # place block at set coord
            print("Placing!")
            paw_obj.placeAtXY(*final_pos)

            # reset paw db
            db.clearGraspDB()
        
                
    perception_obj.my_camera.camera_close()
    cv2.destroyAllWindows()

