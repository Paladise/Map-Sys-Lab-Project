import cv2 as cv
import numpy as np
from drawing import create_image_from_box
from image_similarity_measures.quality_metrics import rmse

RMSE_THRESHOLD = 0.035
SYMBOLS = ["door"]

def detect_if_symbol(pixels, x1, x2, y1, y2):
    """
    Given box of potential symbol, determine whether that image
    is indeed a symbol and return which symbol it is (according to key)
    
    Currently uses root mean squared mimaege as an image similarity measure
    """

    image = create_image_from_box(pixels, x1, x2, y1, y2, 0)

    for symbol in SYMBOLS:
        symbol_image = cv.imread("images/" + symbol + ".png")
        width, height = symbol_image.shape[1], symbol_image.shape[0]

        dim = (width, height)
        opencv_image = cv.cvtColor(np.array(image), cv.COLOR_GRAY2RGB)
        resized_image = cv.resize(opencv_image, dim, interpolation = cv.INTER_AREA)

        m = rmse(symbol_image, resized_image).item()

        if m < RMSE_THRESHOLD:
            return symbol

    return ""