from xml.dom.expatbuilder import parseString
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

def get_cars(boxes, class_ids):
    global overlay2, rx, ry, rob
    rx = len(boxes)
    ry = len(boxes[0])
    rob = len(boxes[0][0])
    cars = [set() for _ in range(rob)]
    objects = []
    #import pdb; pdb.set_trace()
    for i in range(rob):
        if class_ids[i] in [3,8,6]:
            objects.append(i)
    for x in range(rx):
        for y in range(ry):
            for ob in objects:
                if boxes[x][y][ob]:
                    cars[ob].add((x,y))
                    overlay2[x][y]=(255,0,0)
    #import pdb; pdb.set_trace()
    return cars

def compute_overlaps(parked_car_boxes, car_boxes): 
    overlaps = np.zeros((len(parked_car_boxes), len(car_boxes)))#to put the IoU
    for i in range(len(parked_car_boxes)):
        #convert polygon to mask
        mask_s = set()
        poly = shapely_poly(parked_car_boxes[i])
        for x in range(rx):
            for y in range(ry):
                #we now check
                p = shapely_point(y,x)
                if p.within(poly):
                    mask_s.add((x,y))
        print(str(i)+","+str(len(mask_s)))
        """global frame
        ov=frame.copy()
        for x,y in mask_s:
            ov[x][y]=(255,0,0)
        frame2=frame.copy()
        frame2=cv2.addWeighted(ov, 0.6, frame, 0.4, 0, frame2)
        cv2.imshow('output', frame2)
        cv2.waitKey(0)
        cv2.destroyAllWindows()"""
        for j in range(len(car_boxes)):
            if not (len(mask_s) or len(car_boxes[j])): continue
            inter=mask_s & car_boxes[j]
            uni=mask_s | car_boxes[j]
            
            """for x,y in car_boxes[j]:
                ov[x][y]=(0,255,0)
            for x,y in inter:
                ov[x][y]=(0,0,255)"""
            overlaps[i][j] = len(inter)/len(uni)
    return overlaps


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
    global overlay,overlay2
    overlay=frame.copy()
    overlay2=frame.copy()
    rgb_image = frame[:, :, ::-1]

    start=time.time()
    results = model.detect([rgb_image], verbose=0)
    cars = get_cars(results[0]['masks'].astype(int), results[0]['class_ids'])
    overlaps = compute_overlaps(parked_car_boxes, cars)
    end=time.time()
    print("Time in computation: "+str(end-start))

    for parking_area, overlap_areas in zip(parked_car_boxes, overlaps):
        if len(overlap_areas)==0 or np.max(overlap_areas) < 0.15:
            cv2.fillPoly(overlay, [np.array(parking_area)], (71, 27, 92))
            free_space = True      
    frame=cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)
    frame=cv2.addWeighted(overlay2, 0.4, frame, 0.6, 0, frame)

    cv2.imshow('output', frame)
    cv2.waitKey(0)
    cv2.imwrite('out.png',frame)
    cv2.destroyAllWindows()
    print("output saved as out.png")

