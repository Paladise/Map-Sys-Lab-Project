import cv2 as cv
import numpy as np
from PIL import Image

try:
    from utils.drawing import remove_box
except:
    from drawing import remove_box

THRESHOLD = .65 # Threshold needed to identify something as a symbol
BLACK = (0, 0, 0)

def flood(pixels, x, y, found, min_x, max_x, min_y, max_y, width, height):
    """
    Flood Fill
    """
    
    if x < 0 or y < 0 or x >= width or y >= height:
        return found, min_x, max_x, min_y, max_y

    if pixels[x, y] == BLACK and (x, y) not in found and len(found) < 400:
        found.add((x, y))

        if x < min_x:
            min_x = x
        elif x > max_x:
            max_x = x

        if y < min_y:
            min_y = y
        elif y > max_y:
            max_y = y

        for x1, y1 in ((-1, 0), (1, 0), (0, -1), (0, 1)):             
            found, min_x, max_x, min_y, max_y = flood(pixels, x + x1, y + y1, found, min_x, max_x, min_y, max_y, width, height)
                
    return found, min_x, max_x, min_y, max_y

def find_symbols(pil_image, pos_symbols, directory, symbol_files, debugging = False):
    """
    Find any remaining symbols given a blank image    
    """
    
    image = np.array(pil_image)  # Convert PIL image to opencv
    pixels = pil_image.load()
    symbols = {}
    
    for file, symbol in symbol_files.items(): # For every symbol
        symbols[symbol] = []
        template = cv.imread(directory + file) # Get template (uploaded-separately) symbol
        w, h = template.shape[:-1]

        res = cv.matchTemplate(image, template, cv.TM_CCOEFF_NORMED) # Use openCV to match it in map image
    
        loc = np.where(res >= THRESHOLD)
        pos_points = [pt for pt in zip(*loc[::-1])] # Switch columns and rows  
        for pt in pos_points:      
            x, y = pt[0], pt[1]
            
            amount = 0
            for x1, y1 in pos_points:
                dist = ((x-x1)**2 + (y-y1)**2)**0.5
                if dist < 75 and dist > 25:
                    amount += 1
            
            if amount <= 1: # Ignore all ones that are close to other symbols
                if all((abs(x - x1) + abs(y - y1)) > 100 for x1, y1 in symbols[symbol]): # Add padding to prevent duplicates
                    
                    # Attempt to expand boundaries since template image might have not have same size as actual symbol on map
                
                    found_start = False
                    
                    start_x, start_y = x, y
                    for x1 in range(x, x + w):
                        if not found_start:
                            for y1 in range(y, y + h):
                                if not found_start:
                                    if pixels[x1, y1] == BLACK:
                                        start_x = x1
                                        start_y = y1
                                        found_start = True
                                else:
                                    break
                        else:
                            break
                                
                    found, min_x, max_x, min_y, max_y = flood(pixels, start_x, start_y, set(), x, x + w, y, y + h, image.shape[1], image.shape[0])
                    
                    w, h = template.shape[:-1]
                    
                    if len(found) < 400 and 2*w > (max_x - min_x) and 2*h > (max_y - min_y):
                        x, y, w, h = min_x, min_y, max_x - min_x, max_y - min_y
                    
                    remove_box(pixels, x, x + w, y, y + h)
                    if debugging:
                        if symbol in "stairs":
                            cv.rectangle(image, (x, y), (x + w, y + h), (0, 0, 255), 1)
                        else:
                            cv.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 1)
                    symbols[symbol].append((x + w//2, y + h//2)) # Append midpoint
    
    if debugging:
        cv.imwrite("debug_results/search_result_rect.png", image)
    
    return symbols, pil_image

def integrate_detected(rooms, found_symbols, stair_coords):
    """
    Combine found rooms and symbols into one array for simpler exporting
    """
    
    for symbol, list_of_coords in found_symbols.items():
        for coord in list_of_coords:
            
            
            # Attempt to combine names detected near symbols into one label
            
            combined = False             
            x, y = coord[0], coord[1]            
            for room in rooms:
                label, x1, y1 = room[0], room[1], room[2]
                
                if abs(y - y1) < 5 and x < x1 and x1 - x < 25: # Possibly should be one label
                    combined = True
                    rooms.remove(room)
                    new_label = symbol.capitalize() + " " + label
                    rooms.append([new_label, x, y])
                    break
                    
            if not combined: # Did not combine with any existing room names        
                rooms.append([symbol.capitalize(), x, y])
            
            if symbol.lower() in ["stair", "stairs", "stairway"]:
                stair_coords.append([x, y])

    return rooms, stair_coords

    
if __name__ == "__main__":
    symbols, image = find_symbols(Image.open("debug_images/blank2.png"), ["door", "stairs", "sign"], "debug_images/", {"door.png": "door", "stairs.png": "stairs", "symbolsignage.png": "sign"}, True)
    
    image.save("debug_results/search_result.png")
    
    print("Symbols:", symbols)