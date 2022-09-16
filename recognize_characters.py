import colorsys 
import cv2 as cv
import enchant
import numpy as np
import pickle
import pytesseract
import re 
import sys
import time
import tkinter as tk
from image_similarity_measures.quality_metrics import rmse
from PIL import Image, ImageTk, ImageDraw, ImageFont
from random import random

CONFIDENCE_LEVEL = 65
IMAGE_SAVE_PATH = "images/"
FILE_NAME = IMAGE_SAVE_PATH + "practice_map.jpg"
DIST_BETWEEN_LETTERS = 15
Y_THRESHOLD = 4

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

    loaded_pixels = set()
    boxes = set()
    for x in range(WIDTH):
        for y in range(HEIGHT):
            if (x, y) in loaded_pixels or pixels[x, y] == (255, 255, 255): # Skip over looked-at pixels or white pixels
                continue

            found, min_x, max_x, min_y, max_y = flood(x, y, set(), x, x, y, y)
            x_len = max_x - min_x
            y_len = max_y - min_y

            loaded_pixels.update(found)

            if 10 < len(found) and len(found) < 500 and x_len < 30 and y_len > 5 and y_len < 30: # Is appropriate size for character
                # print(f"Drawing box, {x_len} by {y_len} ==> {len(found)}")
                min_x -= 1
                max_x += 1
                min_y -= 1 
                max_y += 1
                boxes.add((min_x, max_x, min_y, max_y))
                h,s,l = random(), 0.5 + random()/2.0, 0.4 + random()/5.0
                rgb = tuple([int(256*i) for i in colorsys.hls_to_rgb(h,l,s)])            
                draw_line(pixels, min_x, max_x, min_y, min_y, rgb)
                draw_line(pixels, max_x, max_x, min_y, max_y, rgb)
                draw_line(pixels, min_x, max_x, max_y, max_y, rgb)
                draw_line(pixels, min_x, min_x, min_y, max_y, rgb)

    return sorted(list(boxes), key = lambda b: (b[0], b[3]))

def predict_char(box, single_char = True):
    """
    Uses box coordinates to create a gray-scale PIL image specifically of that region (with padding)
    And checks if that image is of a door, and if not uses pytesseract to 
    determine what character(s) are in it along with their respective confidences.
    """

    global box_stats
    x1, x2, y1, y2 = box

    # Creating image of that specific area

    padding = 3
    image2 = Image.new("RGB", (x2 - x1 + 1 + 2*padding, y2 - y1 + 1 + 2*padding), color = "white")
    pixels2 = image2.load()
    for x in range(x1 + 1, x2):
        for y in range(y1 + 1, y2):
            pixels2[x - x1 + padding, y - y1 + padding] = pixels[x, y]
    image2 = image2.convert("L")
    
    # Check if the image is of a door

    door_image = cv.imread(IMAGE_SAVE_PATH + "door.png")
    width, height = door_image.shape[1], door_image.shape[0]
    dim = (width, height)

    opencv_image = cv.cvtColor(np.array(image2), cv.COLOR_GRAY2RGB)
    resized_image = cv.resize(opencv_image, dim, interpolation = cv.INTER_AREA)
    measure = rmse(door_image, resized_image).item()
    m = round(measure, 3)

    if m < 0.02:
        image2.save(f"extras/DOOR_{x1}{x2}{y1}{y2}_{m}.png")
        return "Door ", 100.0

    # Run pytesseract (or saved data) on image        

    if USING_TESSERACT:
        if single_char:
            predict = pytesseract.image_to_data(
            image2, config=("-c tessedit"
                            "_char_whitelist=abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
                            " --psm 10"
                            " -l osd"
                            " "), output_type="data.frame")        
            predict = predict[predict.conf != -1]
            try:
                detected_char = str(predict["text"].iloc[0])[0]
                confidence = predict["conf"].iloc[0]   
            except:
                detected_char = ""
                confidence = -1 
        else: # Full word
            predict = pytesseract.image_to_data(
                image2, config=("-c tessedit"
                                "_char_whitelist=abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"),
                                output_type="data.frame")
            predict = predict[predict.conf != -1]
            try:
                detected_char = " ".join(predict["text"].tolist())
                confidence = predict["conf"].iloc[0]   
            except:
                detected_char = ""
                confidence = -1 
    else:
        detected_char = box_stats[(x1, x2, y1, y2)][0]
        confidence = box_stats[(x1, x2, y1, y2)][1]

    box_stats[(x1, x2, y1, y2)] = (detected_char, confidence)

    if confidence > CONFIDENCE_LEVEL:
        image2.save(f"extras/{detected_char}_{confidence}.png")

    return detected_char, confidence


def generate_names(cur_box, used_boxes, detected_name):
    """
    Recursive function using the current box, used boxes, and detected name
    so far to check neighboring pixels and try to construct the full room name.
    """

    used_boxes.append(cur_box)
    detected_name.append(cur_box)
    _, ax2, _, ay2 = cur_box

    for box in boxes:
        if box in used_boxes:
            continue
            
        bx1, _, _, by2 = box

        if abs(ay2 - by2) <= Y_THRESHOLD and abs(ax2 - bx1) <= DIST_BETWEEN_LETTERS and all(pixels[x, ay2] != (0, 0, 0) for x in range(ax2, bx1)): # Part of same word
            used_boxes, detected_name = generate_names(box, used_boxes, detected_name)
            break

    return used_boxes, detected_name

