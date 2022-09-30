import colorsys 
import cv2 as cv
import enchant
import numpy as np
import pickle
import pytesseract
import sys
import time
import tkinter as tk
from image_similarity_measures.quality_metrics import rmse
from PIL import Image, ImageTk, ImageDraw, ImageFont
from random import random

start_time = time.perf_counter()

CONFIDENCE_LEVEL = 69
UPPER_CONFIDENCE_LEVEL = 90
IMAGE_SAVE_PATH = "images/"
FILE_NAME = IMAGE_SAVE_PATH + "practice_map.jpg"
DIST_BETWEEN_LETTERS = 15
DIST_FOR_SPACE = 4
Y_THRESHOLD = 6
RESIZE = 2
PADDING = 3
RMSE_THRESHOLD = 0.02
SYMBOLS = ["door"]

USING_TESSERACT = False
SHOW_IMAGES = False

sys.setrecursionlimit(10000) # We don't talk about this line

if USING_TESSERACT:
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract"
    box_stats = {}
else:
    with open('boxes.pickle', 'rb') as handle:
        box_stats = pickle.load(handle)

d = enchant.Dict("en_US")

print("Loading text file of english words...")

with open("words_alpha.txt") as file:
    ENGLISH_WORDS = set(file.read().split())


def flood(x, y, found, min_x, max_x, min_y, max_y):
    """
    Recursively go through image to check neighboring pixels to form blobs
    of connected pixels as well as min & max for x & y.
    """

    try: # Crude way of making sure pixel is not outside of image
        pixels[x, y]
    except:
        return found, min_x, max_x, min_y, max_y

    if pixels[x, y] == (0, 0, 0) and (x, y) not in found: # Found unvisited black pixel
        found.add((x, y))

        if x < min_x:
            min_x = x
        elif x > max_x:
            max_x = x

        if y < min_y:
            min_y = y
        elif y > max_y:
            max_y = y

        for x1 in range(-1, 2):
            for y1 in range(-1, 2):
                # print(f"({x}, {y}) calling:", (x + x1, y + y1))
                found, min_x, max_x, min_y, max_y = flood(x + x1, y + y1, found, min_x, max_x, min_y, max_y)

    return found, min_x, max_x, min_y, max_y

def draw_square(pixels, min_x, max_x, min_y, max_y, rgb):
    """
    Draws a square by calling draw_line() for each side, because too lazy to integrate :D
    """

    draw_line(pixels, min_x, max_x, min_y, min_y, rgb)
    draw_line(pixels, max_x, max_x, min_y, max_y, rgb)
    draw_line(pixels, min_x, max_x, max_y, max_y, rgb)
    draw_line(pixels, min_x, min_x, min_y, max_y, rgb)


def draw_line(pixels, x1, x2, y1, y2, rgb):
    """
    Draws a line on the PIL image given the start and end coordinates,
    as well as the rgb color.
    """
    
    for x in range(x1, x2 + 1):
        for y in range(y1, y2 + 1):
            try: # Crude way of making sure pixel is not outside of image
                pixels[x, y] = rgb
            except:
                pass


def image_to_black_and_white(pixels):
    """
    Converts a PIL image to only black and white pixels.
    """

    for x in range(WIDTH):
        for y in range(HEIGHT):
            r, g, b = pixels[x, y]
            if 0.2126*r + 0.7152*g + 0.0722*b < 150: # Check if pixel is relatively dark
                pixels[x, y] = (0, 0, 0)
            else:
                pixels[x, y] = (255, 255, 255)


def draw_boxes(pixels):
    """
    Goes throughout a PIL image to draw boxes around potential candidates 
    for characters (using approximate size / shape).
    """

    loaded_pixels, boxes, walls = set(), set(), set()
    for x in range(WIDTH):
        for y in range(HEIGHT):
            if (x, y) in loaded_pixels or pixels[x, y] == (255, 255, 255): # Skip over looked-at pixels or white pixels
                continue

            found, min_x, max_x, min_y, max_y = flood(x, y, set(), x, x, y, y)
            x_len = max_x - min_x
            y_len = max_y - min_y

            loaded_pixels.update(found)

            if 5 < len(found) and len(found) < 500 and x_len < 30 and y_len > 3 and y_len < 30: # Is appropriate size for character
                # print(f"Drawing box, {x_len} by {y_len} ==> {len(found)}")
                min_x -= 1
                max_x += 1
                min_y -= 1 
                max_y += 1
                boxes.add((min_x, max_x, min_y, max_y))
                h,s,l = random(), 0.5 + random()/2.0, 0.4 + random()/5.0
                rgb = tuple([int(256*i) for i in colorsys.hls_to_rgb(h,l,s)])    
                draw_square(pixels, min_x, max_x, min_y, max_y, rgb)  
            else: # Should be part of walls
                walls.update(found)

    return sorted(list(boxes), key = lambda b: (b[0], b[3])), list(walls)


