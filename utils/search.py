import cv2 as cv
import numpy as np
from PIL import Image

try:
    from utils.drawing import remove_box
except:
    from drawing import remove_box

THRESHOLD = .6 # Threshold needed to identify something as a symbol

def find_symbols(pil_image, pos_symbols, directory, symbol_files, debugging = False):
    """
    Find any remaining symbols given a blank image    
    """
    
    image = np.array(pil_image)  # Convert PIL image to opencv
    pixels = pil_image.load()
    symbols = {}
    
    for file, symbol in symbol_files.items():
        symbols[symbol] = []
        template = cv.imread(directory + file)
        w, h = template.shape[:-1]

        res = cv.matchTemplate(image, template, cv.TM_CCOEFF_NORMED)
    
        loc = np.where(res >= THRESHOLD)
        pos_points = [pt for pt in zip(*loc[::-1])]
        for pt in pos_points:  # Switch columns and rows      
            x, y = pt[0], pt[1]
            
            amount = 0
            for x1, y1 in pos_points:
                dist = ((x-x1)**2 + (y-y1)**2)**0.5
                if dist < 75 and dist > 25:
                    amount += 1
            
            if amount <= 1: # Ignore all ones that are close to other symbols
                if all((abs(x - x1) + abs(y - y1)) > 100 for x1, y1 in symbols[symbol]): # Add padding to prevent duplicates
                    remove_box(pixels, x, x + w, y, y + h)
                    if debugging:
                        if symbol in "stairs":
                            cv.rectangle(image, pt, (x + w, y + h), (0, 0, 255), 1)
                        else:
                            cv.rectangle(image, pt, (x + w, y + h), (0, 255, 0), 1)
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
            x, y = coord[0], coord[1]
            rooms.append([symbol.capitalize(), x, y])
            
            if symbol.lower() in ["stair", "stairs", "stairway"]:
                stair_coords.append([x, y])
    
    return rooms, stair_coords

    
if __name__ == "__main__":
    symbols, image = find_symbols(Image.open("debug_images/blank2.png"), ["door", "stairs"], "debug_images/", {"door.png": "door", "stairs.png": "stairs"}, True)
    
    image.save("debug_results/search_result.png")
    
    print("Symbols:", symbols)