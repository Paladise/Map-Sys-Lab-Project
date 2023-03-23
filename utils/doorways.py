from utils.drawing import remove_box

DIRECTIONS = [(-1, 0), (1, 0), (-1, 1), (1, 1)]
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

def rectangle_overlap(a, b):
    """
    Check if two rectangles overlap 
    """
    
    ax1, ax2, ay1, ay2 = a
    bx1, bx2, by1, by2 = b
    
    if ax1 <= bx2 and ax2 >= bx1 and ay1 <= by2 and ay2 >= by1:
        return True # Overlaps
    else:
        return False # Do not overlap

def get_doorways(image, rooms):
    """
    Takes a PIL image of the blank map as well as list of bounding boxes for actual rooms and
    removes walls to create doorways to those rooms
    """
    
    width, height = image.size[0], image.size[1]
    
    def ins(p):
        x, y = tuple(p)
        if x >= 0 and x < width and y >= 0 and y < height:
            return True
        else:
            return False
    
    rooms = [list(r) for r in rooms] # temporary solution
    
    pixels = image.load()
    
    # Expand boxes to roughly enclose full room    
    for room in rooms:
        x1, x2, y1, y2 = room
        center_x, center_y = (x1 + x2) // 2, (y1 + y2) // 2
        
        for i, val in enumerate(DIRECTIONS):
            d, j = val
            if i <= 1:
                x, y = room[i], center_y
            else:
                x, y = center_x, room[i]
            point = [x, y]
            while ins(point) and pixels[point[0], point[1]] == WHITE:
                point[j] += d
                
            room[i] = point[j]
                
    # Get non-intersections when expanding room boundaries beyond on their walls   
    for r in rooms:
        room = r[:]
        x1, x2, y1, y2 = room
        center_x, center_y = (x1 + x2) // 2, (y1 + y2) // 2
        for i, val in enumerate(DIRECTIONS): # Expand in each direction
            d, j = val
            if i <= 1:
                x, y = room[i], center_y
            else:
                x, y = center_x, room[i]
            point = [x, y]
            
            if not ins(point): # Along edge of map, shouldn't be a room (perhaps a door or something)
                continue
            
            begin = point[j] 
           
            while ins(point) and pixels[point[0], point[1]] == BLACK: # Travel along wall
                point[j] += d
                
            while ins(point) and pixels[point[0], point[1]] == WHITE: # Travel along potential hallway area
                point[j] += d
               
            end = point[j] - d # Go back one pixel
            
            if not ins(point): # Reached end of map, shouldn't be a hallway
                continue
            
            # Get rectangular path it traveled along
            
            if i <= 1:
                rect = [min(begin, end), max(begin, end), center_y - 2, center_y + 2]
            else:
                rect = [center_x - 2, center_x + 2, min(begin, end), max(begin, end)]
                
            if not ins([rect[0], rect[2]]) or not ins([rect[1], rect[3]]): # Reached end of map, shouldn't be a hallway
                continue
                
            # Limit distance of how far it traveled along blank area since usually looks out onto a small-length hallway
            if abs(begin - end) > 100:
                continue
              
            if all(not rectangle_overlap(rect, r2) for r2 in rooms if r != r2): # If no intersection, new area is hallway 
                remove_box(pixels, rect[0], rect[1], rect[2], rect[3]) # Replace all walls with blank pixels
                        
    return image # Return updated map
    