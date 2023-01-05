DIRECTIONS = (
    (1, 0),
    (-1, 0),
    (0, 1),
    (0, -1)
)

PADDING = 50
DIST_BETWEEN = PADDING

def simplify(rooms, image):
    def inside(x, y):
        if x < 0 or y < 0 or x >= width or y >= height:
            return False
        else:
            return True

    def move_along(x, y, dir_x, dir_y):
        x1, y1 = x, y
        while inside(x, y) and pixels[x, y] == (255, 255, 255):
            x += dir_x
            y += dir_y

        if dir_x == 0:
            return abs(y1 - y)
        else:
            return abs(x1 - x)
    
    pixels = image.load()
    width, height = image.size[0], image.size[1]

    image2 = image.copy()
    pixels2 = image2.load()

    for x in range(width):
        print("x left:", width - x)
        for y in range(height):

            if pixels2[x, y] == (255, 255, 255):
                dists = []

                for dir_x, dir_y in DIRECTIONS:
                    dist = move_along(x, y, dir_x, dir_y)
                    dists.append(dist)

                if ((abs(dists[0] - dists[1]) == 1 and (dists[0] + dists[1]) % 2 == 1) or dists[0] - dists[1] == 0) and dists[0] < PADDING:

                    if dists[2] == 1 or dists[3] == 1:
                        continue

                    parallel = False

                    for i in range(2):
                        dir_x, dir_y = DIRECTIONS[i]

                        for j in range(DIST_BETWEEN):
                            try:
                                p = pixels2[x + j * dir_x, y + j * dir_y] 
                            except:
                                break
                            if p == (0, 0, 0):
                                break
                            if p == (255, 0, 0) or p == (0, 255, 0):
                                parallel = True
                                break

                    if parallel:
                        continue

                    pixels2[x, y] = (255, 0, 0)

                    for i in range(2, 4):
                        dir_x, dir_y = DIRECTIONS[i]

                        j = 1

                        while True:
                            x1, y1 = x + dir_x * j, y + dir_y * j
                            if inside(x1, y1) and pixels[x1, y1] == (255, 255, 255):
                                pixels2[x1, y1] = (0, 255, 0)
                            else:
                                break

                            j += 1

                elif ((abs(dists[2] - dists[3]) == 1 and (dists[2] + dists[3]) % 2 == 1) or dists[2] - dists[3] == 0) and dists[2] < PADDING:

                    if dists[0] == 1 or dists[1] == 1:
                        continue

                    parallel = False

                    for i in range(2, 4):
                        dir_x, dir_y = DIRECTIONS[i]

                        for j in range(DIST_BETWEEN):
                            try:
                                p = pixels2[x + j * dir_x, y + j * dir_y] 
                            except:
                                break
                            if p == (0, 0, 0):
                                break

                            if p == (255, 0, 0) or p == (0, 255, 0):
                                parallel = True
                                break

                    if parallel:
                        continue

                    pixels2[x, y] = (255, 0, 0)

                    for i in range(0, 2):
                        dir_x, dir_y = DIRECTIONS[i]

                        j = 1

                        while True:
                            x1, y1 = x + dir_x * j, y + dir_y * j
                            if inside(x1, y1) and pixels[x1, y1] == (255, 255, 255):
                                pixels2[x1, y1] = (0, 255, 0)
                            else:
                                break

                            j += 1

    for name, x, y in rooms:
        pixels2[x, y] = (0, 0, 255)

        for x1, y1 in DIRECTIONS:

            x2, y2 = x + x1, y + y1

            while inside(x2, y2) and pixels2[x2, y2] == (255, 255, 255): 
                pixels2[x2, y2] = (0, 0, 255)
                x2 += x1
                y2 += y1

    for x in range(1, width - 1):
        for y in range(1, height - 1):
            if pixels2[x, y] == (0, 255, 0):
                if sum(pixels2[x + dir_x, y + dir_y] == (0, 255, 0) for dir_x, dir_y in DIRECTIONS) == 1 and sum(pixels2[x + dir_x, y + dir_y] == (0, 0, 255) or pixels2[x + dir_x, y + dir_y] == (255, 0, 0) for dir_x, dir_y in DIRECTIONS) == 0:                    

                    x1, y1 = 0, 0
                    for dir_x, dir_y in DIRECTIONS:
                        p = pixels2[x + dir_x, y + dir_y]
                        if p == (0, 255, 0):
                            x1, y1 = dir_x, dir_y
                            break

                    if abs(dir_x) == 1:
                        other_x = 0
                        other_y = 1
                    else:
                        other_x = 1
                        other_y = 0

                    x2, y2 = x, y

                    while inside(x2, y2) and pixels2[x2, y2] == (0, 255, 0) and inside(x2 + other_x, y2 + other_y) and pixels2[x2 + other_x, y2 + other_y] != (0, 255, 0) and pixels2[x2 + other_x, y2 + other_y] != (255, 0, 0) and pixels2[x2 + other_x, y2 + other_y] != (0, 0, 255):

                        pixels2[x2, y2] = (255, 255, 255)
                        x2 += x1
                        y2 += y1

                    pixels2[x2, y2] = (255, 0, 0)

    for x in range(width):
        for y in range(height):
            if pixels2[x, y] != (0, 0, 0) and pixels2[x, y] != (255, 255, 255):
                pixels2[x, y] = (255, 255, 255)
            else:
                pixels2[x, y] = (0, 0, 0)

    return image2
    