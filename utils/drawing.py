from colorsys import hls_to_rgb
from PIL import Image
from random import random    

def flood(pixels, x, y, found, min_x, max_x, min_y, max_y, width, height):
    """
    Recursively go through image to check neighboring pixels to form blobs
    of connected pixels as well as min & max for x & y.
    """
    
    if x < 0 or y < 0 or x >= width or y >= height:
        return found, min_x, max_x, min_y, max_y

    if pixels[x, y] == (0, 0, 0) and (x, y) not in found and len(found) < 10000: # Found unvisited black pixel, checking if < 10000 so don't get recursion error
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
                found, min_x, max_x, min_y, max_y = flood(pixels, x + x1, y + y1, found, min_x, max_x, min_y, max_y, width, height)
                
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


def draw_boxes(orig_image, max_height):
    """
    Goes throughout a PIL image to draw boxes around potential candidates 
    for characters (using approximate size / shape).
    """
    
    pixels = orig_image.load()
    boxes_image = orig_image.copy()
    boxes_pixels = boxes_image.load()
    width, height = orig_image.size[0], orig_image.size[1]
    loaded_pixels, boxes = set(), set()
    
    # Go throughout entire image
    
    for x in range(width):
        if (width - x) % 100 == 0:
            print(width - x, "pixels left")
        for y in range(height):
            if (x, y) in loaded_pixels or pixels[x, y] == (255, 255, 255): # Skip over looked-at pixels or white pixels
                continue

            found, min_x, max_x, min_y, max_y = flood(pixels, x, y, set(), x, x, y, y, width, height)
            x_len = max_x - min_x
            y_len = max_y - min_y

            loaded_pixels.update(found)

            if 5 < len(found) and len(found) < 500 and x_len < 30 and y_len > 3 and y_len < max_height: # Is appropriate size for character
                # print(f"Drawing box, {x_len} by {y_len} ==> {len(found)}")
                min_x -= 1
                max_x += 1
                min_y -= 1 
                max_y += 1
                boxes.add((min_x, max_x, min_y, max_y))
                h,s,l = random(), 0.5 + random()/2.0, 0.4 + random()/5.0
                rgb = tuple([int(256*i) for i in hls_to_rgb(h,l,s)])    
                draw_square(boxes_pixels, min_x, max_x, min_y, max_y, rgb) 

    return boxes_image, sorted(list(boxes), key = lambda b: (b[0], b[3]))


def remove_box(pixels, x1, x2, y1, y2):
    """
    Replaces all pixels with white within a certain box region
    """
    for x in range(x1, x2):
        for y in range(y1, y2):
            pixels[x, y] = (255, 255, 255)


def create_image_from_box(pixels, x1, x2, y1, y2, padding, boxes = []):
    """
    Given box coordinates, return image generated around that box 
    (from initial map) with or without padding
    """

    image2 = Image.new("RGB", (x2 - x1 + 1 + 2*padding, y2 - y1 + 1 + 2*padding), color = "white")
    pixels2 = image2.load()
    for x in range(x1 + 1, x2):
        for y in range(y1 + 1, y2):            
            if pixels[x, y] == (0, 0, 0):
                if not boxes or any(b[0] < x < b[1] and b[2] < y < b[3] for b in boxes):
                    pixels2[x - x1 + padding, y - y1 + padding] = pixels[x, y]

    image2 = image2.convert("L")
    return image2


def print_image_with_ascii(image, border = False):    
    width = image.size[0]

    pixels_in_image = list(image.getdata())    
    pixels_to_chars = ["#" if pixel_value < 255/2 else " " for pixel_value in pixels_in_image]
    pixels_to_chars = "".join(pixels_to_chars)
        
    if not border:
        image_ascii = [pixels_to_chars[index: index + width] for index in range(0, len(pixels_to_chars), width)]

    else:
        image_ascii = ["x" * (width + 2)]
        image_ascii += ["x" + pixels_to_chars[index: index + width] + "x" for index in range(0, len(pixels_to_chars), width)]
        image_ascii += ["x" * (width + 2)]
        
    print("\n".join(image_ascii))