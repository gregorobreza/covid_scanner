import numpy as np
import cv2
import numpy as np

def writeText(text, img, fontScale, thickness, xOffset=0, yOffset=0, fontFace=cv2.FONT_HERSHEY_SIMPLEX):
    """sprejme niz in ga centrira na podano sliko z offsetom premikamo napis iz sredine
    funkcija vrne sliko"""
    textsize = cv2.getTextSize(text, fontFace, fontScale, thickness)[0]
    X = int((img.shape[1] - textsize[0]) / 2)
    Y = int((img.shape[0] + textsize[1]) / 2)
    return cv2.putText(img, text, (X + xOffset, Y + yOffset), fontFace, fontScale, (0, 0, 0), thickness, cv2.LINE_AA)