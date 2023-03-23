import cv2 as cv
import numpy as np
from skimage.measure import approximate_polygon, find_contours

def get_rectangles(img):
    """
    Get rectangles of potential walls in the image by using approximate_polygons()
    """
    
    img = np.array(img.convert('L')) # Convert to opencv format
    contours = find_contours(img) # Find contours in image
    rectangles = []

    for contour in contours:
        # increase tolerance to further reduce number of lines
        polygon = approximate_polygon(contour, tolerance=4)

        polygon = polygon.astype(np.int).tolist()

        # draw polygon 2 lines
        for idx, coords in enumerate(polygon[:-1]):
            y1, x1, y2, x2 = coords + polygon[idx + 1]
            rectangles.append([x1, y1, x1, y2, x2 - x1])
            
    return rectangles