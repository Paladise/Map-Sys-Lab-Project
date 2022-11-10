import cv2 as cv
import numpy as np
from image_similarity_measures.quality_metrics import rmse
from PIL import Image

all = ["door", "stairs", "none"]

for symbol in ["door", "stairs"]:
    print("\n\n\n\nRunning on:", symbol)
    image = Image.open(f"images/{symbol}.png").convert("L")

    measurements = []

    for s in all:
        m = []
        for i in range(1, 14):
            try:
                Image.open(f"images/{s}" + str(i) + ".png")
            except:
                break

            symbol_image = cv.imread(f"images/{s}" + str(i) + ".png")
            try:
                width, height = symbol_image.shape[1], symbol_image.shape[0]
            except:
                break

            dim = (width, height)
            opencv_image = cv.cvtColor(np.array(image), cv.COLOR_GRAY2RGB)
            resized_image = cv.resize(opencv_image, dim, interpolation = cv.INTER_AREA)

            m.append(round(rmse(symbol_image, resized_image).item(), 4))

        print("For symbol", s, "had measurements:", m)
        measurements.extend(m)

    print(sorted(measurements))
