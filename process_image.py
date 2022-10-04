import cv2 as cv
import enchant
import imagehash
import numpy as np
import pickle
import pytesseract
import time
import tkinter as tk
from drawing import draw_boxes, draw_square, image_to_bw, remove_box
from image_similarity_measures.quality_metrics import rmse
from PIL import Image, ImageTk, ImageDraw, ImageFont

start_time = time.perf_counter()

USING_TESSERACT = False
SHOW_IMAGES = False

CONFIDENCE_LEVEL = 69
UPPER_CONFIDENCE_LEVEL = 90
IMAGE_SAVE_PATH = "images/"
FILE_NAME = IMAGE_SAVE_PATH + "practice_map.jpg"
DIST_BETWEEN_LETTERS = 15
DIST_FOR_SPACE = 4
Y_THRESHOLD = 6
BW_THRESHOLD = 150 # Values less than this will become black
RESIZE = 2
PADDING = 3
RMSE_THRESHOLD = 0.035
# SYMBOLS = ["door", "signage", "stairs"]
SYMBOLS = ["door"]

if USING_TESSERACT:
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract"
    box_stats = {}
else:
    with open('boxes.pickle', 'rb') as handle:
        box_stats = pickle.load(handle)

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

        # hash0 = imagehash.average_hash(Image.fromarray(symbol_image))
        # hash1 = imagehash.average_hash(Image.fromarray(resized_image))

        # m = abs(hash0 - hash1)

        # if m < 5:
        #     return symbol

        m = rmse(symbol_image, resized_image).item()

        print("M is:", m)

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


def predict_name(x1, x2, y1, y2, single_char = True, has_spaces = False, symbols = {}):
    """
    Uses box coordinates to create a gray-scale PIL image specifically of that region (with padding)
    And checks if that image is a symbol from key, and if not uses pytesseract to 
    determine what character(s) are in it along with their respective confidences.
    """

    global box_stats

    # Creating image of that specific area

    potential_image = create_image_from_box(x1, x2, y1, y2, PADDING)
    potential_pixels = potential_image.load()

    # display_image = image.copy()
    # p = display_image.load()

    # Remove symbols from image before running pytesseract on it

    for box in symbols.keys():
        bx1, bx2, by1, by2 = box

        for x in range(bx1, bx2):
            for y in range(by1, by2):
                potential_pixels[x - x1 + PADDING, y - y1 + PADDING] = 255
                # p[x, y] = (255, 255, 255)

    # draw_square(p, x1, x2, y1, y2, (0, 0, 255))
    # display_image = display_image.crop((max(0, x1 - 50),  max(0, y1 - 50), min(WIDTH, x2 + 50), min(HEIGHT, y2 + 50)))
    # display_image = display_image.resize((display_image.size[0] * RESIZE, display_image.size[1] * RESIZE), Image.Resampling.LANCZOS)
    # cv_image = np.array(display_image)
    # cv.imshow("Looking at image:", cv_image)
    # cv.waitKey(2000)
    # cv.destroyAllWindows()

    # Run pytesseract (or saved data) on image    

    detected = ""
    confidence = -1

    if USING_TESSERACT:
        if single_char:
            predict = pytesseract.image_to_data(
                potential_image, 
                config=("-c tessedit"
                        "_char_whitelist=abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
                        " --psm 10"
                        " -l osd"), 
                output_type="data.frame")   

            predict = predict[predict["conf"] != -1]
            
            try:
                detected = str(predict["text"].iloc[0])[0]
                confidence = predict["conf"].iloc[0]
            except:
                pass   

        else: # Full word
            if has_spaces:
                config = "--oem 3 -l eng --psm 7"
            else:
                config = "--oem 3 -l eng --psm 7 -c tessedit_char_whitelist=|-abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"

            predict = pytesseract.image_to_data(
                potential_image, config = config, output_type="data.frame")          
            predict = predict[predict["conf"] != -1]

            try:
                detected = " ".join([str(int(a)) if isinstance(a, float) else str(a) for a in predict["text"].tolist()])
                confidence = predict["conf"].iloc[0]                  
            except:
                pass

            print("Detected within predict_name:", detected, "with confidence:", confidence)

            if confidence == 0:
                confidence = 89.0

            # "Reinsert" symbols into detected string

            for s in symbols.values():
                symbol, index = s
                detected = detected[:index] + symbol + detected[index:] 

        box_stats[(x1, x2, y1, y2)] = (detected, confidence)

    else: # Use pickle file for efficiency & since pytesseract doesn't work on school laptop
        detected = box_stats[(x1, x2, y1, y2)][0]
        confidence = box_stats[(x1, x2, y1, y2)][1]  

    return detected, confidence


