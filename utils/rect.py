def find_rectangles(pixels, x, y, found, min_x, max_x, min_y, max_y):
    """
    Recursively go through image to check neighboring pixels to form blobs
    of rectangles as well as min & max for x & y for rendering walls in Three.js
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