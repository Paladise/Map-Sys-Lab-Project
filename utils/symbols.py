import cv2 as cv
import numpy as np

from image_similarity_measures.quality_metrics import ssim
from os import listdir
from os.path import isfile, join
from PIL import Image, ImageChops
from random import choice, random, sample

try:
    from utils.drawing import create_image_from_box
except:
    pass

def get_symbols(directory):
    """ 
    Get the symbols that are in the directory and crop them appropriately
    """
    
    files = {f: f[6:].split(".")[0] for f in listdir(directory) if isfile(join(directory, f)) and f.startswith("symbol")}
    symbols = files.values()
    
    print("Files:", files)
    
    # Crop the images appropriately
    
    for file in files:
        filedir = directory + file
        tresh_min, tresh_max = 128, 255
        cv_image = cv.imread(filedir)
        im_bw = cv.cvtColor(cv_image, cv.COLOR_RGB2GRAY)
        (thresh, im_bw) = cv.threshold(im_bw, tresh_min, tresh_max, 0)
        contours, hierarchy = cv.findContours(im_bw, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
        cs = sorted(contours, key = cv.contourArea, reverse = True)

        c = cs[0]
        x, y, w, h = cv.boundingRect(c)

        if not ((abs(w - cv_image.shape[0]) <= 1 or abs(h - cv_image.shape[1]) <= 1) and cv_image.shape[0] < 50):
            c = cs[1] # Sometimes bounding box may be whole image so take second contour

        x, y, w, h = cv.boundingRect(c)
        pil_image = Image.open(filedir)
        new_image = pil_image.crop((x, y, x + w, y + h))
        new_image.save(filedir)        
    
    return files, symbols

def create_image_from_box_2(pixels, x1, x2, y1, y2, padding, boxes = []):
    """
    Given box coordinates, return image generated around that box 
    (from initial map) with or without padding
    """

    image2 = Image.new("RGB", (x2 - x1, y2 - y1), color = "white")
    pixels2 = image2.load()
    for x in range(x1, x2):
        for y in range(y1, y2): 
            if not boxes or any(b[0] < x < b[1] and b[2] < y < b[3] for b in boxes):
                pixels2[x - x1, y - y1] = pixels[x, y]

    return image2

def detect_if_symbol(pixels, thresholds, x1, x2, y1, y2, directory, symbol_files):
    """
    Given box of potential symbol, determine whether that image
    is indeed a symbol and return which symbol it is (according to key, if given one)
    """
    
    if symbol_files:
        test_image = create_image_from_box_2(pixels, x1 + 1, x2 - 1, y1 + 1, y2 - 1, 0)
        width, height = test_image.size

        for file, symbol in symbol_files.items(): # Check all symbols in key
            key_image = cv.imread(directory + file) # Get image of original symbol
            key_width, key_height = key_image.shape[1], key_image.shape[0]
            test_cv_image = np.array(test_image.resize((key_width, key_height)))[:, :, ::-1] # Resize test image to that of original key

            m = ssim(key_image, test_cv_image).item() # Compare similarity

            if m > thresholds[symbol]:  # Possibly a symbol, so return it
                return symbol
 
    return "" # Return nothing since not a symbol


def trim(im):
    bg = Image.new(im.mode, im.size, im.getpixel((0,0)))
    diff = ImageChops.difference(im, bg)
    diff = ImageChops.add(diff, diff, 2.0, -100)
    bbox = diff.getbbox()
    if bbox:
        return im.crop(bbox)


def get_similarity_thresholds(directory, files, symbols):
    """
    Given possible symbols, construct possible thresholds for similarity images
    by creating several distorted images and comparing their ssims, then returning a dictionary of
    symbols and their threshold values
    """
    
    def inside(x, y):
        if x > 0 and x < w - 1 and y > 0 and y < h - 1:
            return True
        else:
            return False
    
    thresholds = {}

    for file, symbol in files.items():

        print("Looking at symbol:", symbol)

        avg = []
        for _ in range(25): # Create permutations
            image = Image.open(directory + file).convert("RGB")
            pixels = image.load()
            w, h = image.size[0], image.size[1]
            image = create_image_from_box_2(pixels, 0, w, 0, h, 1).convert("RGB") # Add 1 pixel padding

            # Shift image
            
            data = np.array(image)
            data[(data == (0, 0, 0)).all(axis = -1)] = (255, 0, 0)
            img = Image.fromarray(data, mode='RGB')

            temp = choice([(1, 0), (-1, 0), (0, 1), (0, -1), (0, 0)])
            c, f = temp[0], temp[1] # c controls left/right, f controls up/down

            a, b, d, e = 1, 0, 0, 1
    
            img = img.transform(img.size, Image.Transform.AFFINE, (a, b, c, d, e, f)) # Shift image

            # Randomly replace pixels with opposite color
        
            data = np.array(img)
            data[(data == (0, 0, 0)).all(axis = -1)] = (255, 255, 255)
            img = Image.fromarray(data, mode='RGB')

            data = np.array(img)
            data[(data == (255, 0, 0)).all(axis = -1)] = (0, 0, 0)
            image = Image.fromarray(data, mode='RGB')

            pixels = image.load()
            w, h = image.size[0], image.size[1]
            empty, not_empty = [], []

            for x in range(w):
                for y in range(h):
                    if pixels[x, y] == (255, 255, 255):
                        if any(pixels[x + x3, y + y3] == (0, 0, 0) for x3 in range(-1, 2) for y3 in range(-1, 2) if inside(x + x3, y + y3)):
                            empty.append((x, y))
                    else:
                        if any(pixels[x + x3, y + y3] == (255, 255, 255) for x3 in range(-1, 2) for y3 in range(-1, 2) if inside(x + x3, y + y3)):
                            not_empty.append((x, y))

            num = choice(range(1, 10))
            num2 = choice(range(1, 10))

            image2 = image.copy()
            pixels2 = image2.load()

            num = min(num, len(empty))

            for e in sample(empty, num):            
                x, y = e
                pixels2[x, y] = (0, 0, 0)

            num2 = min(num2, len(not_empty))

            for e in sample(not_empty, num2):
                x, y = e
                pixels2[x, y] = (255, 255, 255)
                
            image2 = trim(image2)
            
            cv_image2 = cv.cvtColor(np.array(image2.convert("L")), cv.COLOR_GRAY2RGB)
            cv_image2 = cv.resize(cv_image2, (image.size[0], image.size[1]), interpolation = cv.INTER_AREA)

            m = round(ssim(cv.cvtColor(np.array(image.convert("L")), cv.COLOR_GRAY2RGB), cv_image2).item(), 4)
            avg.append(m)

        threshold = sum(avg) / len(avg) # Set average similarity as threshold
        thresholds[symbol] = threshold - 0.075 # Add extra allowance
        
    print("Thresholds:", thresholds)
    return thresholds