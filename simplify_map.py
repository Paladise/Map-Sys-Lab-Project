DIRECTIONS = (
    (1, 0),
    (-1, 0),
    (0, 1),
    (0, -1)
)

RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)

PADDING = 50
DIST_BETWEEN = PADDING

def simplify(rooms, image):
    def inside(x, y):
        if x < 0 or y < 0 or x >= width or y >= height:
            return False
        else:
            return True

    def move_along(x, y, dir_x, dir_y):
        x1, y1 = x, y
        while inside(x, y) and pixels2[x, y] == WHITE and abs(x1 - x) <= PADDING and abs(y1 - y <= PADDING):
            x += dir_x
            y += dir_y

        if dir_x == 0:
            return abs(y1 - y)
        else:
            return abs(x1 - x)
        
    def move_along2(x, y, dir_x, dir_y):
        x1, y1 = x, y
        while inside(x, y) and pixels2[x, y] != BLACK:
            x += dir_x
            y += dir_y

        if dir_x == 0:
            return abs(y1 - y)
        else:
            return abs(x1 - x)
    
    pixels = image.load()
    width, height = image.size[0], image.size[1]

    image2 = image.copy()
    pixels2 = image2.load()
    
    # Go throughout entire image

    for x in range(width):
        if (width - x) % 10 == 0:
            print("x left:", width - x)
        for y in range(height):

            if pixels2[x, y] == WHITE:
                dists = []
                
                # Get distances to nearest obstacle (or end of map) in every direction

                for dir_x, dir_y in DIRECTIONS:
                    dist = move_along(x, y, dir_x, dir_y)
                    dists.append(dist)

                if ((abs(dists[0] - dists[1]) == 1 and (dists[0] + dists[1]) % 2 == 1) or abs(dists[0] - dists[1]) == 0) and dists[0] < PADDING:

                    # If that pixel is horizontally centered between two things (walls/paths)
                    
                    if dists[2] < 3 or dists[3] < 3:
                        continue
                    
                    if inside(x + dists[0], y) and inside(x - dists[1], y) and (pixels2[x + dists[0], y] in (RED, GREEN) or pixels2[x - dists[1], y] in (RED, GREEN)):
                        continue

                    pixels2[x, y] = RED
    
                    # Go vertically in both directions
        
                    dir_x = 0

                    for dir_y in (-1, 1):                    
                        j = 1
                        while True:
                            x1, y1 = x + dir_x * j, y + dir_y * j
                            if inside(x1, y1) and pixels2[x1, y1] == WHITE:
                                pixels2[x1, y1] = GREEN
                            else:
                                break
                            j += 1
                elif ((abs(dists[2] - dists[3]) == 1 and (dists[2] + dists[3]) % 2 == 1) or abs(dists[2] - dists[3]) == 0) and dists[2] < PADDING:
                    
                    # If that pixel is vertically centered between two things
                    
                    if dists[0] < 3 or dists[1] < 3:
                        continue                        
                    if inside(x, y + dists[2]) and inside(x, y - dists[3]) and (pixels2[x, y + dists[2]] in (RED, GREEN) or pixels2[x, y - dists[3]] in (RED, GREEN)):
                        continue

                    pixels2[x, y] = RED     
                    
                    # Go horizontally in both directions
                    
                    dir_y = 0

                    for dir_x in (-1, 1):
                        j = 1
                        while True:
                            x1, y1 = x + dir_x * j, y + dir_y * j
                            if inside(x1, y1) and pixels2[x1, y1] == WHITE:
                                pixels2[x1, y1] = GREEN
                            else:
                                break
                            j += 1
                  
    # Expand room name edges to walls
                            
    for name, x, y in rooms:
        pixels2[x, y] = BLUE

        for x1, y1 in DIRECTIONS:

            x2, y2 = x + x1, y + y1

            while inside(x2, y2) and pixels2[x2, y2] == WHITE: 
                pixels2[x2, y2] = BLUE
                x2 += x1
                y2 += y1

    # Get possible locations of doorways

    doorways = {}

    for name, orig_x, orig_y in rooms:
        
        x, y = orig_x, orig_y
        
        doorways[name] = []
    
        queue = [(x, y)]
        visited = set()
        
        while queue:
            x, y = queue.pop()
            
            if pixels2[x, y] == RED or pixels2[x, y] == YELLOW:
            
                dists = []
                for dir_x, dir_y in DIRECTIONS:
                    dist = move_along2(x, y, dir_x, dir_y)
                    dists.append(dist)

                if (abs(dists[0] - dists[1]) <= 1 and dists[0] <= 8) or (abs(dists[2] - dists[3]) <= 1 and dists[2] <= 8): # Found doorway
                    pixels2[x, y] = YELLOW

                    doorways[name].append((x, y))
            else:
                for x1, y1 in DIRECTIONS:
                    if (x + x1, y + y1) not in visited and inside(x + x1, y + y1) and pixels2[x, y] != BLACK and pixels2[x, y] != WHITE and abs(x + x1 - orig_x) < 50 and abs(y + y1 - orig_y) < 50:
                        visited.add((x + x1, y + y1))
                        queue.append((x + x1, y + y1))   

    # Clean everything up to create map in process_image.py                    
                        
    for x in range(width):
        for y in range(height):
            if pixels2[x, y] == BLUE or pixels2[x, y] == RED or pixels2[x, y] == GREEN:
                pixels2[x, y] = WHITE
            elif pixels2[x, y] == WHITE:
                pixels2[x, y] = BLACK  
            elif pixels2[x, y] == YELLOW:
                pixels2[x, y] = BLUE
                        
    return image2, doorways

    
if __name__ == "__main__": # For debugging
    import json
    from PIL import Image
    blank_map = Image.open("map.png")
    
    with open("render_floor1.json") as f:
        data = json.load(f)
    
    rooms = data["rooms"]
        
    image2, doorways = simplify(rooms, blank_map)
    image2.save("map_lines2.png")
    