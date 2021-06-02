import time
import os
from flask import Flask, send_file, request
from markupsafe import escape
import json
import random

   
# io helpers
def updateDB(data, file):
    with open(file, 'w') as outfile:
        json.dump(data, outfile)

def getDB(file):
    with open(file) as json_file:
        return json.load(json_file)

# db io functions
# TODO datastructure validation
db_address_blocks = '_blocks.txt'
db_address_grasp = '_grasp.txt'
def updateBlockDB(data):
    updateDB(data, db_address_blocks)

def updateGraspDB(data):
    updateDB(data, db_address_grasp)

def getBlocksDB():
    return getDB(db_address_blocks)

def getGraspDB():
    return getDB(db_address_grasp)


def reset():
    default_grasp_data = [0,0,False]  # [angle, object_coords, is_grasp]
    default_blocks_data = [  # TODO double check format
        {'x': 10,'y': 10,'type':'cube'},
    ]
    updateGraspDB(default_grasp_data)
    updateBlockDB(default_blocks_data)


# test code
def run_testing_thread():
    """ will run thread that updates data every 5 seconds """
    import threading  # only used for testing

    blocksA = [  # TODO double check format
        {'x': 10,'y': 10, 'angle': 30, 'color': 'blue', 'type':'cube'},
        {'x': 100,'y': 100, 'angle': 60, 'color': 'blue', 'type':'cube'},

    ]
    blocksB = [  # TODO double check format
        {'x': 10,'y': 10, 'angle': 270, 'color': 'orange', 'type':'starfish'},
        {'x': 100,'y': 100, 'angle': 60, 'color': 'yellow', 'type':'starfish'},
    ]
    
    def loopWriteToDB():
        fname = 'db_blocks.txt'
        while True:
            updateBlockDB(blocksA)
            time.sleep(5)

            updateBlockDB(blocksB)
            time.sleep(5)            

    test_io_thread = threading.Thread(target = loopWriteToDB)
    test_io_thread.start()


# setup flask server and routes
app = Flask(__name__)

@app.route('/grasp', methods=['GET', 'POST'])
def grasp_request():
    if request.method == 'POST':
        data = request.grasp
        return updateGraspDB(data)
    else:   # GET
        return json.dumps(getGraspDB())


@app.route('/blocks', methods=['GET', 'POST'])
def blocks_request():
    if request.method == 'POST':
        data = request.grasp
        return updateBlockDB(data)
    else:   # GET
        return json.dumps(getBlocksDB())


@app.route('/video_feed')
def video_feed():
    fpath = '_scene.jpg'
    return send_file(fpath, mimetype='image/jpg')


@app.route('/video_feed_test')
def video_feed_test():
    test_img_paths = ['_testA.jpg', '_testB.jpg']
    fpath = random.choice( test_img_paths ) 
    return send_file(fpath, mimetype='image/jpg')


if __name__ == '__main__':
    reset()  # reset data in 'server'
    #run_testing_thread()  # comment this line during production
    app.run()
