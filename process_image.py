import cv2 as cv
import enchant
import json
import numpy as np
import pytesseract
import sys
import time
from detect_if_symbol import detect_if_symbol, get_similarity_thresholds
from drawing import draw_boxes, draw_square, image_to_bw, remove_box, create_image_from_box, flood, print_image_with_ascii
from PIL import Image
from simplify_map import simplify
from unidecode import unidecode

start_time = time.perf_counter()

id = sys.argv[1]
READ_FROM = sys.argv[2]

TESSERACT_DIR_CONFIG = '--tessdata-dir "/cluster/2023abasto/local/share/tessdata"'

sys.setrecursionlimit(10000) # We don't talk about this line

# d = enchant.DictWithPWL("en_US","potential_room_names.txt")
d = enchant.request_pwl_dict("potential_room_names.txt")

CHANGED = 200
CONFIDENCE_THRESHOLD = 60
UPPER_CONFIDENCE_THRESHOLD = 90
IMAGE_SAVE_PATH = f"media/{id}/"
FILE_NAME = IMAGE_SAVE_PATH + READ_FROM
DIST_BETWEEN_LETTERS = 15
DIST_FOR_SPACE = 4
Y_THRESHOLD = 6
BW_THRESHOLD = 150 # Values less than this will become black
RESIZE = 2
PADDING = 3

MOVE_COORDS = ((1, 0), (-1, 0), (0, 1), (0, -1))

# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract" # Windows
# pytesseract.pytesseract.tesseract_cmd = r"/cluster/2023abasto/local/bin/tesseract"
pytesseract.pytesseract.tesseract_cmd = r"/cluster/2023abasto/tesseract-5.1.0/tesseract"
print("Using tesseract version:", pytesseract.get_tesseract_version())


def find_rectangles(pixels, x, y, found, min_x, max_x, min_y, max_y):
    """
    Recursively go through image to check neighboring pixels to form blobs
    of rectangles as well as min & max for x & y.
    """

    try: # Crude way of making sure pixel is not outside of image
        pixels[x, y]
    except:
        return found, min_x, max_x, min_y, max_y

    min_x1, max_x1, min_y1, max_y1 = min_x, max_x, min_y, max_y

    if (x, y) not in found and pixels[x, y] == (0, 0, 0): # Found unvisited black pixel
            
        if x < min_x:
            min_x = x
        elif x > max_x:
            max_x = x

        if y < min_y:
            min_y = y
        elif y > max_y:
            max_y = y

        # Determine if area is still a rectangle

        if all(pixels[x1, y1] == (0, 0, 0) for x1 in range(min_x, max_x + 1) for y1 in range(min_y, max_y + 1)):       
            found.add((x, y))
            for x1 in range(-1, 2):
                for y1 in range(-1, 2):
                    if abs(x1) == abs(y1):
                        continue
                    found, min_x, max_x, min_y, max_y = find_rectangles(pixels, x + x1, y + y1, found, min_x, max_x, min_y, max_y)
        else:
            min_x, max_x, min_y, max_y = min_x1, max_x1, min_y1, max_y1

    return found, min_x, max_x, min_y, max_y


def predict_name(x1, x2, y1, y2, single_char = True, has_spaces = False, symbols = {}, boxes = []):
    """
    Uses box coordinates to create a gray-scale PIL image specifically of that region (with padding)
    And checks if that image is a symbol from key, and if not uses pytesseract to 
    determine what character(s) are in it along with their respective confidences.
    """

    global box_stats

    # Creating image of that specific area
    
    print("Calling from predict name")

    potential_image = create_image_from_box(pixels, x1, x2, y1, y2, PADDING, boxes)
    potential_pixels = potential_image.load()

    # Remove symbols from image before running pytesseract on it

    for box in symbols.keys():
        bx1, bx2, by1, by2 = box

        for x in range(bx1, bx2):
            for y in range(by1, by2):   
                potential_pixels[x - x1 + PADDING, y - y1 + PADDING] = 255

    # Run pytesseract (or saved data) on image    

    detected = ""
    confidence = -1

    config = f"--oem 3 -l eng --psm 7 {TESSERACT_DIR_CONFIG}"

    print("Running with x1", x1, "x2", x2, "y1", y1, "y2", y2)

    p = pytesseract.image_to_data(
        potential_image, config = config, output_type=pytesseract.Output.DICT)   
    print("predict:", p)

    predict = {"conf": [], "text": []}

    for index, val in enumerate(p["conf"]):
        if val != -1:
            predict["conf"].append(val)
            predict["text"].append(p["text"][index])

    try:
        detected = " ".join(predict["text"])
        confidence = predict["conf"][0]                  
    except:
        pass

    # print("Detected within predict_name:", detected, "with confidence:", confidence)

    # "Reinsert" symbols into detected string

    for s in symbols.values():
        symbol, index = s
        detected = detected[:index] + symbol + detected[index:] 

    return detected, confidence


