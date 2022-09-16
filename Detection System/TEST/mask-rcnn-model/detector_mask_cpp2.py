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
from pathlib import Path
import pickle
import argparse

from shapely.geometry import box
from shapely.geometry import Polygon as shapely_poly
from shapely.geometry import Point as shapely_point
import io
import base64


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('image_path', help="Image file")
    parser.add_argument('regions_path', help="Regions file", default="regions.p")
    args = parser.parse_args()

    IMAGE_SOURCE = args.image_path
    alpha = 0.6
    
    global frame,overlay
    frame=cv2.imread(IMAGE_SOURCE)
    overlay=frame.copy()
    
    regions = args.regions_path
    with open(regions, 'rb') as f:
        parked_car_boxes = pickle.load(f)
    with open("ctopy.json",'w') as file:
        overlaps=json.load(file)


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
