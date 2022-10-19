import cv2 as cv
import numpy as np
import imagehash
from image_similarity_measures.quality_metrics import rmse
from PIL import Image

all = ["door", "stairs", "none"]

for symbol in ["door", "stairs"]:
    print("\n\n\n\nRunning on:", symbol)
    image = Image.open(f"images/{symbol}.png").convert("L")

    for s in all:
        for i in range(1, 14):
            symbol_image = cv.imread(f"images/{s}" + str(i) + ".png")
            try:
                width, height = symbol_image.shape[1], symbol_image.shape[0]
            except:
                break
            
            hash0 = imagehash.average_hash(Image.fromarray(symbol_image), hash_size = max(width, height))
            hash1 = imagehash.average_hash(image, hash_size = max(width, height))
            m = abs(hash0 - hash1)
            print(f"\n{s}{i}")
            print(abs(width - image.size[0]), abs(height - image.size[1]))
            print("Image hash m is:", m)

            dim = (width, height)
            opencv_image = cv.cvtColor(np.array(image), cv.COLOR_GRAY2RGB)
            resized_image = cv.resize(opencv_image, dim, interpolation = cv.INTER_AREA)

            m = rmse(symbol_image, resized_image).item()

            print("RMSE m is:", m)