def generate_name(cur_box, used_boxes, detected_name, has_spaces, symbols):
    """
    Recursive function using the current box, used boxes, and detected name
    so far to check neighboring pixels and try to construct the full room name.
    """

    ax1, ax2, ay1, ay2 = cur_box
    symbol = detect_if_symbol(pixels_original, SIMILARITY_THRESHOLDS, ax1, ax2, ay1, ay2)    
    if symbol:
        symbols[cur_box] = (symbol, len(detected_name))

    used_boxes.append(cur_box)
    detected_name.append(cur_box)   

    for box in boxes:
        if box in used_boxes:
            continue

        bx1, bx2, by1, by2 = box
        
#         intersection = max(0, min(ax2, bx2) - max(ax1, bx1)) * max(0, min(ay2, by2) - max(ay1, by1))
            
        if(
            abs((ay1+ay2)/2 - (by1+by2)/2) <= Y_THRESHOLD and # Check if y-coord of centers of boxes are close together
            abs(ax2 - bx1) <= DIST_BETWEEN_LETTERS and # Check if boxes are close enough to be considered in same label
            abs(ay1 - by1) <= Y_THRESHOLD and by2 - by1 > 4 and # 
            all(pixels[x, ay2] != (0, 0, 0) for x in range(ax2, bx1))
          ): # Part of same word
            
            if abs(ax2 - bx1) >= DIST_FOR_SPACE:
                has_spaces = True               
            
            used_boxes, detected_name, has_spaces, symbols = generate_name(box, used_boxes, detected_name, has_spaces, symbols)
            break

    return used_boxes, detected_name, has_spaces, symbols


def flood_y(pixels, x, prev_x):
    """
    Flood y-coord given the image, the x coordinate that you are filling on,
    and the previous x coordinate's all found y-values
    """

    start_y = None
    found = []

    for y in prev_x:
        if pixels[x, y] == (0, 0, 0):
            start_y = y
            break
     
    if start_y:
        for i in (-1, 1):
            y = start_y
            while True:
                if pixels[x, y] == (0, 0, 0) and len(found) <= max_height:
                    found.append(y)
                    y += i
                else:
                    break

    return found  


def flood_character(pixels, x, y, found_pixels):
    if pixels[x, y] == (255, 255, 255):
        return found_pixels
    else:
        max_x, min_x, max_y, min_y = float("-inf"), float("inf"), float("-inf"), float("inf")
        for p in found_pixels:
            max_x = max(max_x, p[0])
            min_x = min(min_x, p[0])
            max_y = max(max_y, p[1])
            min_y = min(min_y, p[1])
    
        if max_x - min_x > max_height or max_y - min_y > max_height:
            return None
        
        found_pixels.add((x, y))
        
        for x1 in range(-1, 2):
            for y1 in range(-1, 2):
                found_pixels = flood_character(pixels, x + x1, y + y1, found_pixels)
                
        return found_pixels

def find_more_chars(pixels, x1, x2, y1, y2, i):
    """
    Attempts to find more symbols that may be a part of room names but are currently
    stuck to walls using current bounding box coords.
    """   

    if i == 1:
        start_x = x2 - 1 # Minus 1 bc of annoying border
    else:
        start_x = x1 + 1 # Add 1 bc of annoying border 

    prev_x = [y for y in range(y1, y2) if pixels[start_x, y] == (0, 0, 0)]
    
    x = start_x
    space = 0
    found = False

    while True: 
        x += i
        
        if x == 0 or x == WIDTH - 1:
            break
            
#         start_y = None
            
#         for y in range(y1, y2):
#             if pixels[x, y] == (0, 0, 0):
#                 start_y = y
#                 break
                
#         if start_y:            
#             found_pixels = flood_character(pixels, x, start_y)
            