def detect_if_symbol(x1, x2, y1, y2):
    """
    Given box of potential symbol, determine whether that image
    is indeed a symbol and return which symbol it is (according to key)
    """

    image = create_image_from_box(x1, x2, y1, y2, 0)

    for symbol in SYMBOLS:
        symbol_image = cv.imread(IMAGE_SAVE_PATH + symbol + ".png")
        width, height = symbol_image.shape[1], symbol_image.shape[0]
        dim = (width, height)

        opencv_image = cv.cvtColor(np.array(image), cv.COLOR_GRAY2RGB)
        resized_image = cv.resize(opencv_image, dim, interpolation = cv.INTER_AREA)
        m = rmse(symbol_image, resized_image).item()

        if m < RMSE_THRESHOLD:
            return symbol

    return ""


def create_image_from_box(x1, x2, y1, y2, padding):
    """
    Given box coordinates, return image generated around that box 
    (from initial map) with or without padding
    """

    image2 = Image.new("RGB", (x2 - x1 + 1 + 2*padding, y2 - y1 + 1 + 2*padding), color = "white")
    pixels2 = image2.load()
    for x in range(x1 + 1, x2):
        for y in range(y1 + 1, y2):
            pixels2[x - x1 + padding, y - y1 + padding] = pixels[x, y]

    image2 = image2.convert("L")
    return image2


def predict_char(x1, x2, y1, y2, single_char = True, has_spaces = False, symbols = {}):
    """
    Uses box coordinates to create a gray-scale PIL image specifically of that region (with padding)
    And checks if that image is a symbol from key, and if not uses pytesseract to 
    determine what character(s) are in it along with their respective confidences.
    """

    global box_stats

    # Creating image of that specific area

    image2 = create_image_from_box(x1, x2, y1, y2, PADDING)
    pixels2 = image2.load()

    # TODO: Remove symbols from image

    for box, s in symbols.items():
        symbol, index = s
        bx1, bx2, by1, by2 = box

        for x in range(bx1, bx2):
            for y in range(by1, by2):
                pixels2[x - x1, y - y1] = 0

    image3 = image2.resize((image2.size[0]*RESIZE,image2.size[1]*RESIZE), Image.Resampling.LANCZOS)

    # display_image = image.copy()
    # p = display_image.load()
    # draw_square(p, x1, x2, y1, y2, (255, 0, 0))
    # display_image = display_image.crop((max(0, x1 - 50),  max(0, y1 - 50), min(WIDTH, x2 + 50), min(HEIGHT, y2 + 50)))
    # display_image = display_image.resize((display_image.size[0] * RESIZE, display_image.size[1] * RESIZE), Image.Resampling.LANCZOS)

    # cv_image = np.array(display_image)
    # cv.imshow("Window", cv_image)
    # cv.waitKey(1250)
    # cv.destroyAllWindows()

    # Check if the image is of a door

    symbol = detect_if_symbol(x1, x2, y1, y2)

    if symbol:
        return symbol  + " ", 100.0

    # Run pytesseract (or saved data) on image    

    detected_char1 = ""
    confidence1 = -2   

    if USING_TESSERACT:
        if single_char:
            predict = pytesseract.image_to_data(
            image2, config=("-c tessedit"
                            "_char_whitelist=abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
                            " --psm 10"
                            " -l osd"
                            " "), output_type="data.frame")   

            predict = predict[predict["conf"] != -1]
            
            try:
                detected_char = str(predict["text"].iloc[0])[0]
                confidence = predict["conf"].iloc[0]   
            except:
                detected_char = ""
                confidence = -1

            if confidence < CONFIDENCE_LEVEL: 

                predict1 = pytesseract.image_to_data(
                image3, config=("-c tessedit"
                                "_char_whitelist=abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
                                " --psm 10"
                                " -l osd"
                                " "), output_type="data.frame")    

                predict1 = predict1[predict1["conf"] != -1]

                try:
                    detected_char1 = str(predict1["text"].iloc[0])[0]
                    confidence1 = predict1["conf"].iloc[0]   
                except:
                    detected_char1 = ""
                    confidence1 = -1 
        else: # Full word

            if has_spaces:
                config = "--oem 3 -l eng --psm 7"
            else:
                config = "--oem 3 -l eng --psm 8 -c tessedit_char_whitelist=|-abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"

            predict = pytesseract.image_to_data(
                image2, config = config, output_type="data.frame")          
            predict = predict[predict["conf"] != -1]

            try:
                detected_char = predict["text"].tolist()
                detected_char = " ".join([str(int(a)) if isinstance(a, float) else str(a) for a in detected_char])
                confidence = predict["conf"].iloc[0]                  
            except:
                detected_char = ""
                confidence = -1
            
            if confidence < CONFIDENCE_LEVEL:
                predict1 = pytesseract.image_to_data(
                    image3, config = config, output_type="data.frame")
                predict1 = predict1[predict1["conf"] != -1]

                try:
                    detected_char1 = predict1["text"].tolist()                
                    detected_char1 = " ".join([str(int(a)) if isinstance(a, float) else str(a) for a in detected_char1])
                    confidence1 = predict1["conf"].iloc[0]                  
                except:
                    detected_char1 = ""
                    confidence1 = -1 

            if confidence == 0:
                confidence = 89.0
            if confidence1 == 0:
                confidence1 = 89.0
    else:
        detected_char = box_stats[(x1, x2, y1, y2, 0)][0]
        confidence = box_stats[(x1, x2, y1, y2, 0)][1]
        detected_char1 = box_stats[(x1, x2, y1, y2, 1)][0]
        confidence1 = box_stats[(x1, x2, y1, y2, 1)][1]

    box_stats[(x1, x2, y1, y2, 0)] = (detected_char, confidence)
    box_stats[(x1, x2, y1, y2, 1)] = (detected_char1, confidence1)

    if confidence1 > confidence1:
        confidence = confidence1
        detected_char = detected_char1

    if confidence > CONFIDENCE_LEVEL:
        name = detected_char.replace("|", " pipe ")
        image2.save(f"extras/{name}_{confidence}.png")

    return detected_char, confidence


