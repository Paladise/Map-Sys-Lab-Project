import cv2 as cv
import numpy as np
import math

 
filename = "good_map.png"
src = cv.imread(filename, cv.IMREAD_GRAYSCALE) # Load image 
dst = cv.Canny(src, 50, 200, None, 3)

# Copy edges to the images that will display the results in BGR
cdst = cv.cvtColor(dst, cv.COLOR_GRAY2BGR)
cdstP = np.copy(cdst)

# Regular hough lines transform

lines_reg = cv.HoughLines(dst, 0.5, np.pi / 180, 10, None)

if lines_reg is not None:
    for i in range(0, len(lines_reg)):
        rho = lines_reg[i][0][0]
        theta = lines_reg[i][0][1]
        a = math.cos(theta)
        b = math.sin(theta)
        x0 = a * rho
        y0 = b * rho
        pt1 = (int(x0 + 1000*(-b)), int(y0 + 1000*(a)))
        pt2 = (int(x0 - 1000*(-b)), int(y0 - 1000*(a)))
        cv.line(cdst, pt1, pt2, (0,0,255), 1)

# Probabilistic hough lines transform

lines = cv.HoughLinesP(dst, 0.5, np.pi / 180, 10, None, 10, 2)

if lines is not None:
    for i in range(0, len(lines)):
        l = lines[i][0]
        cv.line(cdstP, (l[0], l[1]), (l[2], l[3]), (255,0,0), 1)

cv.imshow("Detected Lines - Regular", cdst)
cv.imshow("Detect lines - Probabilistic", cdstP)
cv.imwrite("detected_lines.png", cdstP)
cv.waitKey()