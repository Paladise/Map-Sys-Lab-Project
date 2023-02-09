import cv2
import numpy as np


def remove_glare(filename):
    # read image
    img = cv2.imread(filename)
    h, w = img.shape[:2]

    # threshold
    lower = (225, 225, 225)
    upper = (255, 255, 255)
    thresh = cv2.inRange(img, lower, upper)
    cv2.imwrite("tomato_thresh.jpg", thresh) 

    # apply morphology close and open to make mask
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7,7))
    morph = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel, iterations=1)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (25,25))
    morph = cv2.morphologyEx(morph, cv2.MORPH_DILATE, kernel, iterations=1)

    # floodfill the outside with black
    black = np.zeros([h + 2, w + 2], np.uint8)
    mask = morph.copy()

    # use mask with input to do inpainting
    result1 = cv2.inpaint(img, mask, 101, cv2.INPAINT_TELEA)
    result2 = cv2.inpaint(img, mask, 101, cv2.INPAINT_NS)

    # write result to disk
    cv2.imwrite("tomato_morph.jpg", morph)
    cv2.imwrite("tomato_mask.jpg", mask)
    cv2.imwrite("tomato_inpaint1.jpg", result1)
    cv2.imwrite("tomato_inpaint2.jpg", result2)