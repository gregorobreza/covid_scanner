import sys
from imutils import paths
import numpy as np
import imutils
import cv2
import datetime

from imutils.video import VideoStream
import multiprocessing as mp

from tesseract_script import readText, string_processor


q = mp.Queue()



def mainMrzLoop(video_stream):

    rectKernel = cv2.getStructuringElement(cv2.MORPH_RECT, (13, 5))
    #sqKernel = cv2.getStructuringElement(cv2.MORPH_RECT, (21, 21))
    sqKernel = cv2.getStructuringElement(cv2.MORPH_RECT, (21, 27))

    vs = video_stream

    image = vs.read()
    #_, image = vs.read()
    
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        

    gray2 = cv2.GaussianBlur(gray, (3, 3), 0)
    blackhat = cv2.morphologyEx(gray2, cv2.MORPH_BLACKHAT, rectKernel)


    gradX = cv2.Sobel(blackhat, ddepth=cv2.CV_32F, dx=1, dy=0, ksize=-1)
    gradX = np.absolute(gradX)
    (minVal, maxVal) = (np.min(gradX), np.max(gradX))
    gradX = (255 * ((gradX - minVal) / (maxVal - minVal))).astype("uint8")

    gradX = cv2.morphologyEx(gradX, cv2.MORPH_CLOSE, rectKernel)
    thresh = cv2.threshold(gradX, 0, 225, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

    thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, sqKernel)
    thresh = cv2.erode(thresh, None, iterations=4)

    p = int(image.shape[1] * 0.05)
    thresh[:, 0:p] = 0
    thresh[:, image.shape[1] - p:] = 0

    cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    cnts = sorted(cnts, key=cv2.contourArea, reverse=True)

        
    for c in cnts:
        # compute the bounding box of the contour and use the contour to
        # compute the aspect ratio and coverage ratio of the bounding box
        # width to the width of the image
        (x, y, w, h) = cv2.boundingRect(c)
        ar = w / float(h)
        crWidth = w / float(gray.shape[1])
        # check to see if the aspect ratio and coverage width are within
         # acceptable criteria
        if ar > 6 and crWidth > 0.33:
            
            # pad the bounding box since we applied erosions and now need
            # to re-grow it
            pX = int((x + w) * 0.035)
            pY = int((y + h) * 0.035)
            (x, y) = (x - pX, y - pY)
            (w, h) = (w + (pX * 2), h + (pY * 2))
            # extract the ROI from the image and draw a bounding box
            # surrounding the MRZ
            cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
            
            roi = gray[y:y + h, x:x + w].copy()
            
            return image, roi
                

        break
    
    return image, None
