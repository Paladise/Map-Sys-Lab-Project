import enchant
import json
import sys

from PIL import Image
from time import perf_counter

from utils.bounding_boxes import get_bounding_boxes_opencv
from utils.bw import convert_to_bw
from utils.doorways import get_doorways
from utils.flatten import flatten_image
from utils.font_size import get_bound_font_size
from utils.recognize import process_image
from utils.rect import find_rectangles
from utils.search import find_symbols, integrate_detected
from utils.simplify import simplify_map
from utils.symbols import get_symbols, get_similarity_thresholds
from utils.walls import get_rectangles

start_time = perf_counter()

id = sys.argv[1]
READ_FROM = sys.argv[2]

DIRECTORY = f"media/{id}/"
FILE_NAME = DIRECTORY + READ_FROM
ALLOWED_ROOM_NAMES = enchant.request_pwl_dict("utils/potential_room_names.txt")
BW_THRESHOLD = 150 # Values less than this will become black
WEAK_CONFIDENCE = 75.0
HIGH_CONFIDENCE = 90.0
MAX_FONT_SIZE, MIN_FONT_SIZE = get_bound_font_size(FILE_NAME, ALLOWED_ROOM_NAMES, WEAK_CONFIDENCE, HIGH_CONFIDENCE - 5)
SYMBOL_FILES, POS_SYMBOLS = get_symbols(DIRECTORY)
SIMILARITY_THRESHOLDS = get_similarity_thresholds(DIRECTORY, SYMBOL_FILES, POS_SYMBOLS)


original_image = flatten_image(FILE_NAME)
WIDTH, HEIGHT = original_image.size[0], original_image.size[1]

bw_image = convert_to_bw(original_image.copy(), BW_THRESHOLD)
bw_image.save(DIRECTORY + f"black_and_white_{READ_FROM[:-4]}.png")

print("Max font size:", MAX_FONT_SIZE)
print("Min font size:", MIN_FONT_SIZE)
boxes, boxes_image = get_bounding_boxes_opencv(DIRECTORY + f"black_and_white_{READ_FROM[:-4]}.png", MAX_FONT_SIZE, MIN_FONT_SIZE)
boxes_image.save(DIRECTORY + f"boxes_{READ_FROM[:-4]}.png")

print("Processing image...")
rooms, blank_image, actual_boxes, stair_coords = process_image(boxes, original_image, bw_image, SIMILARITY_THRESHOLDS, ALLOWED_ROOM_NAMES, MAX_FONT_SIZE, DIRECTORY, SYMBOL_FILES) 

blank_image.save(DIRECTORY + f"temp_blank_map_{READ_FROM[:-4]}.png")

print("stairs BEFORE:", stair_coords)

print("Getting symbols that we might have missed...")
found_symbols, blank_image = find_symbols(blank_image, POS_SYMBOLS, DIRECTORY, SYMBOL_FILES)
rooms, stair_coords = integrate_detected(rooms, found_symbols, stair_coords, blank_image)

print("Getting rectangles...")
rectangles, _ = get_rectangles(blank_image, WIDTH, HEIGHT, rooms)

print("Getting doorways...")
blank_image = get_doorways(blank_image, actual_boxes)
blank_pixels = blank_image.load()
blank_image.save(DIRECTORY + f"blank_map_{READ_FROM[:-4]}.png")

print("Getting paths and doorways...")
blank_image, doorways = simplify_map(rooms, blank_image)
blank_pixels = blank_image.load()
blank_image.save(DIRECTORY + f"pathways_{READ_FROM[:-4]}.png")

print("Saving paths...")
map = [[1 if blank_pixels[x, y] == (0, 0, 0) else 2 if blank_pixels[x, y] == (255, 255, 0) else 0 for y in range(HEIGHT)] for x in range(WIDTH)] # 1 is for everything that is not a path, 0 is for the paths, and 2 is for doorways            

with open(DIRECTORY + f"render_{READ_FROM[:-4]}.json", "w") as f:    
    json.dump({"rooms": rooms, "points": rectangles, "map": map, "doorways": doorways, "stairs": stair_coords}, f, indent = 4, default = str) 
    
print("stairs:", stair_coords)
    
    
print("Entire program took", round(perf_counter() - start_time, 3), "seconds.")