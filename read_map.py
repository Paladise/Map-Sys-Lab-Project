import cv2 as cv
import numpy as np
import math


def main():    
    filename = "map_with_removed_characters.jpg"
    src = cv.imread(cv.samples.findFile(filename), cv.IMREAD_GRAYSCALE) # Load image
    
    if src is None: # Check if image is loaded fine
        print("Error opening image")
        return    
    
    dst = cv.Canny(src, 50, 200, None, 3)
    
    # Copy edges to the images that will display the results in BGR
    cdst = cv.cvtColor(dst, cv.COLOR_GRAY2BGR)
    cdst_reg = np.copy(cdst)
    
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
            cv.line(cdst_reg, pt1, pt2, (0,0,255), 1)
    
    lines = cv.HoughLinesP(dst, 0.5, np.pi / 180, 10, None, 10, 2) # Probabilitistic Hough Lines Transformation
    
    if lines is not None:
        for i in range(0, len(lines)):
            l = lines[i][0]
            cv.line(cdst, (l[0], l[1]), (l[2], l[3]), (255,0,0), 1)

    # cv.imshow("Source", src)
    cv.imshow("Detected Lines", cdst)
    cv.imshow("Detect lines - reg", cdst_reg)
    cv.imwrite("detected_lines.jpg", cdst)

    cv.waitKey()
    return 0
    
if __name__ == "__main__":
    main()