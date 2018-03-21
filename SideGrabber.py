import cv2 as cv
import numpy as np


class SideGrabber:
    def __init__(self, pic_method):
        runSG(pic_method)


def takePic():
    "Returns image from webcam"
    cap = cv.VideoCapture(0)
    rettp, frametp = cap.read()
    return rettp, frametp

def returnLargestContour(contours):
    """Returns the largest contour in the list of contours"""
    return returnContourOnArea(contours, sizeIndex = 1)

def returnContourOnArea(contours, sizeIndex = 1):
    """Returns the contour with the sizeIndex largest area"""
    sizes = []
    for cnts in contours:
        sizes.append([cv.contourArea(cnts), cnts])
    sizes.sort(key= lambda x: x[0])
    return sizes[len(sizes)-sizeIndex][1]



def findSquares(mat, apsPrc=0.1, areaLim = 1000):
    """Returns list of contours that are squares with an area larger than areaLim"""
    _, contours, hierachy = cv.findContours(mat,cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
    squareCnt = []
    for cnt in contours:
        arc = cv.arcLength(cnt, True)
        approxPoly = cv.approxPolyDP(cnt, apsPrc*arc, True) #MAYBE CHECK IF CNT IS TOP LEVEL?
        area = cv.contourArea(cnt)
        x, y, w, h = cv.boundingRect(cnt)
        rect_area = w * h
        extent = float(area) / rect_area
        if len(approxPoly) == 4 and cv.contourArea(approxPoly) > areaLim and extent > 0.8:
                squareCnt.append(approxPoly)
    if len(squareCnt) > 0:
        return squareCnt
    else:
        return 0

def recursive_len(item):
    """Counts number of items in 2d list"""
    if type(item) == list:
        return sum(recursive_len(subitem) for subitem in item)
    else:
        return 1



def filterSquares(contours, rangeLim = 2.0):
    """Filters out the contours in the list that do not have an area within a
     median area divided by and multiplied by rangeLim"""
    return_contours = []
    contours.sort(key= lambda x: cv.contourArea(x))
    median_area = cv.contourArea(contours[int(len(contours)/2)])
    for cnts in contours:
        if median_area/2.0 < cv.contourArea(cnts) < median_area*2.0:
            return_contours.append(cnts)
    return return_contours

def checkColour(mean_val, color_code = 'HSV'):
    """Returns colour string based on which hue the input HSV is closest to"""
    H = 0
    S = 1
    V = 2
    colVal = [mean_val[H], mean_val[S], mean_val[V]]
    blue = [105, H, 'blue']
    lightred = [5, H, 'red']
    darkred = [175, H, 'red']
    orange = [15, H, 'orange']
    yellow = [25, H, 'yellow']
    green = [70, H, 'green']
    white = [80, S, 'white']
    colours = [blue, lightred, darkred, orange, yellow, green, white]
    distance = [1000, 0]
    for colour in colours:
        if colour is white:
            if colVal[colour[1]] < colour[0]:
                return colour[2]
        else:
            if distance[0] > abs(colVal[colour[1]] - colour[0]):
                distance[0] = abs(colVal[colour[1]] - colour[0])
                distance[1] = colour[2]
    return distance[1]


def runSG(image_method):
    """This is the 'Main' function that finds the colurs of the stickers of the side"""
    #Import image
    img_choice = image_method
    image = np.array(0)
    while True:
        if img_choice == 'c':
            ret, image = takePic()
            break
        elif img_choice == 'd':
            image = cv.imread('image3.jpeg', 1)
            break
        elif img_choice == 'p':
            img_path = input('Insert path')
            image = cv.imread(img_path, 1)
            break
        elif img_choice == 'q':
            quit()
        else:
            img_choice = input('Not a valid image input method [d/c/p/q]')
            quit()

    # SMOOTH AND CONVERT IMAGE TO GRAYSCALE
    image_gray = cv.cvtColor(cv.GaussianBlur(image, (5, 5), 0), cv.COLOR_BGR2GRAY)

    # THRESHOLD SO THAT THE BLACK BETWEEN STICKERS BECOMES ONLY MASKED PART THEN DILATE
    black_grid = cv.adaptiveThreshold(image_gray, 255, cv.ADAPTIVE_THRESH_GAUSSIAN_C, cv.THRESH_BINARY_INV,25,5)
    black_grid = cv.GaussianBlur(black_grid, (21,21), 0)
    _, black_grid = cv.threshold(black_grid,50,255,cv.THRESH_BINARY)
    dilation_kernel = np.ones((5,5),np.uint8)
    black_grid = cv.dilate(black_grid, dilation_kernel, iterations=4)

    cv.namedWindow('dilation', cv.WINDOW_NORMAL)
    cv.imshow('dilation', black_grid)
    cv.waitKey(0)
    cv.destroyAllWindows()

    # FIND DOMINANT SQUARE AND REMOVE EVERYTHING OUTSIDE OF IT
    contours_black_grid = findSquares(black_grid)
    mask_whole_rubrik = cv.drawContours(np.zeros(image_gray.shape, np.uint8), returnLargestContour(contours_black_grid), -1, 255, -1)
    black_grid = cv.bitwise_or(mask_whole_rubrik, black_grid)
    contours_black_grid = findSquares(black_grid)
    contours_black_grid = filterSquares(contours_black_grid)
    image_contours = image.copy()
    cv.drawContours(image_contours, contours_black_grid, -1, (100,255,100),thickness=5)

    # MAKE LIST OF COLOURS AND CENTERS
    side_map_items = []
    image_HSV = cv.cvtColor(image, cv.COLOR_BGR2HSV)
    image_HSV = cv.GaussianBlur(image_HSV, (11,11), 0)
    image_HSV = cv.GaussianBlur(image_HSV, (5,5), 0)

    cv.namedWindow('sideHSV', cv.WINDOW_NORMAL)
    cv.namedWindow('side', cv.WINDOW_NORMAL)
    cv.imshow('side', image_contours)
    cv.imshow('sideHSV', image_HSV)
    cv.waitKey(0)
    cv.destroyAllWindows()

    # FIND ALL H VALUES INSIDE OF MASK MADE BY THE INSIDE OF THE BLACK GRID AND TRANSFORM ANY H > 170 TO H = 180 - H
    hvalues = image_HSV[:,:,0]
    for idx, h in enumerate(hvalues.flat):
        if h > 170:
            hvalues.flat[idx] = 180-h
    image_HSV[:, :, 0] = hvalues

    for cnts in contours_black_grid:
        M = cv.moments(cnts)
        cx = int(M['m10'] / M['m00'])
        cy = int(M['m01'] / M['m00'])
        mask = np.zeros(image_gray.shape, np.uint8)
        cv.drawContours(mask, cnts, -1, 255, -1)
        mean_val = cv.mean(image_HSV, mask)
        items = [mean_val, cx, cy]
        side_map_items.append(items)

    side_map_items.sort(key= lambda x: int(x[1]) + int(x[2]) * 10)
    side_map = []
    for items in side_map_items:
        side_map.append(checkColour(items[0]))
    return(side_map)