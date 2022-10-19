import cv2 as cv
import pytesseract
from PIL import Image

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract"

# Grayscale, Gaussian blur, Otsu's threshold
image = cv.imread("images/floor1.jpg")
gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
blur = cv.GaussianBlur(gray, (3,3), 0)
thresh = cv.threshold(blur, 0, 255, cv.THRESH_BINARY_INV + cv.THRESH_OTSU)[1]

# Morph open to remove noise and invert image
kernel = cv.getStructuringElement(cv.MORPH_RECT, (3,3))
opening = cv.morphologyEx(thresh, cv.MORPH_OPEN, kernel, iterations=1)
invert = 255 - opening
# cv.imshow("Begin", invert)

# Add boxes using pytesseract

pil_img = Image.open("images/floor1.jpg")
pix = pil_img.load()
h, w, c = image.shape

boxes = pytesseract.image_to_boxes(invert)
for b in boxes.splitlines():
    b = b.split(' ')

    x1 = int(b[1])
    x2 = int(b[3])
    y1 = h - int(b[2])
    y2 = h - int(b[4])

    if abs(x1 - x2) * abs(y1 - y2) < 1200 and abs(x1 - x2) > 10 and abs(y1 - y2) > 10:
        for x in range(x1 - 1, x2 + 1):
            for y in range(y2 - 1, y1 + 1):
                pix[x, y] = (255, 255, 255)

        image = cv.rectangle(image, (int(b[1]), h - int(b[2])), (int(b[3]), h - int(b[4])), (0, 255, 0), 2)
cv.imwrite("tes_detected_boxes.png",image)
cv.imshow("Boxes", image)
pil_img.show()
