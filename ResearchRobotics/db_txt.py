import json
from cv2 import imwrite

# db io functions
db_address_blobs = '_blobs.txt'
db_address_grasp = '_grasp.txt'
db_address_img = '_scene.jpg'

# io helpers
def updateDB(data, file):
    with open(file, 'w') as outfile:
        json.dump(data, outfile)

def updateDBTxt(data, file):
    with open(file, 'w') as outfile:
        outfile.write(data)

def getDB(file):
    with open(file) as json_file:
        return json.load(json_file)


def updateDBImg(frame):
    imwrite(db_address_img,frame)


# helper functions
# TODO validation
def updateBlockDB(data):
    updateDB(data, db_address_blobs)


def getBlocksDB():
    return getDB(db_address_blobs)


def updateGraspDB(data, as_text=False):
    if as_text:
        updateDBTxt(data, db_address_grasp)
    else:
        updateDB(data, db_address_grasp)


def getGraspDB():
    return getDB(db_address_grasp)


def clearGraspDB():
    data = {'grasp':'reset'}
    updateDB(data, db_address_grasp)