#             if found_pixels:
            
#                 if i == 1:
#                     x = max(found_pixels, key=lambda i: i[0])
#                 else:
#                     x = min(found_pixels, key=lambda i: i[0])
#             else:
#                 break
#         else:
#             if space == 5:
#                 return None
            
#             space += 1

        cur_x = flood_y(pixels, x, prev_x)   

        if found:
            prev_x = cur_x    

        if len(cur_x) > max_height: # Most likely a wall
            break
        elif len(cur_x) == 0: # Space
            space += 1
        elif len(cur_x) > 0: # Looking into potential char
            found = True 

            y1 = min(y1, min(cur_x))
            y2 = max(y2, max(cur_x))

        if space == 5 or x < 0 or x > WIDTH: # Only found empty space 
            return None

    return x, y1, y2 # Return updated x boundary, and y-values
 

def process_image(boxes, pixels):
    """
    Process the entire image to identify all integral parts using already-identified boxes.
    """

    used_boxes, rooms = [], []
    
    for box in boxes:    
        if box in used_boxes:
            continue

#         input("Starting to look at new word... [CLICK ENTER TO CONTINUE]")

        used_boxes, detected_name, has_spaces, symbols = generate_name(box, used_boxes, detected_name = [], has_spaces = False, symbols = {})
        first_char = detected_name[0]
        last_char = detected_name[-1]

        if len(detected_name) == 1 and symbols: # If it's a singular symbol
            print_image = create_image_from_box(pixels, x1, x2, y1, y2, 0)
            print_image_with_ascii(print_image)
            s = list(symbols.values())[0][0]
            print("Symbol:", s)
            rooms.append((s, ((first_char[0] + first_char[1])//2, (first_char[2] + first_char[3])//2)))
            remove_box(pixels, first_char[0], first_char[1], first_char[2], first_char[3])
        else: # Predict full room name
            
            if len(detected_name) == 1: # Probably just a wall
                continue
                
            print("After generated name, detected_name:", detected_name)
            print("After generated name symbols:", symbols)

            # Get bounding box of entire room name

            x1, x2 = first_char[0], last_char[1]
            y1, y2 = float("inf"), float("-inf")        
            for i in detected_name:
                y1 = min(y1, i[2])
                y2 = max(y2, i[3])

            # Try to predict room name

            if len(detected_name) == 1:
                single_char = True
            else:
                single_char = False

            # Expand potential word boundaries
            
            full_word, confidence = predict_name(x1, x2, y1, y2, single_char, has_spaces, symbols, detected_name)
            
            print("initial prediction:", full_word, "confidence:", confidence)
            
            print("initial:")
            print_image = create_image_from_box(pixels, x1, x2, y1, y2, 0, detected_name)
            print_image_with_ascii(print_image)
            
            if full_word.isalpha() and len(full_word) > 4 and confidence > 30.0:
                suggestions = [i for i in d.suggest(full_word) if len(i) == len(full_word) + 1]
                print("suggestions:", suggestions)
                if len(suggestions) == 1:
                    full_word = suggestions[0].capitalize()

                    print("Full word after using suggestions:", full_word)
                    rooms.append((full_word, ((first_char[0] + first_char[1])//2, (y1 + y2)//2)))
                    remove_box(pixels, x1, x2, y1, y2)
                    continue
                    
            if " " not in full_word and full_word and d.check(full_word.lower()):
                print("In dictionary so adding...")
                rooms.append((full_word, ((first_char[0] + first_char[1])//2, (y1 + y2)//2)))
                remove_box(pixels, x1, x2, y1, y2)
                continue
            
            if confidence == 0 and full_word.isnumeric() and len(full_word) == len(detected_name) - 1:
                    confidence = CHANGED        
            
            if confidence < CONFIDENCE_THRESHOLD:
                orig = (x1, x2, y1, y2)
                
                if res := find_more_chars(pixels, x1, x2, y1, y2, -1):
                    x1, y1, y2 = res[0], res[1], res[2]

                if res := find_more_chars(pixels, x1, x2, y1, y2, 1):
                    x2, y1, y2 = res[0], res[1], res[2]
                    
                
                if orig != (x1, x2, y1, y2):
                    print("Expanded boundaries to be:", x1, x2, y1, y2)
                    full_word, confidence = predict_name(x1, x2, y1, y2, single_char, has_spaces, symbols)
            
                    print_image = create_image_from_box(pixels, x1, x2, y1, y2, 0, [])
                    print("With expanded")
                    print_image_with_ascii(print_image)
            
            print("Original detected full word:", full_word, "with confidence:", confidence)

            full_word.replace(",", "")
            if len(full_word) > 0 and full_word[0] == "-":
                full_word = full_word[1:]
                print("Modified to be:", full_word)
            
            if len(full_word) == 0:
                print("Empty, so continuing...")
                continue
                
            if " " not in full_word and d.check(full_word.lower()):
                print("In dictionary so adding...")
                rooms.append((full_word, ((first_char[0] + first_char[1])//2, (y1 + y2)//2)))
                remove_box(pixels, x1, x2, y1, y2)
                continue
            
                
            if full_word.isalpha():
                suggestions = [i for i in d.suggest(full_word) if len(i) == len(full_word)]
                print("suggestions:", suggestions)
                if len(suggestions) == 1:
                    full_word = suggestions[0].capitalize()

                    print("Full word after using suggestions:", full_word)
                    rooms.append((full_word, ((first_char[0] + first_char[1])//2, (y1 + y2)//2)))
                    remove_box(pixels, x1, x2, y1, y2)
                    continue
            
            if confidence >= CONFIDENCE_THRESHOLD:
                print(f"Confidence {confidence} greater than threshold: {CONFIDENCE_THRESHOLD}")
                if len(full_word) == 1 and confidence < UPPER_CONFIDENCE_THRESHOLD and not full_word.isnumeric(): # Mis-identified character
                    print("Probable mis-identified character, continuing...")
                    continue
                    
                if full_word.isnumeric() and len(full_word) == 4:
                    if full_word[-1] == "8":
                        full_word = full_word[:3] + "B"
                        
                    for i, char in enumerate(detected_name):
                        if char[1] - char[0] == 2:                           
                            if i == 0 and full_word[i] == "1":
                                first_char = detected_name[1]
                                x1 = first_char[0]
                                full_word = full_word[:i] + full_word[i + 1:] 
                            else:
                                if len(detected_name) == len(full_word) + 1:
                                    full_word2 = full_word[i:]
                                    first_char = detected_name[i + 1]
                                    x1 = first_char[0]
                                    
                                    print("Adding:", full_word2)
                                    
                                    rooms.append((full_word2, ((first_char[0] + first_char[1])//2, (y1 + y2)//2)))
                                    remove_box(pixels, x1, x2, y1, y2)
                                    
                                    first_char = detected_name[0]
                                    x1 = first_char[0]
                                    full_word = full_word[:i]
                                    x2 = detected_name[i - 1][1]
                                
                            break

                # Get word suggestions
    
                full = full_word[:]        
                full_word = []

                for word in full.split(" "):
                    if word == "":
                        continue

                    if not d.check(word) and len(word) > 1 and "-" not in word:
                        suggestions = [i for i in d.suggest(word)]
                        if len(suggestions) == 1:
                            full_word.append(suggestions[0].capitalize())
                        else:
                            full_word.append(word)
                    else:
                        full_word.append(word)
                        
                full_word = " ".join(full_word)
                
                if full_word.count(" ") == 1:
                    a, b = full_word.split(" ")[0], full_word.split(" ")[1]
                    if b == a[-len(b):]:
                        full_word = a
                            
                        print("Changed because in substring")

                print("Full word after using suggestions:", full_word)

                rooms.append((full_word, ((first_char[0] + first_char[1])//2, (y1 + y2)//2)))
                remove_box(pixels, x1, x2, y1, y2)
            else:
                
                if len(full_word) == 2 and full_word.isnumeric() and confidence > 40.0:
                    print("Full word clutch:", full_word)

                    rooms.append((full_word, ((first_char[0] + first_char[1])//2, (y1 + y2)//2)))
                    remove_box(pixels, x1, x2, y1, y2)
                else:                
                    print("Not adding...")   

    a = sorted(rooms, key = lambda i: int(i[0]) if i[0].isnumeric() else 0)
    return [[i[0], i[1][0], i[1][1]] for i in a]

image = Image.open(FILE_NAME).convert("RGB")
pixels_original = image.load()

print("Converting to black and white...")
image = image_to_bw(image, BW_THRESHOLD)
pixels = image.load()
WIDTH, HEIGHT = image.size[0], image.size[1]
image.save(IMAGE_SAVE_PATH + f"black_and_white_{READ_FROM[:-4]}.png")

print("Getting font-size (largest box size)...")

images = cv.imread(IMAGE_SAVE_PATH + f"black_and_white_{READ_FROM[:-4]}.png")
rgb = cv.cvtColor(images, cv.COLOR_BGR2RGB)
results = pytesseract.image_to_data(rgb, output_type=pytesseract.Output.DICT, config = TESSERACT_DIR_CONFIG)

max_height = 50 # Default max height

for i in range(0, len(results["text"])):
    x = results["left"][i]
    y = results["top"][i]
    w = results["width"][i]
    h = results["height"][i]
    text = results["text"][i]
    conf = int(results["conf"][i])
     
    # filter out weak confidence text localizations
    if (conf > 75.0 and text.isalpha() and d.check(text)) or (conf > 90.0 and len(text) >= 2 and text.isnumeric()):
        
        if text.isalpha() and (text[0].isupper() or any(a in "dfhklb" for a in text)) and all(i not in "qypj" for i in text):
            max_height = (round(h * 3/2) + 5)
            print("Confidence: {}".format(conf))
            print("Text: {}".format(text))
            print("height:", h)
            print("Maximum height allowed will be:", max_height)
            print()

print("Drawing boxes...")

# from colorsys import hls_to_rgb
# from random import random
# tresh_min, tresh_max = 128, 255
# cv_image = cv.imread(IMAGE_SAVE_PATH + f"black_and_white_{READ_FROM[:-4]}.png")
# im_bw = cv.cvtColor(cv_image, cv.COLOR_RGB2GRAY)
# (thresh, im_bw) = cv.threshold(im_bw, tresh_min, tresh_max, 0)
# contours, hierarchy = cv.findContours(im_bw, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
# # Find contours, obtain bounding box
# boxes_image = image.copy()
# boxes_pixels = boxes_image.load()
# boxes = set()
# for c in contours:
#     x,y,w,h = cv.boundingRect(c)
#     if  w < 40 and h > 3 and h < max_height:
#         hasdf,s,l = random(), 0.5 + random()/2.0, 0.4 + random()/5.0
#         rgb = tuple([int(256*i) for i in hls_to_rgb(hasdf,l,s)]) 
#         draw_square(boxes_pixels, x, x + w, y, y + h, rgb)
#         boxes.add((x, x + w, y, y + h))
# boxes = sorted(list(boxes), key = lambda b: (b[0], b[3]))
boxes_image, boxes = draw_boxes(image, max_height) 
boxes_image.save(IMAGE_SAVE_PATH + f"custom_boxes_{READ_FROM[:-4]}.png")

print("Getting symbol similarity threhsolds...")
SIMILARITY_THRESHOLDS = get_similarity_thresholds()

print("Processing image...")
blank_image = image.copy()
blank_pixels = blank_image.load()
rooms = process_image(boxes, blank_pixels) 

print("Getting rectangles...")
loaded_pixels, rectangles = set(), []
for x in range(WIDTH):
    if WIDTH - x % 100 == 0:
        print(width - x, "left")
    for y in range(HEIGHT):
        if (x, y) in loaded_pixels or blank_pixels[x, y] == (255, 255, 255): # Skip over looked-at pixels or white pixels
            continue

        found, min_x, max_x, min_y, max_y = find_rectangles(blank_pixels, x, y, set(), x, x, y, y)
        x_len = max_x - min_x
        y_len = max_y - min_y

        loaded_pixels.update(found)
        rectangles.append([min_x, min_y, min_x, max_y, x_len])
            
blank_image.save(IMAGE_SAVE_PATH + f"blank_map_{READ_FROM[:-4]}.png")

blank_image = simplify(rooms, blank_image)
blank_pixels = blank_image.load()

map = [[1 if blank_pixels[x, y] == (0, 0, 0) else 0 for y in range(HEIGHT)] for x in range(WIDTH)]

with open(IMAGE_SAVE_PATH + f"render_{READ_FROM[:-4]}.json", "w") as f:
    json.dump({"rooms": rooms, "points": rectangles, "map": map}, f, indent = 4) 
    
print("Entire program took", round(time.perf_counter() - start_time, 3), "seconds.")