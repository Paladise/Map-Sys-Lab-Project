import cv2 as cv
import pytesseract
from PIL import Image

def get_bound_font_size(filename, d, weak_confidence, high_confidence):
    TESSERACT_DIR_CONFIG = '--tessdata-dir "/cluster/2023abasto/local/share/tessdata"'
    pytesseract.pytesseract.tesseract_cmd = r"/cluster/2023abasto/tesseract-5.1.0/tesseract"

    images = cv.imread(filename)
    rgb = cv.cvtColor(images, cv.COLOR_BGR2RGB)
    results = pytesseract.image_to_data(rgb, output_type=pytesseract.Output.DICT, config = f"--oem 3 -l eng --psm 11 -c tessedit_char_whitelist=0123456789abcdefghijklmnopqrstuvwxyz {TESSERACT_DIR_CONFIG}")

    max_height = 0
    min_height = float("inf")

    for i in range(0, len(results["text"])):
        x = results["left"][i]
        y = results["top"][i]
        w = results["width"][i]
        h = results["height"][i]
        text = results["text"][i]
        conf = int(results["conf"][i])

        # filter out weak confidence text localizations
        if (conf > weak_confidence and text.isalpha() and d.check(text) and (text[0].isupper() or any(a in "dfhklb" for a in text)) and all(i not in "qypj" for i in text)) or (conf > high_confidence and len(text) >= 2 and text.isnumeric()):
            
            if h > max_height:  
                max_height = h                
                print("Confidence: {}".format(conf))
                print("Text: {}".format(text))
                print("Maximum height allowed will be:", max_height)
                print()
            if h < min_height:    
                min_height = h
                print("Confidence: {}".format(conf))
                print("Text: {}".format(text))
                print("Minimum height allowed will be:", min_height)
                print()
                    
    max_height += 5
    min_height -= 5
    return max_height, min_height