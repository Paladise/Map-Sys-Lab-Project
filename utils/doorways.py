import cv2 as cv
import numpy as np

inputImage = cv.imread("rail.webp")
inputImageGray = cv.cvtColor(inputImage, cv.COLOR_BGR2GRAY)
edges = cv.Canny(inputImageGray,150,200,apertureSize = 3)
minLineLength = 50
maxLineGap = 5
lines = cv.HoughLinesP(edges,cv.HOUGH_PROBABILISTIC, np.pi/180, 30, minLineLength,maxLineGap)
for x in range(0, len(lines)):
    for x1,y1,x2,y2 in lines[x]:
        #cv.line(inputImage,(x1,y1),(x2,y2),(0,128,0),2, cv.LINE_AA)
        pts = np.array([[x1, y1 ], [x2 , y2]], np.int32)
        cv.polylines(inputImage, [pts], True, (0,255,0))

font = cv.FONT_HERSHEY_SIMPLEX
cv.putText(inputImage,"Tracks Detected", (500, 250), font, 0.5, 255)
cv.imwrite("doorway_result.png", inputImage)
cv.imwrite("edges.png", edges)