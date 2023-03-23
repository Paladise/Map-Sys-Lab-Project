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

MIN_PADDING = 20
DOORWAY_SIZE = 10
PADDING = 50
DIST_BETWEEN = PADDING

def simplify_map(rooms, image):
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
    
    # Check horizontal strips
    
    for y in range(height):
        for x in range(width):
            if pixels2[x, y] == BLACK or x == 0: # Wall
                dist = move_along2(x + 1, y, 1, 0) + 1 # Distance to next wall
                
                if dist == 1:
                    continue
                elif inside(x + dist, y) and (pixels2[x, y] == GREEN or pixels2[x + dist, y] == GREEN) and dist < MIN_PADDING:
                    continue
                elif any((inside(x + dist // 2 + i, y) and pixels2[x + dist // 2 + i, y] == GREEN) for i in range(-DOORWAY_SIZE, DOORWAY_SIZE + 1)) and dist > DOORWAY_SIZE:
                    continue
                    
                x += dist // 2
                
                pixels2[x, y] = RED
                
                # Go vertically in both directions
        
                dir_x = 0

                for dir_y in (-1, 1):                    
                    j = 1
                    while True:
                        x1, y1 = x + dir_x * j, y + dir_y * j
                        if inside(x1, y1) and pixels2[x1, y1] == WHITE:
                            pixels2[x1, y1] = GREEN
                            dist1 = move_along2(x1, y1, -1, 0)
                            dist2 = move_along2(x1, y1, 1, 0)
                            if dist1 + dist2 >= 5 and dist1 + dist2 < DOORWAY_SIZE and (dist1 + dist2 != dist + 1 or (dist1 + dist2 != dist and dist1 == dist2)):
                                break
                        else:
                            break
                        j += 1
                        
#     image2.save("after_horizontal.png")
    
    # Check vertical strips
    
    for x in range(width):
        for y in range(height):
            if pixels2[x, y] == BLACK or y == 0 or pixels2[x, y] == GREEN: # Wall
                dist = move_along(x, y + 1, 0, 1) + 1 # Distance to next green or black pixel        
                if dist == 1:
                    continue
                elif inside(x, y + dist) and (pixels2[x, y] == GREEN or pixels2[x, y + dist] == GREEN) and dist < MIN_PADDING:
                    continue
                y += dist // 2
                
                pixels2[x, y] = RED
                
                # Go horizontally in both directions
        
                dir_y = 0

                for dir_x in (-1, 1):                          
                    j = 1
                    while True:
                        x1, y1 = x + dir_x * j, y + dir_y * j
                        if inside(x1, y1) and pixels2[x1, y1] == WHITE:
                            pixels2[x1, y1] = GREEN
                            dist1 = move_along2(x1, y1, 0, 1)
                            dist2 = move_along2(x1, y1, 0, -1)
                            if dist1 + dist2 >= 5 and dist1 + dist2 < DOORWAY_SIZE and (dist1 + dist2 != dist + 1 or (dist1 + dist2 != dist and dist1 == dist2)):
                                if dir_x == 1:
                                    pixels2[x1, y1] = WHITE
                                break
                        else:
                            break
                        j += 1
                        
#     image2.save("after_vertical.png")
                  
    # Expand room name edges to walls
                            
    for name, x, y in rooms:
        pixels2[x, y] = BLUE

        for x1, y1 in DIRECTIONS:

            x2, y2 = x + x1, y + y1

            while inside(x2, y2) and pixels2[x2, y2] != BLACK: 
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
                    dist = move_along2(x, y, dir_x, dir_y) # Until wall
                    dists.append(dist)

                if (abs(dists[0] - dists[1]) <= 1 and dists[0] <= 8) or (abs(dists[2] - dists[3]) <= 1 and dists[2] <= 8): # Found doorway
                    pixels2[x, y] = YELLOW

                    doorways[name].append((x, y))
                    continue

            for x1, y1 in DIRECTIONS:
                if (x + x1, y + y1) not in visited and inside(x + x1, y + y1) and pixels2[x, y] != BLACK and pixels2[x, y] != WHITE and abs(x + x1 - orig_x) < 50 and abs(y + y1 - orig_y) < 50:
                    visited.add((x + x1, y + y1))
                    queue.append((x + x1, y + y1))  
                        
#     image2.save("map_lines.png")

    # Change colors create map in process_image.py                    
                        
    for x in range(width):
        for y in range(height):
            if pixels2[x, y] == BLUE or pixels2[x, y] == RED or pixels2[x, y] == GREEN:
                pixels2[x, y] = WHITE
            elif pixels2[x, y] == WHITE:
                pixels2[x, y] = BLACK
            
    # Clean up
    
    for orig_x in range(width):
        for orig_y in range(height):
            x = orig_x
            y = orig_y
            while True:
                if pixels2[x, y] == WHITE:
                    vals = [1 if inside(x+x1, y+y1) and (pixels2[x + x1, y + y1] == WHITE or pixels2[x + x1, y + y1] == YELLOW) else 0 for x1, y1 in DIRECTIONS]
                    if sum(vals) == 1:
                        x1, y1 = DIRECTIONS[vals.index(1)]
                        pixels2[x, y] = BLACK
                        x += x1
                        y += y1
                    else:
                        if sum(vals) == 0:
                            pixels2[x, y] = BLACK
                        break
                else:
                    break
                               
    return image2, doorways    