def generate_name(cur_box, used_boxes, detected_name, has_spaces, symbols):
    """
    Recursive function using the current box, used boxes, and detected name
    so far to check neighboring pixels and try to construct the full room name.
    """

    ax1, ax2, ay1, ay2 = cur_box
    symbol = detect_if_symbol(ax1, ax2, ay1, ay2)    
    if symbol:
        symbols[cur_box] = (symbol, len(detected_name))

    used_boxes.append(cur_box)
    detected_name.append(cur_box)   

    for box in boxes:
        if box in used_boxes:
            continue

        bx1, _, by1, by2 = box
            
        if abs((ay1+ay2)/2 - (by1+by2)/2) <= Y_THRESHOLD and abs(ax2 - bx1) <= DIST_BETWEEN_LETTERS and all(pixels[x, ay2] != (0, 0, 0) for x in range(ax2, bx1)): # Part of same word
            if abs(ax2 - bx1) >= DIST_FOR_SPACE: 
                has_spaces = True               
            
            used_boxes, detected_name, has_spaces, symbols = generate_name(box, used_boxes, detected_name, has_spaces, symbols)
            break

    return used_boxes, detected_name, has_spaces, symbols


def process_image(boxes, pixels):
    """
    Process the entire image to identify all integral parts using already-identified boxes.
    """

    d = enchant.Dict("en_US")

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
    rooms = []

    for box in boxes:    
        if box in used_boxes:
            continue

        print("Starting to look at new word...")

        used_boxes, detected_name, has_spaces, symbols = generate_name(box, used_boxes, detected_name = [], has_spaces = False, symbols = {})

        print("After generated named, detected_name:", detected_name)
        print("After generated name symbols:", symbols)

        if len(detected_name) == 1 and symbols: # If it's a singular symbol
            s = list(symbols.values())[0][0]
            print("Symbol:", s)
            rooms.append((s, (detected_name[0][0], detected_name[0][3])))
            remove_box(pixels, detected_name[0][0], detected_name[0][1], detected_name[0][2], detected_name[0][3])
        else: # Predict full room name

            # Get bounding box of entire room name

            first = detected_name[0]
            last = detected_name[-1]
            y1, y2 = float("inf"), float("-inf")        
            for i in detected_name:
                y1 = min(y1, i[2])
                y2 = max(y2, i[3])

            # Try to predict room name

            if len(detected_name) == 1:
                single_char = True
            else:
                single_char = False

            full_word, confidence = predict_name(first[0], last[1], y1, y2, single_char, has_spaces, symbols)
            full_word.replace(",", "")

            if "|" in full_word: # If mistook a wall for a "|", split it along there
                if len(full_word) == 1:
                    continue

                pipe = full_word.index("|")
                full_word1 = full_word[:pipe]
                full_word2 = full_word[pipe + 1:]
                print("Full word:", full_word1)
                print("Full word:", full_word2)

                for i, b in enumerate(detected_name):
                    if i != pipe:
                        remove_box(pixels, b[0], b[1], b[2], b[3])
                        if i == 0:
                            rooms.append((full_word1, (b[0], b[3])))
                        elif i == pipe + 1:
                            rooms.append((full_word2, (b[0], b[3])))
            elif confidence >= CONFIDENCE_LEVEL:
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

                print("Full name:", full_word)
                rooms.append((full_word, (first[0], y2)))
                remove_box(pixels, first[0], last[1], y1, y2)

            elif len(detected_name) > 1: # Go individually

                label = []

                for b in detected_name:
                    if b in symbols:
                        label.append(symbols[b][0])
                    elif (pred := predict_name(b[0], b[1], b[2], b[3]))[1] >= CONFIDENCE_LEVEL:
                        label.append(pred[0])
                    else:
                        label.append("*")

                label = "".join(label)

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

                # Remove extra *'s which are most probably walls

                if len(label) > 1 and label[0] == "*" and label[1] != "*":
                    label = label[1:]
                if len(label) > 1 and label[-2] != "*" and label[-1] == "*":
                    label = label[:-1]            

                label = label.capitalize() 
                if all(i != "*" for i in label):   
                    print("Each character:", label)   
                    rooms.append((label, (first[0], y2)))         
            
        if SHOW_IMAGES:
            if confidence < CONFIDENCE_LEVEL:
                if all(i == "*" for i in label):
                    continue
                text = f"Each: {label}"
            else:
                text = f"Full: {full_word}"

                if confidence == 89.0:
                    text += " But 100"
            
            image3 = Image.open(FILE_NAME)
            pixels3 = image3.load()
            for i in detected_name:
                x1, x2, y1, y2 = i
                font = ImageFont.truetype("arial", 45)
                draw_square(pixels3, x1, x2, y1, y2, (255, 0, 0))

            if x1 + 200 > WIDTH:
                x1 -= 200
            
            ImageDraw.Draw(image3).text((x1, y1), text, (255, 0, 0), font = font)

            tk_image = ImageTk.PhotoImage(image3.resize((1200, 700)))
            image_label.configure(image = tk_image)
            image_label.pack()
            root.update()
            time.sleep(1.5)

    a = sorted(rooms, key = lambda i: int(i[0]) if i[0].isnumeric() else 0)
    return [[i[0], i[1][0], i[1][1]] for i in a]


