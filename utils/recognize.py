import pytesseract
from utils.drawing import create_image_from_box, print_image_with_ascii, remove_box
from utils.symbols import detect_if_symbol

SIMILARITY_THRESHOLDS = []
ALLOWED_ROOM_NAMES = None
WIDTH, HEIGHT = None, None
MAX_FONT_SIZE = None
DIRECTORY = None
SYMBOL_FILES = None
TESSERACT_DIR_CONFIG = '--tessdata-dir "/cluster/2023abasto/local/share/tessdata"'

DIST_BETWEEN_LETTERS = 15
DIST_FOR_SPACE = 4
Y_THRESHOLD = 6
PADDING = 3
CHANGED = 200
CONFIDENCE_THRESHOLD = 60
UPPER_CONFIDENCE_THRESHOLD = 90

pytesseract.pytesseract.tesseract_cmd = r"/cluster/2023abasto/tesseract-5.1.0/tesseract"

stair_coords = []

def predict_name(pixels, x1, x2, y1, y2, single_char = True, has_spaces = False, symbols = {}, boxes = []):
    """
    Uses box coordinates to create a gray-scale PIL image specifically of that region (with padding)
    And checks if that image is a symbol from key, and if not uses pytesseract to 
    determine what character(s) are in it along with their respective confidences.
    """

    global box_stats

    # Creating image of that specific area

    potential_image = create_image_from_box(pixels, x1, x2, y1, y2, PADDING, boxes)
    potential_pixels = potential_image.load()

    # Remove symbols from image before running pytesseract on it

    for box in symbols.keys():
        bx1, bx2, by1, by2 = box

        for x in range(bx1, bx2):
            for y in range(by1, by2):   
                potential_pixels[x - x1 + PADDING, y - y1 + PADDING] = 255

    # Run pytesseract on image    

    detected = "" # Default results
    confidence = -1

    config = f"--oem 3 -l eng --psm 7 -c tessedit_char_whitelist=' 0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ' {TESSERACT_DIR_CONFIG}"

    print("Running with x1", x1, "x2", x2, "y1", y1, "y2", y2)

    p = pytesseract.image_to_data(
        potential_image, config = config, output_type=pytesseract.Output.DICT)   

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

    print("Detected:", detected, "with confidence:", confidence)

    # "Reinsert" symbols into detected string

    for s in symbols.values():
        symbol, index = s
        detected = detected[:index] + symbol.capitalize() + " " + detected[index:] # Make symbol look natural

    return detected, confidence


