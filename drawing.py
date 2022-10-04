from colorsys import hls_to_rgb
from random import random
from sys import setrecursionlimit

setrecursionlimit(10000) # We don't talk about this line

def image_to_bw(image, threshold):
    """
    Converts a PIL image to only black and white pixels
    given a black and white threshold
    """

    width, height = image.size[0], image.size[1]
    pixels = image.load()

    for x in range(width):
        for y in range(height):
            r, g, b = pixels[x, y]
            if 0.2126*r + 0.7152*g + 0.0722*b < threshold: # Check if pixel is relatively dark
                pixels[x, y] = (0, 0, 0)
            else:
                pixels[x, y] = (255, 255, 255)

    return image
    

def flood(pixels, x, y, found, min_x, max_x, min_y, max_y):
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
                found, min_x, max_x, min_y, max_y = flood(pixels, x + x1, y + y1, found, min_x, max_x, min_y, max_y)

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


def draw_boxes(image):
    """
    Goes throughout a PIL image to draw boxes around potential candidates 
    for characters (using approximate size / shape).
    """

    pixels = image.load()
    width, height = image.size[0], image.size[1]

    loaded_pixels, boxes, walls = set(), set(), set()
    for x in range(width):
        for y in range(height):
            if (x, y) in loaded_pixels or pixels[x, y] == (255, 255, 255): # Skip over looked-at pixels or white pixels
                continue

            found, min_x, max_x, min_y, max_y = flood(pixels, x, y, set(), x, x, y, y)
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
                rgb = tuple([int(256*i) for i in hls_to_rgb(h,l,s)])    
                draw_square(pixels, min_x, max_x, min_y, max_y, rgb)  
            else: # Should be part of walls
                walls.update(found)

    # with open("list_of_points.txt", "w") as f:
    #     for i in walls:
    #         f.write(f"{i[0]} {i[1]} 0\n")

    return image, sorted(list(boxes), key = lambda b: (b[0], b[3])), list(walls)


def remove_box(pixels, x1, x2, y1, y2):
    """
    Replaces all pixels with white within a certain box region
    """
    for x in range(x1, x2):
        for y in range(y1, y2):
            pixels[x, y] = (255, 255, 255)