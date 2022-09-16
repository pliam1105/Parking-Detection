import os
import sys
import time
import numpy as np
import cv2
from pathlib import Path
import pickle
import argparse
import torch
#import tensorflow as tf
from shapely.geometry import box
from shapely.geometry import Polygon as shapely_poly
import io
import base64

#MODEL INITIALIZATION
model = torch.hub.load('ultralytics/yolov5', 'yolov5x6')
#model.conf = 0.25  # confidence threshold (0-1)
#model.iou = 0.45  # NMS IoU threshold (0-1)
model.classes = [2,5,7]  # (optional list) filter by class, i.e. = [0, 15, 16] for persons, cats and dogs

def get_cars(boxes):
    global overlay
    cars = []
    for i, box in enumerate(boxes):
        x1 = box[0]
        y1 = box[1]
        x2 = box[2]
        y2 = box[3]
        p1 = (x1, y1)
        p2 = (x2, y1)
        p3 = (x2, y2)
        p4 = (x1, y2)
        cv2.polylines(overlay,np.int32([np.array([p1,p2,p3,p4])]),True,(255,0,0),1)
        cars.append([p1,p2,p3,p4])
    return np.array(cars)

def compute_overlaps(parked_car_boxes, car_boxes):
    new_car_boxes = []
    for box in car_boxes:
        cv2.polylines(overlay,np.int32([np.array(box)]),True,(255,0,0),1)
    
    overlaps = np.zeros((len(parked_car_boxes), len(car_boxes)))
    for i in range(len(parked_car_boxes)):
        for j in range(len(car_boxes)):
            pol1_xy = parked_car_boxes[i]
            pol2_xy = car_boxes[j]
            polygon1_shape = shapely_poly(pol1_xy)
            polygon2_shape = shapely_poly(pol2_xy)

            polygon_intersection = polygon1_shape.intersection(polygon2_shape).area
            polygon_union = polygon1_shape.union(polygon2_shape).area
            IOU = polygon_intersection / polygon_union
            overlaps[i][j] = IOU
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
    
    frame=cv2.imread(IMAGE_SOURCE)
    global overlay
    overlay=frame.copy()
    rgb_image = frame[:, :, ::-1]
    start=time.time()
    results = model([rgb_image],augment=True)
    end=time.time()
    print("Time in computation: "+str(end-start))
    #import pdb; pdb.set_trace()
    cars = get_cars(results.xyxy[0][:,0:4])
    overlaps = compute_overlaps(parked_car_boxes, cars)

    for parking_area, overlap_areas in zip(parked_car_boxes, overlaps):
        if len(overlap_areas)==0 or np.max(overlap_areas) < 0.15:
            cv2.fillPoly(overlay, [np.array(parking_area)], (71, 27, 92))
            free_space = True      
    frame=cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)

    cv2.imshow('output', frame)
    cv2.waitKey(0)
    cv2.imwrite('out.png',frame)
    cv2.destroyAllWindows()
    print("output saved as out.png")

