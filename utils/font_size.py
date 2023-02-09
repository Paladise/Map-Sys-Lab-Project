import cv2 as cv
import pytesseract
from PIL import Image

def get_max_font_size(filename, d, weak_confidence, high_confidence):
    TESSERACT_DIR_CONFIG = '--tessdata-dir "/cluster/2023abasto/local/share/tessdata"'
    pytesseract.pytesseract.tesseract_cmd = r"/cluster/2023abasto/tesseract-5.1.0/tesseract"

    images = cv.imread(filename)
    rgb = cv.cvtColor(images, cv.COLOR_BGR2RGB)
    results = pytesseract.image_to_data(rgb, output_type=pytesseract.Output.DICT, config = TESSERACT_DIR_CONFIG)

    max_height = 50 # Default max height

    for i in range(0, len(results["text"])):
        x = results["left"][i]
        y = results["top"][i]
        w = results["width"][i]
        h = results["height"][i]
        text = results["text"][i]
        conf = int(results["conf"][i])

        # filter out weak confidence text localizations
        if (conf > weak_confidence and text.isalpha() and d.check(text)) or (conf > high_confidence and len(text) >= 2 and text.isnumeric()):

            if text.isalpha() and (text[0].isupper() or any(a in "dfhklb" for a in text)) and all(i not in "qypj" for i in text):
                max_height = (round(h * 3/2) + 5)
                print("Confidence: {}".format(conf))
                print("Text: {}".format(text))
                print("height:", h)
                print("Maximum height allowed will be:", max_height)
                print()
    
    return max_height