def generate_name(cur_box, used_boxes, detected_name, has_spaces = False):
    """
    Recursive function using the current box, used boxes, and detected name
    so far to check neighboring pixels and try to construct the full room name.
    """

    ax1, ax2, ay1, ay2 = cur_box
    symbols = {}
    used_boxes.append(cur_box)
    detected_name.append(cur_box)
    symbol = detect_if_symbol(ax1, ax2, ay1, ay2)
    if symbol:
        symbols[cur_box] = (symbol, len(used_boxes))

    for box in boxes:
        if box in used_boxes:
            continue

        bx1, _, by1, by2 = box
            
        if abs((ay1+ay2)/2 - (by1+by2)/2) <= Y_THRESHOLD and abs(ax2 - bx1) <= DIST_BETWEEN_LETTERS and all(pixels[x, ay2] != (0, 0, 0) for x in range(ax2, bx1)): # Part of same word
            if abs(ax2 - bx1) >= DIST_FOR_SPACE: 
                has_spaces = True               
            
            used_boxes, detected_name, has_spaces, symbols = generate_name(box, used_boxes, detected_name, has_spaces)
            break

    return used_boxes, detected_name, has_spaces, symbols


def remove_box(pixels, x1, x2, y1, y2):
    """
    Replaces all pixels with white within a certain box region
    """
    for x in range(x1, x2):
        for y in range(y1, y2):
            pixels[x, y] = (255, 255, 255)


