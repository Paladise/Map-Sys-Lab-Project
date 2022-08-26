import cv2 as cv
from PIL import Image

img = Image.open("detected_lines.jpg")
pix = img.load()

q = [(x, y) for x in range(img.width) for y in range(img.height)]

def flooooooood(q):
    while q:
        x, y = q.pop()

        r, g, b = pix[x, y]
        if r + g + abs(b - 255) < 220: # If blueish pixel
            pix[x, y] = (0, 0, 255) # Make pixel actual blue

            # Loop through neighboring pixels 
            for x1 in (-2, -1, 1, 2):
                for y1 in (-2, -1, 1, 2):
                    try:
                        r, g, b = pix[x + x1, y + y1]
                    except:
                        continue
                    if abs(r - 255) + abs(g - 255) + abs(b - 255) < 220: # If whiteish pixel
                        pix[x + x1, y + y1] = (0, 0, 255) # Make pixel blue
                        q.append((x + x1, y + y1)) # Add to q

flooooooood(q)

# Remove extra whiteish pixels
for x in range(img.width):
    for y in range(img.height):
        if pix[x, y] != (0, 0, 0) and pix[x, y] != (0, 0, 255):
            pix[x, y] = (0, 0, 0)

img.show()
img.save("only_walls_finalized.jpg")
        