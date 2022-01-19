#!/home/pi/pct_scan/env/pct/bin/python3
#0.1.2
#import ostalih modulov
from os import name
import sys
from imutils.video import VideoStream
import datetime
import imutils
import time
import cv2
import multiprocessing as mp
import numpy as np
import screeninfo

#uvoz nasih funcij
from autoDetectMrzFin import mainMrzLoop
from tessaract_detect import processMrz, string_processor, displayDataFromId
from display_text import writeText
from makeqr import createJson, createQr
from leds import ledWhite, ledGreen, ledRed, ledOff

# Uvoz logginga
import logging as lg
#lg.basicConfig(filename='/home/pi/pct_scan/samotest/qr-generator.log', level=lg.INFO, filemode='a', format='%(asctime)s - %(levelname)s : %(message)s')

#definicija parametrov za nas zaslon
screen_id = 0
screen = screeninfo.get_monitors()[screen_id]
frame_width, frame_height = screen.width, screen.height

def draw_circle(event,x,y,flags,param):
    global mouseX,mouseY
    global qrGenerate
    global idRead
    global created
    if event == cv2.EVENT_LBUTTONDOWN:
        if idRead == True and qrGenerate == None:
            cv2.circle(frame_copy,(x,y),100,(255,0,0),-1)
            mouseX,mouseY = x,y
            if mouseX >= 400 and mouseY > frame_height-80:
                qrGenerate = True
                lg.info(f'Uporabnik potrdil ime in datum rojstva.')
                
                
            elif mouseX < 400 and mouseY > frame_height-80:
                idRead = None
                qrGenerate = None
                #lg.warning(f'Uporabnik preklical prebrano ime in datum rojstva.')
                ledWhite(brightness)
                
        elif idRead==True and qrGenerate==True:
            cv2.circle(frame_copy,(x,y),100,(255,0,0),-1)
            mouseX,mouseY = x,y
            if mouseY > frame_height-80:
                idRead = None
                qrGenerate = None
                created = None
                #lg.info(f'ZAKLJUCEK')
                #lg.info(f'-------------------------')
                ledWhite(brightness)
                
window_name = 'projector'
cv2.namedWindow(window_name, cv2.WND_PROP_FULLSCREEN)
cv2.moveWindow(window_name, screen.x - 1, screen.y - 1)
cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
cv2.setMouseCallback(window_name, draw_circle)
# get the size of the screen



#uvoz slik za prikaz UI
'''
korak1 = cv2.imread("./koraki/korak_1.png")
korak2 = cv2.imread("./koraki/korak_2.png")
korak3 = cv2.imread("./koraki/korak_3.png")
potrdi = cv2.imread("./koraki/potrdi.png")
zakljuci = cv2.imread("./koraki/zakljuci.png")
prepoznavanje = cv2.imread("./koraki/prepoznavanje.png")
'''
pathNavodila = "/home/pi/pct_scan/samotest"

korak1 = cv2.imread(pathNavodila+"/koraki/korak_1.png")
korak2 = cv2.imread(pathNavodila+"/koraki/korak_2.png")
korak3 = cv2.imread(pathNavodila+"/koraki/korak_3.png")
potrdi = cv2.imread(pathNavodila+"/koraki/potrdi.png")
zakljuci = cv2.imread(pathNavodila+"/koraki/zakljuci.png")
prepoznavanje = cv2.imread(pathNavodila+"/koraki/prepoznavanje.png")

img_height, img_width, _ = korak1.shape
img_height_o, img_width_o, _ = potrdi.shape





fps = 15

vflip = True
# za RPI uporabi tole metodo iz knjizice imutils
vs = VideoStream(usePiCamera=True, resolution=(frame_width, frame_height), framerate=fps, vflip=vflip).start()
time.sleep(2.0)


#lokacija navodil
x = int((frame_width-img_width)/2)
y = 0

#lokacija obvestil
x_o = int((frame_width-img_width_o)/2)
y_o = frame_height - img_height_o

#belo ozadje
white_background = np.zeros([frame_height,frame_width,3],dtype=np.uint8)
white_background.fill(255)



idRead = None
IdCount = 0

qrGenerate = None

organization = "FS"

created = None
brightness = 8 # Svetlost ledic od 0-31
ledWhite(brightness) # LEDICE
while True:
    if idRead == None:
        frame, roi = mainMrzLoop(vs)
        frame_copy = frame.copy()
        frame_copy[ y:y+img_height , x:x+img_width ] = korak1
        if roi is not None:
            IdCount +=1
            if IdCount==32:
                try: 
                    data = processMrz(roi, vflip)
                    if string_processor(data) is not None:
                        birthday, name = string_processor(data)
                        if birthday[0].isalpha():
                            birthday = birthday[13:19]
                        else:
                            birthday = birthday[:6]
                        if displayDataFromId(name, birthday) is not None:
                            namesString, birthdayString =  displayDataFromId(name, birthday)
                            IdCount = 0
                            idRead = True
                        else:
                            IdCount = 0
                            idRead =None
                    #lg.info(f'ID PREBRAN')
                    else:
                        IdCount = 0
                        idRead = None
                        continue
                except TypeError as e:
                    #lg.error(f'Exception reading ID: {e}')
                    idCount = 0
                    idRead = None
        if IdCount >=30:
            frame_copy[ y_o:y_o+img_height_o , x_o:x_o+img_width_o ] = prepoznavanje

    elif idRead == True and qrGenerate==None:
        ledOff()
        frame_copy = white_background.copy()
        frame_copy[ y:y+img_height , x:x+img_width ] = korak2
        frame_copy[ y_o:y_o+img_height_o , x_o:x_o+img_width_o ] = potrdi
        name_text = "Priimek in ime: " + namesString
        frame_copy = writeText(name_text, frame_copy, 1, 2, yOffset = -60)
        birthday_text = "Datum rojstva: " + birthdayString
        frame_copy = writeText(birthday_text, frame_copy, 1, 2, yOffset = 30)



    elif idRead == True and qrGenerate == True:
        frame_copy = white_background.copy()
        frame_copy[ y:y+img_height , x:x+img_width ] = korak3
        frame_copy[ y_o:y_o+img_height_o , x_o:x_o+img_width_o ] = zakljuci
        if created == None:
            jsonData = createJson(name, birthday, organization, "FS1:")
            created = createQr(jsonData)
            img = cv2.imread("personalqr.png")
            img = imutils.resize(img, 300)
            h, w, _ = img.shape
            hh, ww, _ = frame_copy.shape
            yoff = round((hh-h)/2)
            xoff = round((ww-w)/2)
            frame_copy[yoff:yoff+h, xoff:xoff+w] = img
        elif created == True:
            frame_copy[yoff:yoff+h, xoff:xoff+w] = img







# show the frame
    cv2.imshow(window_name, frame_copy)
    
    key = cv2.waitKey(1) & 0xFF
        # if the `q` key was pressed, break from the loop
    if key == ord("q"):
        ledOff()
        break

cv2.destroyAllWindows()
vs.stop()