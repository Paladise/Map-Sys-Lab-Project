from drawing import image_to_bw, create_image_from_box
from PIL import Image

image = Image.open("images/floor1.jpg")
BW_THRESHOLD = 150

print("Converting to black and white...")
image = image_to_bw(image, BW_THRESHOLD)
pixels = image.load()

boxes = {
    "door": [        
        (467, 88, 484, 108),
        (574, 150, 591, 171),
        (975, 45, 992, 69),
        (1098, 255, 1115, 276),
        (1115, 505, 1132, 525),
        (821, 735, 839, 755),
        (699, 817, 716, 837),
        (317, 808, 334, 828),
        (68, 610, 86, 630),
        (2, 430, 19, 450),
        (3, 311, 21, 331),
        (216, 43, 234, 63),
        (351, 61, 368, 81)
    ],

    "stairs": [
        (270, 229, 287, 243),
        (506, 288, 524, 302),
        (955, 667, 971, 682),
        (346, 657, 363, 671),
        (611, 130, 627, 144)
    ],

    "none": [
        (116, 120, 128, 130),
        (128, 267, 138, 275),
        (398, 154, 411, 167)
    ]
}

for symbol, box in boxes.items():
    for i, b in enumerate(box):
        x1, y1, x2, y2 = b
        image2 = create_image_from_box(pixels, x1 - 1, x2 + 1, y1 - 1, y2 + 1, 0)
        image2 = image2.crop((1, 1, x2 - x1 + 1, y2 - y1 + 1))
        image2.save("images/" + symbol + str(i + 1) + ".png")

