import cv2 as cv
import numpy as np


def main():    
    filename = "map_with_removed_characters.jpg"
    src = cv.imread(cv.samples.findFile(filename), cv.IMREAD_GRAYSCALE) # Load image
    
    if src is None: # Check if image is loaded fine
        print("Error opening image")
        return    
    
    dst = cv.Canny(src, 50, 200, None, 3)
    
    # Copy edges to the images that will display the results in BGR
    cdst = cv.cvtColor(dst, cv.COLOR_GRAY2BGR)
    
    
    lines = cv.HoughLinesP(dst, 0.5, np.pi / 180, 10, None, 10, 2) # Probabilitistic Hough Lines Transformation
    
    if lines is not None:
        for i in range(0, len(lines)):
            l = lines[i][0]
            cv.line(cdst, (l[0], l[1]), (l[2], l[3]), (255,0,0), 1)

    # cv.imshow("Source", src)
    cv.imshow("Detected Lines", cdst)
    cv.imwrite("detected_lines.jpg", cdst)

    cv.waitKey()
    return 0
    
if __name__ == "__main__":
    main()