import git
import os

if not os.path.exists("Mask_RCNN"):
    print("Cloning M-RCNN repository...")
    git.Git("./").clone("https://github.com/matterport/Mask_RCNN.git")

import sys
# Root directory of the project
ROOT_DIR = os.path.abspath("Mask_RCNN/mrcnn/")

# Import Mask RCNN
sys.path.append(ROOT_DIR)  # To find local version of the library

import time
import numpy as np
import cv2
import Mask_RCNN.mrcnn.config
import Mask_RCNN.mrcnn.utils
from Mask_RCNN.mrcnn.model import MaskRCNN
from pathlib import Path
import pickle
import argparse
import json
import requests
from shapely.geometry import box
from shapely.geometry import Polygon as shapely_poly
import io
import base64

class Config(Mask_RCNN.mrcnn.config.Config):
    NAME = "model_config"
    IMAGES_PER_GPU = 1
    GPU_COUNT = 1
    NUM_CLASSES = 81

config = Config()
config.display()
PARKING_ID=1
ROOT_DIR = os.getcwd()
MODEL_DIR = os.path.join(ROOT_DIR, "logs")
COCO_MODEL_PATH = os.path.join(ROOT_DIR, "mask_rcnn_coco.h5")

print(COCO_MODEL_PATH)
if not os.path.exists(COCO_MODEL_PATH):
    Mask_RCNN.mrcnn.utils.download_trained_weights(COCO_MODEL_PATH)

model = MaskRCNN(mode="inference", model_dir=MODEL_DIR, config=Config())
model.load_weights(COCO_MODEL_PATH, by_name=True)

def filter_boxes(boxes, class_ids):
    global overlay
    cars = []
    for i, box in enumerate(boxes):
        y1 = box[0]
        x1 = box[1]
        y2 = box[2]
        x2 = box[3]
        p1 = (x1, y1)
        p2 = (x2, y1)
        p3 = (x2, y2)
        p4 = (x1, y2)
        #cv2.polylines(overlay,np.int32([np.array([p1,p2,p3,p4])]),True,(255,0,0),1)
        #cv2.putText(overlay,str(class_ids[i]),p4,cv2.FONT_HERSHEY_SIMPLEX,0.5,(255,0,0),1,2,)
        if class_ids[i] in [3, 8, 6]:
            cars.append([p1,p2,p3,p4])
    return np.array(cars)

def intersection_compute(parking_spaces, car_boxes):    
    for i in range(len(parking_spaces)):
        free_space=True
        for j in range(len(car_boxes)):
            polyspace = parking_spaces[i]
            polycar = car_boxes[j]
            polygonspace = shapely_poly(polyspace)
            polygoncar = shapely_poly(polycar)
            poly_inter = polygonspace.intersection(polygoncar).area
            poly_uni = polygonspace.union(polygoncar).area
            IOU = poly_inter / poly_uni
            if(IOU>=0.15): free_space=False
        free.append(free_space)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('image_path', help="Image file")
    parser.add_argument('regions_path', help="Regions file", default="regions.p")
    args = parser.parse_args()
    
    regions = args.regions_path
    with open(regions, 'rb') as f:
        parking_spaces = pickle.load(f)

    IMAGE_SOURCE = args.image_path
    alpha = 0.6
    #cap=cv2.VideoCapture(0)#READ FROM CAMERA
    #ret,frame = cap.read()
    try:
        while True:
            frame=cv2.imread(IMAGE_SOURCE)
            global overlay
            #overlay=frame.copy()
            rgb_image = frame[:, :, ::-1]
            #start=time.time()
            results = model.detect([rgb_image], verbose=0)
            #end=time.time()
            #print("Time in computation: "+str(end-start))
            cars = filter_boxes(results[0]['rois'], results[0]['class_ids'])
            global free
            free=[PARKING_ID]
            intersection_compute(parking_spaces, cars)
            #now we want to put this to our database
            jsonData = json.dumps(free)
            #import pdb; pdb.set_trace()
            newHeaders = {'Content-type': 'application/json'}
            response = requests.post('https://pliamprojects.000webhostapp.com/parking/upload_data.php',data=jsonData,headers=newHeaders)
            print(response.status_code)
            print(response.content)
            #frame=cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)
            
            #cv2.imshow('output', frame)
            #cv2.waitKey(0)
            #cv2.imwrite('out.png',frame)
            #cv2.destroyAllWindows()
            #print("output saved as out.png")
    except KeyboardInterrupt:
        pass
