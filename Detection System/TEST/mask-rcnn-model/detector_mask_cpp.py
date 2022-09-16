from xml.dom.expatbuilder import parseString
import git
import os
import json

if not os.path.exists("Mask_RCNN"):
    print("Cloning M-RCNN repository...")
    git.Git("./").clone("https://github.com/matterport/Mask_RCNN.git")

import sys
# Root directory of the project
ROOT_DIR = os.path.abspath("Mask_RCNN/mrcnn/")

# Import Mask RCNN
sys.path.append(ROOT_DIR)  # To find local version of the library

import os
import subprocess
import time
import numpy as np
import cv2
import Mask_RCNN.mrcnn.config
import Mask_RCNN.mrcnn.utils
from Mask_RCNN.mrcnn.model import MaskRCNN
from pathlib import Path
from keras import backend as K
import pickle
import argparse

from shapely.geometry import box
from shapely.geometry import Polygon as shapely_poly
from shapely.geometry import Point as shapely_point
import io
import base64

class Config(Mask_RCNN.mrcnn.config.Config):
    NAME = "model_config"
    IMAGES_PER_GPU = 1
    GPU_COUNT = 1
    NUM_CLASSES = 81

config = Config()
config.display()

ROOT_DIR = os.getcwd()
MODEL_DIR = os.path.join(ROOT_DIR, "logs")
COCO_MODEL_PATH = os.path.join(ROOT_DIR, "mask_rcnn_coco.h5")

print(COCO_MODEL_PATH)
if not os.path.exists(COCO_MODEL_PATH):
    Mask_RCNN.mrcnn.utils.download_trained_weights(COCO_MODEL_PATH)

model = MaskRCNN(mode="inference", model_dir=MODEL_DIR, config=Config())
model.load_weights(COCO_MODEL_PATH, by_name=True)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('image_path', help="Image file")
    parser.add_argument('regions_path', help="Regions file", default="regions.p")
    args = parser.parse_args()
    
    regions = args.regions_path
    with open(regions, 'rb') as f:
        parked_car_boxes = pickle.load(f)

    IMAGE_SOURCE = args.image_path
    alpha = 0.6
    
    global frame
    frame=cv2.imread(IMAGE_SOURCE)
    rgb_image = frame[:, :, ::-1]
    start=time.time()
    results = model.detect([rgb_image], verbose=0)
    resmask = results[0]['masks'].astype(int)
    resclas= results[0]['class_ids']
    K.clear_session()
    with open("pytoc.json",'w') as file:
        json.dump({'masks':resmask.tolist(),'class_ids':resclas.tolist(),'parking':parked_car_boxes},file)
    exit()


