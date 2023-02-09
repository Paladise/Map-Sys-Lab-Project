import cv2 as cv
from colorsys import hls_to_rgb
from PIL import Image
from random import random

from utils.drawing import draw_square, draw_boxes

def get_bounding_boxes(filename, max_height):

    print("Drawing boxes...")
    
    BETA = False

    if BETA:
        tresh_min, tresh_max = 128, 255
        cv_image = cv.imread(filename)
        im_bw = cv.cvtColor(cv_image, cv.COLOR_RGB2GRAY)
        (thresh, im_bw) = cv.threshold(im_bw, tresh_min, tresh_max, 0)
        contours, hierarchy = cv.findContours(im_bw, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)

        # Find contours, obtain bounding box
        boxes_image = Image.open(filename)
        boxes_pixels = boxes_image.load()
        boxes = set()
        for c in contours:
            x,y,w,h = cv.boundingRect(c)
            if  w < max_height and h > 3 and h < max_height:
                hasdf,s,l = random(), 0.5 + random()/2.0, 0.4 + random()/5.0
                rgb = tuple([int(256*i) for i in hls_to_rgb(hasdf,l,s)]) 
                draw_square(boxes_pixels, x, x + w, y, y + h, rgb)
                boxes.add((x, x + w, y, y + h))
        boxes = sorted(list(boxes), key = lambda b: (b[0], b[3]))
    else:
        boxes_image, boxes = draw_boxes(Image.open(filename), max_height) 
    
    return boxes, boxes_image