import cv2 as cv
from colorsys import hls_to_rgb
from PIL import Image
from random import random

try:
    from utils.drawing import draw_square, draw_boxes
except:
    from drawing import draw_square, draw_boxes

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

def get_bounding_boxes(filename, max_height, min_height):
    """
    Original flood-fill method for determining bounding boxes
    """
    boxes_image, boxes = draw_boxes(Image.open(filename), max_height) 
    
    return boxes, boxes_image

def rectangle_overlap(a, b):
    """
    Check if two rectangles overlap so redundant bounding boxes are not detected
    """

    ax1, ax2, orig_ay1, orig_ay2 = a
    bx1, bx2, orig_by1, orig_by2 = b
    
    # Expand boundaries for smarter detection
    
    ax1 -= 3
    ax2 += 3
    ay1 = (orig_ay1 + orig_ay2) / 2 - 4
    ay2 = (orig_ay1 + orig_ay2) / 2 + 4
    by1 = (orig_by1 + orig_by2) / 2 - 4
    by2 = (orig_by1 + orig_by2) / 2 + 4
    
    if ax1 <= bx2 and ax2 >= bx1 and ay1 <= by2 and ay2 >= by1:
        return True # Overlaps
    else:
        return False # Do not overlap
    
def clear_perimeter(boxes_pixels, b):
    """
    Check if a bounding box is surrounded by white pixels    
    """
    
    x1, x2, y1, y2 = b[0] - 1, b[1] + 1, b[2] - 1, b[3] + 1 # Add padding beforehand
    
    for x in range(x1, x2 + 1):
        if boxes_pixels[x, y1] != WHITE or boxes_pixels[x, y2] != WHITE:
            return False

    for y in range(y1, y2 + 1):
        if boxes_pixels[x1, y] != WHITE or boxes_pixels[x2, y] != WHITE:
            return False
        
    return True 

def check_interior(pixels, x1, x2, y1, y2):
    """
    Check if the interior of a bounding box is also made up of pixels, in other words,
    check if there are some pixels inside the bounding boxes that are not immediately next to the perimeter
    """
    
    return any(pixels[x, y] == BLACK for x in range(x1 + 2, x2 - 1) for y in range(y1 + 2, y2 - 1))
            
def get_bounding_boxes_opencv(filename, max_height = 22, min_height = 9):
    """
    Determine bounding boxes using opencv findContours() method
    """
    
    tresh_min, tresh_max = 128, 255
    cv_image = cv.imread(filename)
    im_bw = cv.cvtColor(cv_image, cv.COLOR_RGB2GRAY)
    (thresh, im_bw) = cv.threshold(im_bw, tresh_min, tresh_max, 0)
    contours, hierarchy = cv.findContours(im_bw, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
    
    # Get initial boxes of correct size
    boxes_image = Image.open(filename)
    boxes_pixels = boxes_image.load()
    boxes = []
    indices = []
    for index, c in enumerate(contours):
        x,y,w,h = cv.boundingRect(c)
        if  h >= min_height and h <= max_height and w > 1:
            if w <= 4 or h <= 4 or check_interior(boxes_pixels, x, x + w, y, y + h):
                boxes.append((x, x + w, y, y + h))
                indices.append(index)
    
      # Debugging
#     for b in boxes:
#         x1, x2, y1, y2 = b
#         hasdf,s,l = random(), 0.5 + random()/2.0, 0.4 + random()/5.0
#         rgb = tuple([int(256*i) for i in hls_to_rgb(hasdf,l,s)]) 
#         draw_square(boxes_pixels, x1, x2, y1, y2, rgb)
        
#     return boxes, boxes_image
    
    # Remove redundant bounding boxes
    new_boxes = []
    removeable = set()
    for i1, b1 in enumerate(boxes):
        if any(rectangle_overlap(b1, b2) for b2 in boxes if b1 != b2) or clear_perimeter(boxes_pixels, b1):
        
            # Mark a box as a bounding box only if it "overlaps" another box 
            # (i.e. part of same room name)
            # Or since a box may contain a full word, mark it if it is surrounded
            # by blank pixels, since will be in center of room
        
            children = [b2 for i2, b2 in enumerate(boxes) if hierarchy[0,indices[i2],3] == indices[i1]]
            if len(children) > 1:
                continue
            elif len(children) == 1:
                child = children[0]
                removeable.add(child)
            new_boxes.append(b1)
            
    boxes = []    
    for b1 in new_boxes:
        if b1 in removeable:
            continue            
        if any(rectangle_overlap(b1, b2) for b2 in new_boxes if b1 != b2 and b2 not in removeable) or clear_perimeter(boxes_pixels, b1):
            boxes.append(b1)        
            x1, x2, y1, y2 = b1

            # Draw box on image
            hasdf,s,l = random(), 0.5 + random()/2.0, 0.4 + random()/5.0
            rgb = tuple([int(256*i) for i in hls_to_rgb(hasdf,l,s)]) 
            draw_square(boxes_pixels, x1, x2, y1, y2, rgb)
            
    boxes = sorted(list(boxes), key = lambda b: (b[0], b[3]))
            
    return boxes, boxes_image


if __name__ == "__main__":
    filename = "debug_images/black_and_white_floor1.png"
    filename = "debug_images/test_bounding2.png"
    _, image = get_bounding_boxes_opencv(filename)
    image.save("debug_results/bounding_boxes.png")