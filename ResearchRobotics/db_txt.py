import json

# io helpers
def updateDB(data, file):
    with open(file, 'w') as outfile:
        json.dump(data, outfile)

def getDB(file):
    with open(file) as json_file:
        return json.load(json_file)

# db io functions
# TODO datastructure validation
db_address_blobs = '_blobs.txt'
db_address_grasp = '_grasp.txt'

# helper functions
def updateBlockDB(data):
    updateDB(data, db_address_blobs)

def updateGraspDB(data):
    updateDB(data, db_address_grasp)

def getBlocksDB():
    return getDB(db_address_blobs)

def getGraspDB():
    return getDB(db_address_grasp)