image = Image.open(FILE_NAME)

print("Converting to black and white...")
image = image_to_bw(image, BW_THRESHOLD)
pixels = image.load()
WIDTH, HEIGHT = image.size[0], image.size[1]
# image.save(IMAGE_SAVE_PATH + "black_and_white.png")
	
print("Drawing boxes...")
boxes_image, boxes, walls = draw_boxes(image) 
boxes_image.save(IMAGE_SAVE_PATH + "custom_boxes.png")

blank_image = image.copy()
blank_pixels = blank_image.load()

print("Processing image...")
rooms = process_image(boxes, blank_pixels) 
print("\n\n\n", rooms)   
# blank_image.show()
blank_image.save(IMAGE_SAVE_PATH + "blank_map.png")

if USING_TESSERACT:
    print("Saving updated boxes...")
    with open('boxes.pickle', 'wb') as handle:
        pickle.dump(box_stats, handle, protocol=pickle.HIGHEST_PROTOCOL)

    if not SHOW_IMAGES:
        print("Entire program took", round(time.perf_counter() - start_time, 3), "seconds.")

"""
To-do list:

Combine pixels into lines

Repeat symbol detection for all symbols (right now only doing doors)
Detect text wrapping
Detect symbols that are next to walls
- If found full name box that is not a real word, check left and right side
    - Try to go all the way down that direction (allowing to go up and down)
    - If vertical distance is greater than certain threshold, assume
    that distance is a vertical wall and ignore all pixels with the same x-coord
    - Splice the rest and create a bounding box on that region, then retry with full word
    including that new box

    - Make sure to add precaution to combine all letters that the wall may have interfered with
    - For example, Chem might only be Ch + em

At the end go throughout the entire image and try to pick up any extra symbols of that specific size
(may be time-consuming, so might not do it)

Form outer walls, and walls of classrooms
- Maybe navigate based on the fact you can't go near region of certain room name (full of numbers)
to try to avoid navigating through classrooms

Check all floors to see where images match up
- Match up through stairs
"""