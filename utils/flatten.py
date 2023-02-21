import cv2 as cv
import numpy as np
from PIL import Image

np.set_printoptions(suppress=True) # Don't use scientific notation

def flatten_image(filename, debugging = False):   
    img = cv.imread(filename)
    height, width = img.shape[:2]

    # threshold
    lower = (180, 180, 180)
    upper = (240,240,240)
    thresh = cv.inRange(img, lower, upper)
    
    if debugging:
        cv.imwrite("thresh_before.jpg", thresh) 

    # find all of the connected components (white blobs in your image).
    # im_with_separated_blobs is an image where each detected blob has a different pixel value ranging from 1 to nb_blobs - 1.
    nb_blobs, im_with_separated_blobs, stats, _ = cv.connectedComponentsWithStats(thresh)
    # stats (and the silenced output centroids) gives some information about the blobs. See the docs for more information. 
    # here, we're interested only in the size of the blobs, contained in the last column of stats.
    sizes = stats[:, -1]
    # the following lines result in taking out the background which is also considered a component, which I find for most applications to not be the expected output.
    # you may also keep the results as they are by commenting out the following lines. You'll have to update the ranges in the for loop below. 
    sizes = sizes[1:]
    nb_blobs -= 1

    # minimum size of particles we want to keep (number of pixels).
    # here, it's a fixed value, but you can set it as you want, eg the mean of the sizes or whatever.
    min_size = 5000

    thresh = np.zeros_like(thresh) # Create black image
    for blob in range(nb_blobs):
        if sizes[blob] >= min_size: # Blob of big enough size
#             print(sizes[blob])
            thresh[im_with_separated_blobs == blob + 1] = 255 # Replaces black pixels with white
 
    if debugging:
        cv.imwrite("thresh_after.png", thresh)

    contours, hierarchy = cv.findContours(thresh, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_NONE)
    
    # Find biggest contour
    if contours:
        c = max(contours, key = cv.contourArea)
        x,y,w,h = cv.boundingRect(c)    
    else:
        print("Did not detect contour")
        return Image.open(filename)
    
    approx = cv.approxPolyDP(c, 100,True)
    
    pts1 = [
        x, y, x + w, y + h
    ]
    
    dest = np.array([[x, y], [x, y + h], [x + w, y + h], [x + w, y]], np.float32)
    approx = approx.squeeze()
    approx = np.float32(approx)
    
    if debugging:
#         print("c:", c)
        print("Destination:", dest)
        print()
        print("Approximation:", approx)   
        cv.rectangle(img, (x, y, x + w, y + h), (0, 0, 255), 2)
        cv.imwrite("temp.png", img)
    
    matrix = cv.getPerspectiveTransform(approx, dest)
    result = cv.warpPerspective(img, matrix, (width, height))
    result = result[y:y+h, x:x+w] # Crop
    
    if debugging: 
        cv.imwrite("result.png", result)
    
    img = cv.cvtColor(result, cv.COLOR_BGR2RGB)
    img_pil = Image.fromarray(img)
    
    return img_pil
    
if __name__ == "__main__":
#     flatten_image("floor1.jpg", True)
#     flatten_image("test.jpg",True)
#     flatten_image("test2.jpg",True)
    flatten_image("test3.jpg",True)