def process_image(boxes):
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

    for box in boxes:    
        if box in used_boxes:
            continue

        used_boxes, detected_name = generate_names(box, used_boxes, [])
        label = ""

        # Use full word

        first = detected_name[0]
        last = detected_name[-1]
        y1, y2 = float("inf"), float("-inf")        
        for i in detected_name:
            y1 = min(y1, i[2])
            y2 = max(y2, i[3])
        full_word, confidence = predict_char((first[0], last[1], y1, y2), False)
        if confidence >= CONFIDENCE_LEVEL:
            print("Full name:", full_word)

        if confidence < CONFIDENCE_LEVEL: # Go individually

            label = "".join([pred[0] if (pred := predict_char(b))[1] >= CONFIDENCE_LEVEL else "." for b in detected_name])

            # Change lowercase L's to 1's in room names
            change = True
            is_start = True
            for i in range(len(label)):
                if label[i] == "l":
                    continue
                elif label[i].isnumeric() and is_start:
                    is_start = False
                elif not is_start and not label[i].isnumeric():
                    change = False
            if change:
                label = "".join([i if i != "l" else "1" for i in label])

            # Change 0's to O's in room names

            if all(i == "0" or i.isalpha() for i in label) and len(label) > 1:
                label = "".join([i if i != "0" else "o" for i in label])

            label = label.capitalize() 
            if any(i != "." for i in label):   
                print("Each character:", label)
        else:
            for word in full_word.split(" "):
                if word == "":
                    continue

                if not d.check(word):
                    suggestions = [i for i in d.suggest(word) if len(i) == len(word)]
                    print("Suggestions:", suggestions)
        
        if SHOW_IMAGES:
            if confidence < CONFIDENCE_LEVEL:
                if all(i == "." for i in label):
                    continue
                text = f"Each: {label}"
            else:
                text = f"Full: {full_word}"
            
            image3 = Image.open(FILE_NAME)
            pixels3 = image3.load()
            for i in detected_name:
                x1, x2, y1, y2 = i
                font = ImageFont.truetype("arial", 45)
                color = (255, 0, 0)
                draw_line(pixels3, x1, x2, y1, y1, color)
                draw_line(pixels3, x2, x2, y1, y2, color)
                draw_line(pixels3, x1, x2, y2, y2, color)
                draw_line(pixels3, x1, x1, y1, y2, color)
            
            ImageDraw.Draw(image3).text((x1, y1), text, color, font = font)

            tk_image = ImageTk.PhotoImage(image3.resize((1000, 600)))
            image_label.configure(image = tk_image)
            image_label.pack()
            root.update()
            time.sleep(1.5)

image = Image.open(FILE_NAME)
pixels = image.load()
WIDTH, HEIGHT = image.width, image.height

print("Converting to black and white...")
image_to_black_and_white(pixels)
# image.save(IMAGE_SAVE_PATH + "black_and_white.png")

print("Drawing boxes...")
boxes_image = image.copy()
boxes_pixels = boxes_image.load()
boxes = draw_boxes(boxes_pixels)  
# image.save(IMAGE_SAVE_PATH + "custom_boxes.png")

print("Processing image...")
process_image(boxes)    

with open('boxes.pickle', 'wb') as handle:
    pickle.dump(box_stats, handle, protocol=pickle.HIGHEST_PROTOCOL)

"""
Maybe ask user to take another picture of key if applicable?

BEFORE identifying boxes for characters, go through key
In example image, this includes:
- Restroom
- Elevator
- Signage
- Door

Save coordinates of each box identified to be a character
Go through each set of coordinates

    PERHAPS DO THIS AS PART OF THE LOOP BEFORE?

    Check if there are any coordinates to the right within a few pixels,
    and approximately on the same y-level:

    These should be part of the same word / room number
    Combine these to form room tag

    Find complete room names / door numbers that are not text-wrapped and combine them
    - Instead of just checking right, check below also and make sure there are no pixels between two boxes

    TRY TO DIFFERENTIATE BETWEEN SINGULAR ROOM NUMBERS LIKE 8 AND MISCLASSIFIED PIXELS

    TRY TO REMOVE DOTS ABOVE I's

    If it is a word
        Check if it is actually a word, if it isn't a word
            Check pixels in between letters and pixels along the side, if not connected?

            For example, in practice image:
            - Doesn't identify the first "i" in Einstein
            - Doesn't identify "N" and "o" in Neuro since those letters are connected to walls
            - Doesn't identify "h" in Chem since h is connected to wall

            POSSSIBLY CREATE A LIST OF "OFFICE" WORDS TO COMPARE WITH? may not be feasible for non-office buildings
             
            For example, in practice image:
            - Doesn't identify "A" and "d" in Admin, but catches "min"
"""

    
                    