def generate_name(color_pixels, orig_pixels, cur_box, used_boxes, detected_name, has_spaces, symbols, boxes):
    """
    Recursive function using the current box, used boxes, and detected name so far
    to check neighboring pixels and try to construct the full room name.
    """

    ax1, ax2, ay1, ay2 = cur_box
    
    symbol = detect_if_symbol(color_pixels, SIMILARITY_THRESHOLDS, ax1, ax2, ay1, ay2, DIRECTORY, SYMBOL_FILES)    
    if symbol: # Check if bounding box contains a symbol
        symbols[cur_box] = (symbol, len(detected_name))
        
        if symbol.lower() in ["stair", "stairs", "stairway"]:
            stair_coords.append([(ax1 + ax2) // 2, (ay1 + ay2) // 2]) # Add it to stair coordinates to match up floors

    used_boxes.append(cur_box)
    detected_name.append(cur_box) # Add box to detected name

    for box in boxes: # Search for boxes that are possibly in same room name
        if box in used_boxes:
            continue

        bx1, bx2, by1, by2 = box
        
#         intersection = max(0, min(ax2, bx2) - max(ax1, bx1)) * max(0, min(ay2, by2) - max(ay1, by1))
            
        if(
            abs((ay1+ay2)/2 - (by1+by2)/2) <= Y_THRESHOLD and # Check if y-coord of centers of boxes are close together
            abs(ax2 - bx1) <= DIST_BETWEEN_LETTERS and # Check if boxes are close enough to be considered in same label
            abs(ay1 - by1) <= Y_THRESHOLD and by2 - by1 > 4 and # 
            all(orig_pixels[x, ay2] != (0, 0, 0) for x in range(ax2, bx1)) # No walls in between
          ): # Part of same word
            
            if abs(ax2 - bx1) >= DIST_FOR_SPACE:
                has_spaces = True               
            
            used_boxes, detected_name, has_spaces, symbols = generate_name(color_pixels, orig_pixels, box, used_boxes, detected_name, has_spaces, symbols, boxes)
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
            if i == 1: # Don't have duplicate
                y += 1
            while True:
                if pixels[x, y] == (0, 0, 0) and len(found) <= MAX_FONT_SIZE:
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
    
        if max_x - min_x > MAX_FONT_SIZE or max_y - min_y > MAX_FONT_SIZE:
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
    
    if not prev_x: # OpenCV weird bounding boxes not bounding correctly
        prev_x = [(y1 + y2) // 2] # Just set initial y to middle value
    
    x = start_x
    space = 0
    found = False
    cur_x = None

    while True: 
#         print("Find more x:", x, "prev_x:", prev_x, "cur_x:", cur_x, "space:", space, "found:", found)
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
            
        cur_x = flood_y(pixels, x, prev_x)     

        if len(cur_x) > MAX_FONT_SIZE: # Most likely a wall
            break
        elif len(cur_x) == 0: # Space
            space += 1
        elif len(cur_x) > 0: # Looking into potential char
            found = True 

            y1 = min(y1, min(cur_x))
            y2 = max(y2, max(cur_x))

        if space == 5 or x < 0 or x > WIDTH: # Only found empty space 
            return None
        
        if found:
            prev_x = cur_x  

    return x, y1, y2 # Return updated x boundary, and y-values
 

def process_image(boxes, color_image, bw_image, thresholds, allowed, max_height, directory, symbol_files):
    """
    Process the entire image to identify all integral parts using already-identified boxes.
    """
    
    blank_image = bw_image.copy()
    orig_pixels = blank_image.load()
    pixels = bw_image.load()
    color_pixels = color_image.load()
    
    global SIMILARITY_THRESHOLDS, ALLOWED_ROOM_NAMES, WIDTH, HEIGHT, MAX_FONT_SIZE, DIST_BETWEEN_LETTERS, DIST_FOR_SPACE, Y_THRESHOLD, DIRECTORY
    SIMILARITY_THRESHOLDS = thresholds
    ALLOWED_ROOM_NAMES = allowed
    WIDTH = blank_image.size[0]
    HEIGHT = blank_image.size[1]
    DIRECTORY = directory
    SYMBOL_FILES = symbol_files
    MAX_FONT_SIZE = max_height
    if MAX_FONT_SIZE >= 50: # Create bigger constants for bigger text
        DIST_BETWEEN_LETTERS = 20
        DIST_FOR_SPACE = 5
        Y_THRESHOLD = 12

    used_boxes, rooms, actual_boxes = [], [], []
    
    for box in boxes:    
        if box in used_boxes:
            continue

#         input("Starting to look at new word... [CLICK ENTER TO CONTINUE]")

        used_boxes, detected_name, has_spaces, symbols = generate_name(color_pixels, orig_pixels, box, used_boxes, detected_name = [], has_spaces = False, symbols = {}, boxes = boxes)
        first_char = detected_name[0]
        last_char = detected_name[-1]
        
        if len(detected_name) == 1 and symbols: # If it's a singular symbol
            x1, x2 = first_char[0], first_char[1]
            y1, y2 = first_char[2], first_char[3]
            print_image = create_image_from_box(orig_pixels, x1, x2, y1, y2, 0)
            print_image_with_ascii(print_image)
            s = list(symbols.values())[0][0]
            print("Symbol:", s)
            rooms.append((s, ((first_char[0] + first_char[1])//2, (first_char[2] + first_char[3])//2)))
            actual_boxes.append((x1, x2, y1, y2))
            remove_box(pixels, first_char[0], first_char[1], first_char[2], first_char[3])
        else: # Predict full room name
            
#             if len(detected_name) == 1: # Probably just a wall
#                 continue
                
            print("After generated name, detected_name:", detected_name, "symbols:", symbols)

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
            
            full_word, confidence = predict_name(pixels, x1, x2, y1, y2, single_char, has_spaces, symbols, detected_name)
            
            print_image = create_image_from_box(pixels, x1, x2, y1, y2, 0, detected_name)
            print_image_with_ascii(print_image)
            
            if full_word.isalpha() and len(full_word) > 4 and confidence > 30.0:
                suggestions = [i for i in ALLOWED_ROOM_NAMES.suggest(full_word) if len(i) == len(full_word) + 1]
                print("suggestions:", suggestions)
                if len(suggestions) == 1:
                    full_word = suggestions[0].capitalize()
                    rooms.append((full_word, ((first_char[0] + first_char[1])//2, (y1 + y2)//2)))
                    actual_boxes.append((x1, x2, y1, y2))
                    remove_box(pixels, x1, x2, y1, y2)
                    continue
                    
            if " " not in full_word and full_word and ALLOWED_ROOM_NAMES.check(full_word.lower()):
                print(f"{full_word} in dictionary so adding...")
                actual_boxes.append((x1, x2, y1, y2))
                rooms.append((full_word, ((first_char[0] + first_char[1])//2, (y1 + y2)//2)))
                remove_box(pixels, x1, x2, y1, y2)
                continue
            
            if confidence == 0 and ((full_word.isnumeric() and len(full_word) == len(detected_name) - 1) or symbols.keys()):
                print("Changed confidence because of pytessseract bug")
                confidence = CHANGED        
            
            if confidence < CONFIDENCE_THRESHOLD: # Expand boundaries
                orig = (x1, x2, y1, y2)
                
                if res := find_more_chars(pixels, x1, x2, y1, y2, -1):
                    x1, y1, y2 = res[0], res[1], res[2]

                if res := find_more_chars(pixels, x1, x2, y1, y2, 1):
                    x2, y1, y2 = res[0], res[1], res[2]
                    
                
                if orig != (x1, x2, y1, y2):
                    print("Expanded boundaries to be:", x1, x2, y1, y2)
                    full_word, confidence = predict_name(pixels, x1, x2, y1, y2, single_char, has_spaces, symbols)
            
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
                
            if " " not in full_word and ALLOWED_ROOM_NAMES.check(full_word.lower()):
                print("In dictionary so adding...")
                actual_boxes.append((x1, x2, y1, y2))
                rooms.append((full_word, ((first_char[0] + first_char[1])//2, (y1 + y2)//2)))
                remove_box(pixels, x1, x2, y1, y2)
                continue
                
            if full_word.isalpha():
                suggestions = [i for i in ALLOWED_ROOM_NAMES.suggest(full_word) if len(i) == len(full_word)]
                print("Suggestions:", suggestions)
                if len(suggestions) == 1:
                    full_word = suggestions[0].capitalize()
                    actual_boxes.append((x1, x2, y1, y2))
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
                                    actual_boxes.append((x1, x2, y1, y2))
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

                    if not ALLOWED_ROOM_NAMES.check(word) and len(word) > 1 and "-" not in word:
                        suggestions = [i for i in ALLOWED_ROOM_NAMES.suggest(word)]
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
                actual_boxes.append((x1, x2, y1, y2))
                rooms.append((full_word, ((first_char[0] + first_char[1])//2, (y1 + y2)//2)))
                remove_box(pixels, x1, x2, y1, y2)
            else:
                
                if len(full_word) == 2 and full_word.isnumeric() and confidence > 40.0:
                    print("Full word clutch:", full_word)
                    actual_boxes.append((x1, x2, y1, y2))
                    rooms.append((full_word, ((first_char[0] + first_char[1])//2, (y1 + y2)//2)))
                    remove_box(pixels, x1, x2, y1, y2)
                elif len(list(symbols.values())) == 1:
                    s = list(symbols.values())[0][0].capitalize()
                    box_coords = list(symbols.keys())[0]
                    print("Symbol clutch:", s)
                    x1, x2, y1, y2 = box_coords
                    actual_boxes.append((x1, x2, y1, y2))
                    rooms.append((full_word, ((x1 + x2)//2, (y1 + y2)//2)))
                    remove_box(pixels, x1, x2, y1, y2)
                else:                
                    print("Not adding...")   
    
    a = sorted(rooms, key = lambda i: int(i[0]) if i[0].isnumeric() else 0)

    return [[i[0], i[1][0], i[1][1]] for i in a], bw_image, actual_boxes, stair_coords