def process_image(boxes, pixels):
    """
    Process the entire image to identify all integral parts using already-identified boxes.
    """

    if SHOW_IMAGES:
        root = tk.Tk()
        root.attributes("-fullscreen", True)
        root.bind("<Escape>", lambda event: root.attributes("-fullscreen",
                                    not root.attributes("-fullscreen")))
        image_label = tk.Label(root)
        caption_label = tk.Label(root)
        caption_label.config(font = ("Arial", 60))
        image_label.pack()
        caption_label.pack()
        root.update()

    used_boxes = []    
    room_names = []

    for box in boxes:    
        if box in used_boxes:
            continue

        used_boxes, detected_name, has_spaces, symbols = generate_name(box, used_boxes, [])
        label = ""

        # Use full word

        first = detected_name[0]
        last = detected_name[-1]
        y1, y2 = float("inf"), float("-inf")        
        for i in detected_name:
            y1 = min(y1, i[2])
            y2 = max(y2, i[3])

        full_word, confidence = predict_char(first[0], last[1], y1, y2, False, has_spaces, symbols)
        full_word.replace(",", "")

        if "|" in full_word:
            pipe = full_word.index("|")
            full_word1 = full_word[:pipe]
            full_word2 = full_word[pipe + 1:]
            print("Full word:", full_word1)
            print("Full word:", full_word2)

            room_names.append(full_word1)
            room_names.append(full_word2)
            continue

            # TODO: Remove box here

        if confidence >= CONFIDENCE_LEVEL:
            if len(full_word) == 1 and confidence < UPPER_CONFIDENCE_LEVEL: # Mis-identified character
                print("mis identified")
                continue

            for word in full_word.split(" "):
                if word == "":
                    continue

                if not d.check(word):
                    suggestions = [i for i in d.suggest(word) if len(i) == len(word)]
                    if len(suggestions) == 1:
                        full_word = suggestions[0]
                    #     print("Suggestions:", suggestions)
                    # elif len(suggestions) > 1:
                    #     print(f"{len(suggestions)} suggestions, not displaying them...")

            print("Full name:", full_word)
            room_names.append(full_word)
            remove_box(pixels, first[0], last[1], y1, y2)

        elif len(detected_name) > 1: # Go individually

            label = "".join([pred[0] if (pred := predict_char(b))[1] >= CONFIDENCE_LEVEL else "*" for b in detected_name])

            for b in detected_name:
                remove_box(pixels, b[0], b[1], b[2], b[3])

            # Change l's and i's to 1's in room names
            change = True
            is_start = True
            for i in range(len(label)):
                if label[i] in "lIi":
                    continue
                elif label[i].isnumeric() and is_start:
                    is_start = False
                elif not is_start and not label[i].isnumeric():
                    change = False

            if change:
                label = "".join([i if i not in "lIi" else "1" for i in label])

            # Change 0's to O's in room names

            if all(i == "0" or i.isalpha() or i == "*" for i in label) and len(label) > 1:
                label = "".join([i if i != "0" else "o" for i in label])

            # Change O's to 0's in room names

            if all(i in "oO" or i.isnumeric() or i == "*" for i in label) and len(label) > 1:
                label = "".join([i if i not in "oO" else "0" for i in label])

            if len(label) > 1 and label[0] == "*" and label[1] != "*":
                label = label[1:]
            if len(label) > 1 and label[-2] != "*" and label[-1] == "*":
                label = label[:-1]            

            label = label.capitalize() 
            if any(i != "*" for i in label):   
                print("Each character:", label)   
                room_names.append(label)         
        
        if SHOW_IMAGES:
            if confidence < CONFIDENCE_LEVEL:
                if all(i == "*" for i in label):
                    continue
                text = f"Each: {label}"
            else:
                text = f"Full: {full_word}"

                if confidence == 89.0:
                    text += " But 100"

            text += f" {has_spaces}"[:2]
            
            image3 = Image.open(FILE_NAME)
            pixels3 = image3.load()
            for i in detected_name:
                x1, x2, y1, y2 = i
                font = ImageFont.truetype("arial", 45)
                draw_square(pixels3, x1, x2, y1, y2, (255, 0, 0))

            if x1 + 200 > WIDTH:
                x1 -= 200
            
            ImageDraw.Draw(image3).text((x1, y1), text, color, font = font)

            tk_image = ImageTk.PhotoImage(image3.resize((1000, 600)))
            image_label.configure(image = tk_image)
            image_label.pack()
            root.update()
            time.sleep(1.5)

    return sorted(room_names, key = lambda i: int(i) if i.isnumeric() else 0)


image = Image.open(FILE_NAME)
pixels = image.load()
WIDTH, HEIGHT = image.width, image.height

print("Converting to black and white...")
image_to_black_and_white(pixels)
# image.save(IMAGE_SAVE_PATH + "black_and_white.png")

	
print("Drawing boxes...")
boxes_image = image.copy()
blank_image = image.copy()
boxes_pixels = boxes_image.load()
blank_pixels = blank_image.load()
boxes, walls = draw_boxes(boxes_pixels) 
with open("list_of_points.txt", "w") as f:
    for i in walls:
        f.write(f"{i[0]} {i[1]} 0\n")

# boxes_image.save(IMAGE_SAVE_PATH + "custom_boxes.png")

print("Processing image...")
room_names = process_image(boxes, blank_pixels) 
print("\n\n\n", room_names)   
# blank_image.show()
blank_image.save(IMAGE_SAVE_PATH + "blank_map.png")

if USING_TESSERACT:
    print("Saving updated boxes...")
    with open('boxes.pickle', 'wb') as handle:
        pickle.dump(box_stats, handle, protocol=pickle.HIGHEST_PROTOCOL)

    if not SHOW_IMAGES:
        print("Entire program took", round(time.perf_counter() - start_time, 3), "seconds.")