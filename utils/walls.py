import cv2 as cv
import numpy as np
from skimage.measure import approximate_polygon, find_contours
from PIL import Image

def get_rectangles(img, WIDTH, HEIGHT, rooms):
    """
    Get rectangles of potential walls in the image by using approximate_polygons()
    """
    
    img = np.array(img.convert('L')) # Convert to opencv format
    contours = find_contours(img) # Find contours in image
    rectangles = []
    
    map = np.full((HEIGHT, WIDTH, 3), 255, dtype=np.uint8)

    for contour in contours:
        # increase tolerance to further reduce number of lines
        polygon = approximate_polygon(contour, tolerance=3)

        polygon = polygon.astype(np.int).tolist()

        # draw polygon 2 lines
        for idx, coords in enumerate(polygon[:-1]):
            y1, x1, y2, x2 = coords + polygon[idx + 1]
            rectangles.append([x1, y1, x1, y2, x2 - x1])
            
            y = (y1, y2)
            x = (x1, x2)
            
            y1, y2 = min(y), max(y)
            x1, x2 = min(x), max(x)
                          
            map[y1:y2 + 1,x1:x2 + 1] = [0, 0, 0]
            
    img = Image.fromarray(map, 'RGB')
    img.save('new map.png')
                    
            
    return rectangles, img