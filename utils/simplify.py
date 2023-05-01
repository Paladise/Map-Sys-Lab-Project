# Code to build upon pathways along hallways and rooms

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
MIN_CONTINUE = 40
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
        
        # Get distance to next wall when moving along certain direction
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
    
    # Check horizontal strips, create vertical lines
    
    ignore = set()
    
    for y in range(height):
        for x in range(width):
            if pixels2[x, y] == BLACK: # Wall
                dist = move_along2(x + 1, y, 1, 0) + 1 # Distance to next wall
                
                if dist < 3: # Continue if only 1-2 pixel gap
                    continue
                elif any((inside(x + dist // 2 + i, y) and pixels2[x + dist // 2 + i, y] == GREEN) for i in range(-DOORWAY_SIZE, DOORWAY_SIZE + 1)) and dist > DOORWAY_SIZE: # Go to midway between both walls, and if its wider than a doorway, continue if there are any pathways next to it within a doorway range
                    continue
                    
                x += dist // 2 # Go to midpoint between walls
                
                if (x, y) in ignore or pixels2[x, y] == GREEN:
                    continue
                
                pixels2[x, y] = RED
                
                # Go vertically in both directions
        
                dir_x = 0

                for dir_y in (-1, 1):
                    not_centered = 0
                    j = 1
                    while True:
                        x1, y1 = x + dir_x * j, y + dir_y * j
                        
                        if inside(x1, y1) and pixels2[x1, y1] == WHITE: # Until hits wall or edge of image                            
                            pixels2[x1, y1] = GREEN
                            # Get distances horizontally perpendicular to next wall
                            dist1 = move_along2(x1, y1, -1, 0)
                            dist2 = move_along2(x1, y1, 1, 0)
                            
                            if dist1 + dist2 >= 5 and dist1 + dist2 < DOORWAY_SIZE and (dist1 + dist2 - dist > 1 or (dist1 + dist2 != dist and dist1 == dist2)):
                                break
                            elif abs(dist1 - dist2) > 5 and (dist1 < 5 or dist2 < 5): # Path is hugging a wall, and not in center of hallway
                                not_centered += 1
            
                            elif dist1 + dist2 < DOORWAY_SIZE:
                                pixels2[x1, y1] = YELLOW
                                
                            if not_centered == MIN_CONTINUE:
                                break
                        else:
                            break
                        j += 1
                        
                    if not inside(x1, y1): # Hit outside of image
                        dir_y *= -1
                        while True:
                            x1, y1 = x + dir_x * j, y + dir_y * j
                            if inside(x1, y1):
                                ignore.add((x1, y1))
                                dist1 = move_along2(x1, y1, -1, 0)
                                dist2 = move_along2(x1, y1, 1, 0)
                                
                                if dist1 + dist2 >= 5 and dist1 + dist2 < DOORWAY_SIZE and abs(dist1 - dist2) <= 1:
                                    break
                                
                                pixels2[x1, y1] = WHITE
                            else:
                                break
                            j += 1
                        
#     image2.save("after_horizontal.png")
    
    # Check vertical strips, create horizontal lines
    
    ignore = set()
    
    for x in range(width):
        for y in range(height):
            if pixels2[x, y] == BLACK or pixels2[x, y] == GREEN: # Wall
                dist = move_along(x, y + 1, 0, 1) + 1 # Distance to next green or black pixel        
                if dist < 3:
                    continue
                elif inside(x, y + dist) and (pixels2[x, y] == GREEN or pixels2[x, y + dist] == GREEN) and dist < MIN_PADDING:
                    continue
                elif inside(x, y + dist) and pixels2[x, y] == GREEN and pixels2[x, y + dist] == GREEN:
                    continue
                    
                y += dist // 2
                
                if (x, y) in ignore or pixels2[x, y] == GREEN:
                    continue
                
                pixels2[x, y] = RED
                
                # Go horizontally in both directions
        
                dir_y = 0

                for dir_x in (-1, 1):   
                    not_centered = 0
                    j = 1
                    while True:
                        x1, y1 = x + dir_x * j, y + dir_y * j
                        if inside(x1, y1) and pixels2[x1, y1] != BLACK:
                            pixels2[x1, y1] = GREEN
                            dist1 = move_along2(x1, y1, 0, 1)
                            dist2 = move_along2(x1, y1, 0, -1)
                            
                            if dist1 + dist2 >= 5 and dist1 + dist2 < DOORWAY_SIZE and (dist1 + dist2 - dist > 1 or (dist1 + dist2 != dist and dist1 == dist2)):                               
                                if pixels2[x1 + dir_x, y1] == GREEN:
                                    break
                            elif abs(dist1 - dist2) > 5 and (dist1 < 5 or dist2 < 5): # Path is hugging a wall, and not in center of hallway
                                not_centered += 1
                                
                            if not_centered == MIN_CONTINUE:
                                break
                        else:
                            break
                        j += 1
                                               
                    if not inside(x1, y1): # Hit outside of image, 
                        j = 0
                        while True:
                            x1, y1 = x + dir_x * j, y + dir_y * j
                            if inside(x1, y1):
                                ignore.add((x1, y1))
                                pixels2[x1, y1] = WHITE
                            else:
                                break
                            j += 1
                            
                            
#     image2.save("after_vertical.png")
                  
    # Expand room name edges to walls
                            
    for name, x, y in rooms:
        pixels2[x, y] = BLUE
        
        if any(inside(x+x3, y+y3) and pixels2[x + x3, y + y3] == GREEN for x3, y3 in DIRECTIONS):
            continue

        for x1, y1 in DIRECTIONS:

            x2, y2 = x + x1, y + y1

            while inside(x2, y2) and pixels2[x2, y2] != BLACK:
                
                if pixels2[x2, y2] != GREEN:
                    pixels2[x2, y2] = BLUE
                    
                if any(inside(x2+x3, y2+y3) and pixels2[x2 + x3, y2 + y3] == GREEN for x3, y3 in DIRECTIONS):
                    break
                    
                x2 += x1
                y2 += y1
                
            if not inside(x2, y2): # Override if hit side of image
                if x1 == 0:
                    y1 *= -1
                else:
                    x1 *= -1
                
                x2 += x1
                y2 += y1
                while pixels2[x2, y2] == BLUE: 
                    pixels2[x2, y2] = WHITE
                    x2 += x1
                    y2 += y1

    # Get possible locations of doorways

    doorways = {}

    for name, orig_x, orig_y in rooms:
        
        if not name.isnumeric(): # Only do doorways for room names that are entirely of numbers
            continue
        
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
                    
            if pixels2[x, y] != YELLOW:
                for x1, y1 in DIRECTIONS:
                    if (x + x1, y + y1) not in visited and inside(x + x1, y + y1) and pixels2[x, y] != BLACK and pixels2[x, y] != WHITE and abs(x + x1 - orig_x) < 50 and abs(y + y1 - orig_y) < 50:
                        visited.add((x + x1, y + y1))
                        queue.append((x + x1, y + y1))  
                        
#     image2.save(f"map_lines_{len(rooms)}.png")

    # Change colors create map in process_image.py                    
                        
    for x in range(width):
        for y in range(height):
            if pixels2[x, y] == BLUE or pixels2[x, y] == RED or pixels2[x, y] == GREEN:
                pixels2[x, y] = WHITE
            elif pixels2[x, y] == WHITE:
                pixels2[x, y] = BLACK
            
    # Clean up
    
#     for orig_x in range(width):
#         for orig_y in range(height):
#             x = orig_x
#             y = orig_y
#             while True:
#                 if pixels2[x, y] == WHITE:
#                     vals = [1 if inside(x+x1, y+y1) and (pixels2[x + x1, y + y1] == WHITE or pixels2[x + x1, y + y1] == YELLOW) else 0 for x1, y1 in DIRECTIONS]
#                     if sum(vals) == 1:
#                         x1, y1 = DIRECTIONS[vals.index(1)]
#                         pixels2[x, y] = BLACK
#                         x += x1
#                         y += y1
#                     else:
#                         if sum(vals) == 0:
#                             pixels2[x, y] = BLACK
#                         break
#                 else:
#                     break
                    
    return image2, doorways    

if __name__ == "__main__":
    rooms = [['Auditorium', 125, 195], ['Aud Lob', 136, 300], ['Gym 1', 138, 405], ['Storage', 139, 638], ['Wrestling', 146, 528], ['Weight', 155, 580], ['Gym 2', 235, 715], ['PCR', 314, 236], ['Ghandi', 346, 498], ['Art Gallery', 347, 306], ['Front', 415, 188], ['Office', 416, 203], ['Faraday', 427, 603], ['Nobel', 459, 234], ['Dome', 464, 138], ['115C', 595, 228], ['Energy', 624, 91], ['Optics', 654, 193], ['Galileo', 652, 292], ['Einstein', 684, 756], ['8 Proto', 710, 80], ['M', 725, 228], ['Cafe', 782, 517], ['DaVinci', 793, 187], ['Boiler', 858, 415], ['Ocean', 877, 220], ['em', 941, 98], ['Turing', 970, 518], ['Cafeteria', 1002, 320], ['1-1', 155, 471], ['1-2', 127, 108], ['1-3', 1093, 113], ['2', 957, 205], ['3-1', 930, 72], ['3-2', 1000, 58], ['4', 897, 195], ['5 Neuro', 864, 71], ['6', 816, 107], ['8', 771, 137], ['9-1', 651, 67], ['9-2', 656, 137], ['10', 840, 231], ['11', 756, 235], ['12', 688, 236], ['14', 728, 297], ['15', 790, 296], ['16', 875, 296], ['17', 945, 297], ['18', 790, 333], ['22', 791, 397], ['23', 791, 472], ['25', 885, 480], ['26', 923, 464], ['27', 969, 452], ['28', 1011, 452], ['29', 1058, 464], ['30', 1099, 492], ['31', 1061, 549], ['33', 1045, 594], ['34', 939, 594], ['36', 919, 549], ['37', 869, 549], ['38 M', 805, 565], ['39', 869, 583], ['40', 857, 610], ['42', 922, 685], ['45', 867, 698], ['47', 750, 602], ['48', 797, 660], ['50', 753, 660], ['51', 770, 712], ['52', 770, 784], ['53', 640, 784], ['54', 640, 712], ['56', 705, 601], ['57', 687, 660], ['58', 663, 601], ['59', 644, 660], ['60', 599, 561], ['62', 599, 461], ['64', 599, 422], ['65', 599, 379], ['66', 599, 339], ['67', 605, 296], ['68', 568, 296], ['69', 559, 339], ['70', 558, 379], ['71', 558, 423], ['73', 558, 461], ['74', 558, 520], ['75', 558, 562], ['77', 611, 667], ['80', 551, 661], ['81', 561, 601], ['82', 515, 660], ['83', 489, 601], ['84', 471, 659], ['85', 427, 660], ['86', 392, 601], ['87', 382, 660], ['88', 357, 732], ['89', 356, 777], ['98', 34, 428], ['103', 273, 464], ['104', 298, 463], ['105', 352, 562], ['106', 351, 529], ['107', 374, 453], ['109', 281, 422], ['110', 281, 371], ['111', 364, 356], ['113', 296, 331], ['115', 535, 235], ['118', 358, 236], ['130', 29, 336], ['131', 35, 280], ['134', 35, 160], ['135', 35, 92], ['Stairs-1', 268, 77], ['Stairs-2', 1008, 84], ['Stairs-3', 617, 138], ['Stairs-4', 277, 236], ['Stairs-5', 814, 237], ['Stairs-6', 513, 296], ['Stairs-7', 658, 512], ['Stairs-8', 1100, 534], ['Stairs-9', 353, 664], ['Stairs-10', 961, 675], ['Stairs-11', 690, 803], ['Signage-1', 692, 278], ['Signage-2', 437, 306], ['Signage-3', 798, 499], ['Signage-4', 333, 511], ['Signage-5', 737, 745], ['Door 14', 226, 52], ['Door-1', 361, 70], ['Door 1', 477, 97], ['Door 2', 584, 160], ['Door 4', 1108, 265], ['Door 12', 13, 321], ['Door 11', 12, 440], ['Door 5', 1125, 515], ['Door 10', 78, 620], ['Door 8', 542, 695], ['Door 6', 831, 745], ['Door-2', 331, 818], ['Door 7', 713, 827]]
    
#     rooms = [['Box', 25, 150], ['Franklin', 109, 216], ['M-1', 131, 559], ['t', 161, 174], ['Library', 318, 408], ['Robotics', 400, 78], ['208 Elec', 401, 165], ['Tesla', 461, 686], ['M-2', 495, 204], ['Curie', 516, 113], ['M-3', 573, 558], ['DNA', 589, 75], ['Biotech', 657, 71], ['1t', 707, 622], ['Hopper', 728, 445], ['03', 601, 49], ['22', 193, 276], ['200', 718, 130], ['201', 656, 45], ['202', 622, 161], ['206', 512, 53], ['207', 399, 54], ['211', 549, 268], ['212', 493, 268], ['214', 451, 211], ['215', 405, 211], ['217', 358, 210], ['219', 313, 210], ['225', 137, 266], ['226', 90, 266], ['229', 679, 450], ['230', 680, 417], ['232', 813, 417], ['233', 813, 450], ['235', 816, 532], ['236', 769, 532], ['237', 723, 532], ['238', 677, 532], ['239', 628, 513], ['240', 628, 556], ['241', 652, 600], ['242', 682, 671], ['243', 638, 670], ['244', 595, 671], ['245', 559, 622], ['246', 522, 560], ['247', 515, 622], ['248', 532, 669], ['249', 531, 740], ['250', 403, 741], ['251-1', 403, 671], ['251-2', 748, 413], ['252', 470, 564], ['253', 451, 622], ['254', 426, 564], ['255', 408, 622], ['256', 309, 314], ['278', 335, 564], ['282', 284, 622], ['283', 258, 564], ['284', 241, 622], ['285', 198, 622], ['286', 163, 564], ['Sign-1', 543, 139], ['Sign-2', 409, 371], ['Sign-3', 735, 462], ['Stair-1', 772, 63], ['Stair-2', 394, 120], ['Stair-3', 210, 141], ['Stair-4', 61, 206], ['Stair-5', 579, 209], ['Stair-6', 285, 270], ['Stair-7', 429, 476], ['Stair-8', 860, 501], ['Stair 287', 134, 624], ['Stair-9', 725, 637], ['Stair-10', 457, 761]]
    
    from PIL import Image    
    simplify_map(rooms, Image.open("debug_images/blank2.png"))
#     simplify_map(rooms, Image.open("debug_images/blank3.png"))