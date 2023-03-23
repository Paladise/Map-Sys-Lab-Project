import cv2 as cv
import numpy as np
from PIL import Image

try:
    from utils.drawing import remove_box
except:
    from drawing import remove_box

THRESHOLD = .65 # Threshold needed to identify something as a symbol

def find_symbols(pil_image, pos_symbols, directory, symbol_files):
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
        for pt in zip(*loc[::-1]):  # Switch columns and rows            
            x, y = pt[0], pt[1]
            if all((abs(x - x1) + abs(y - y1)) > 100 for x1, y1 in symbols[symbol]): # Add padding to prevent duplicates
                remove_box(pixels, x, x + w, y, y + h)
#                 cv.rectangle(image, pt, (x + w, y + h), (0, 0, 255), 2)
                symbols[symbol].append((x + w//2, y + h//2)) # Append midpoint
    
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
    symbols, image = find_symbols(Image.open("debug_images/blank2.png"), ["door", "stairs"], [])
    
    image.save("debug_results/search_result.png")
    
    print("Symbols:", symbols)