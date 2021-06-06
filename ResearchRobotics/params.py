"""
params.py

Global parameters for use in modules
"""

class Paw:
    closeAngle = 600

class Perception:
    color_ranges = { # HSV
        'red': [(0, 151, 100), (255, 255, 255)], 
        'green': [(0, 0, 0), (255, 122, 255)], 
        'blue': [(0, 0, 0), (255, 255, 122)], 
        }

    min_cnt_area = 100
    block_threshold = 47
    starfish_threshold = 6
    
    # HSV color ranges are below, but LAB work better.
    # color_ranges={
    #     'red': [(0, 151, 100), (80, 255, 230)], 
    #     'green': [(23, 52, 60), (87, 255, 255)], 
    #     'blue': [(90, 116, 0), (141, 255, 255)],
    # }