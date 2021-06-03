import time
import os
from flask import Flask, send_file, request
from markupsafe import escape
import json
import random
import db_txt as db
   



def reset():
    default_grasp_data = [0,0,False]  # [angle, object_coords, is_grasp]
    default_blobs_data = [  # TODO double check format
        {'x': '50','y': '50', 'angle': '270', 'color': 'orange', 'type':'starfish'},
        {'x': '200','y': '200', 'angle': '270', 'color': 'orange', 'type':'cube'},
    ]
    db.updateGraspDB(default_grasp_data)
    db.updateBlockDB(default_blobs_data)


# test code
def run_testing_thread():
    """ will run thread that updates data every 5 seconds """
    import threading  # only used for testing

    blobsA = [  # TODO double check format
        {'x': '10','y': '10', 'angle': '270', 'color': 'orange', 'type':'cube'},
        {'x': '200','y': '150', 'angle': '60', 'color': 'yellow', 'type':'cube'},

    ]
    blobsB = [  # TODO double check format
        {'x': '50','y': '50', 'angle': '270', 'color': 'orange', 'type':'starfish'},
        {'x': '100','y': '100', 'angle': '60', 'color': 'yellow', 'type':'starfish'},
    ]
    
    def loopWriteToDB():
        fname = 'db_blobs.txt'
        while True:
            updateBlockDB(blobsA)
            time.sleep(5)

            updateBlockDB(blobsB)
            time.sleep(5)            

    test_io_thread = threading.Thread(target = loopWriteToDB)
    test_io_thread.start()


# setup flask server and routes
app = Flask(__name__)

@app.route('/grasp', methods=['GET', 'POST'])
def grasp_request():
    if request.method == 'POST':
        data = request.grasp
        return db.updateGraspDB(data)
    else:   # GET
        return json.dumps(db.getGraspDB())


@app.route('/blobs', methods=['GET', 'POST'])
def blobs_request():
    if request.method == 'POST':
        data = request.grasp
        return db.updateBlockDB(data)
    else:   # GET
        return json.dumps(db.getBlocksDB())


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
