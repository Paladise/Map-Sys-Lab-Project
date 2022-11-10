import math

STAIR_LOCATIONS = {
    "1": [
        (270, 229),
        (506, 288),
        (652, 505),
        (346, 657)
    ], 
    "2": [
        (54, 199),
        (281, 267),
        (572, 202),
        (423, 470),
        (127, 617),
        (451, 753)
    ]
}


# x_dif = min(STAIR_LOCATIONS["1"])[0] - min(STAIR_LOCATIONS["2"])[0]
# y_dif = min(STAIR_LOCATIONS["1"])[1] - min(STAIR_LOCATIONS["2"])[1]

point1 = (270, 229) 
point1_2 = (54, 199)

point2 = (955, 668) 
point2_2 = (719, 629)

x_dif = point1[0] - point1_2[0]
x_dif_2 = point2[0] - point2_2[0]

y_dif = point1[1] - point1_2[1]
y_dif_2 = point2[1] - point2_2[1]
print(x_dif, x_dif_2, y_dif, y_dif_2)

x_scale = 1 + (x_dif_2 - x_dif) / (point2[0] - point1[0])
print(x_scale)

y_scale = 1 + (y_dif_2 - y_dif) / (point2[1] - point1[1])
print(y_scale)

for i in STAIR_LOCATIONS["1"]:
    for a in STAIR_LOCATIONS["2"]:
        x2 = i[0] - x_dif
        y2 = i[1] - y_dif
        j = (x2, y2)
        # print(j)
        # print(math.sqrt((a[0] - j[0])**2 + (a[1] - j[1])**2))
        if math.sqrt((a[0] - j[0])**2 + (a[1] - j[1])**2) < 20:
            print(i, a)

from PIL import Image

image = Image.open("images/blank_map_floor1.png")
pixels = image.load()
image2 = Image.open("images/blank_map_floor2.png")
pixels2 = image2.load()


for x in range(image.size[0]):
    for y in range(image.size[1]):
        
        x2 = (x_dif_2 - x_dif) / (point2[0] - point1[0]) * (x - point1[0]) 
        x2 *= x_scale
        y2 = (y_dif_2 - y_dif) / (point2[1] - point1[1]) * (y - point1[1])
        y2 *= y_scale

        # print(x, (x_dif_2 - x_dif), (point2[0] - point1[0]), (x - point1[0]), round(x2), x - round(x2) - x_dif)
        # print(y, (y_dif_2 - y_dif), (point2[1] - point1[1]), (y - point1[1]), round(y2), y - round(y2) - y_dif)
        # input()

        x2 = x - round(x2) - x_dif
        y2 = y - round(y2) - y_dif

        if x2 < 0 or y2 < 0 or x2 >= image2.size[0] or y2 >= image2.size[1]:
            continue

        if pixels2[x2, y2] == (0, 0, 0):
            if pixels[x, y] == (0, 0, 0):

                pixels[x, y] = (0, 0, 255)
            else:
                pixels[x, y] = (0, 255, 0)

# image.show()
image.save("images/matched_floors.png")


