# modified from
#  https://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_gui/py_trackbar/py_trackbar.html
import cv2
import numpy as np

colors = { #LAB
    'red': [(0, 151, 100), (255, 255, 255)], 
    'green': [(0, 0, 0), (255, 122, 255)], 
    'blue': [(0, 0, 0), (255, 255, 122)], 
    }

def nothing(x):
    pass

def main():
    cap = cv2.VideoCapture(0)
    # cap =cv2.VideoCapture('/home/tim/wacky_lighting.avi')
    cv2.namedWindow('image')
    cv2.namedWindow('mask')

    c = 'green'
    lower = np.array(colors[c][0])
    upper = np.array(colors[c][1])

    # Make trackbars, with default values above
    cv2.createTrackbar('L_lower','image',lower[0],255,nothing)
    cv2.createTrackbar('L_upper','image',upper[0],255,nothing)
    cv2.createTrackbar('A_lower','image',lower[1],255,nothing)
    cv2.createTrackbar('A_upper','image',upper[1],255,nothing)
    cv2.createTrackbar('B_lower','image',lower[2],255,nothing)
    cv2.createTrackbar('B_upper','image',upper[2],255,nothing)
    print("Showing video. With the CV window in focus, press q to exit, p to pause.")
    while(1):
        ret, img = cap.read()
        if not ret: break
        # get current positions of four trackbars
        lower[0] = cv2.getTrackbarPos('L_lower', 'image')
        lower[1] = cv2.getTrackbarPos('A_lower', 'image')
        lower[2] = cv2.getTrackbarPos('B_lower', 'image')
        upper[0] = cv2.getTrackbarPos('L_upper', 'image')
        upper[1] = cv2.getTrackbarPos('A_upper', 'image')
        upper[2] = cv2.getTrackbarPos('B_upper', 'image')
        # Create mask by thresholding LAB image
        mask = detect_color(img, lower, upper)
        cv2.imshow('image',img)
        cv2.imshow('mask', mask)
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