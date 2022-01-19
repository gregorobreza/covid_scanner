#!/home/pi/pct_scan/env/pct/bin/python3
#0.1.0
from os import name
import sys
from imutils.video import VideoStream
import datetime
import imutils
import time
import cv2
import multiprocessing as mp
import numpy as np
from leds import ledWhite, ledGreen, ledRed, ledOff

#uvoz nasih funkcij
from qrDetectorFin import mainCovidLoop
from autoDetectMrzFin import mainMrzLoop
from tesseract_script import readText, string_processor, processMrz
from validation import qrEuValidityCheck, identityCheck, qrOrgValidityCheck
from sound import validBuzz, invalidBuzz
from makeqr import createJson, createQr

from display_text import writeText

#uvoz fullscreen
import screeninfo

# uvoz logging
#import logging as lg
#lg.basicConfig(filename='/home/pi/pct_scan/pct/video-stream.log', level=lg.INFO, filemode='a', format='%(asctime)s - %(levelname)s : %(message)s')

def back(event, x,y,flags,param):
    global mouseX,mouseY
    global covidValidity
    global idValidity
    global qr_count
    global IdCount
    global validation_count
    global notification_count
    global qrGenerate
    global countdown
    global created
    if event == cv2.cv2.EVENT_LBUTTONDOWN:
        if covidValidity == True and qrGenerate == None:
            #cv2.circle(frame_copy,(x,y),100,(255,0,0),-1)
            mouseX,mouseY = x,y
            if mouseX <= 50 and mouseY < frame_height-400:
                created = None
                covidValidity = None
                idValidity = None
                qrGenerate = None
                qr_count = 0
                IdCount = 0
                validation_count = 0
                notification_count = 0
        elif idValidity == True and qrGenerate == True:
            #cv2.circle(frame_copy,(x,y),100,(255,0,0),-1)
            mouseX,mouseY = x,y
            if mouseY > frame_height-80:
                covidValidity = None
                idValidity = None
                qrGenerate = None
                created = None
                qr_count = 0
                IdCount = 0
                validation_count = 0
                notification_count = 0
                ledWhite(brightness)  # LEDICE


#definicija parametrov za nas zaslon
screen_id = 0
screen = screeninfo.get_monitors()[screen_id]
frame_width, frame_height = screen.width, screen.height

window_name = 'projector'
cv2.namedWindow(window_name, cv2.WND_PROP_FULLSCREEN)
cv2.moveWindow(window_name, screen.x - 1, screen.y - 1)
cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
cv2.setMouseCallback(window_name, back)
# get the size of the screen



#uvoz slik za prikaz UI
'''
korak1 = cv2.imread("./navodila/korak1.png")
korak2 = cv2.imread("./navodila/korak2.png")
ustrezno = cv2.imread("./navodila/ustrezno.png")
neustrezno = cv2.imread("./navodila/neustrezno.png")
prepoznavanje = cv2.imread("./navodila/prepoznavanje.png")
poskusi = cv2.imread("./navodila/poskusi_ponovno.png")
'''
# Dodaj path do mape kjer se nahaja skripta in mapa s slikami za GUI
pathNavodila = "/home/pi/pct_scan/samogenerator"

korak1 = cv2.imread(pathNavodila+"/navodila/korak1.png")
korak2 = cv2.imread(pathNavodila+"/navodila/korak2.png")
korak3 = cv2.imread(pathNavodila+"/navodila/korak3.png")
ustrezno = cv2.imread(pathNavodila+"/navodila/ustrezno.png")
neustrezno = cv2.imread(pathNavodila+"/navodila/neustrezno.png")
prepoznavanje = cv2.imread(pathNavodila+"/navodila/prepoznavanje.png")
poskusi = cv2.imread(pathNavodila+"/navodila/poskusi_ponovno.png")
zakljuci = cv2.imread(pathNavodila+"/navodila/zakljuci.png")

img_height, img_width, _ = korak1.shape
img_height_o, img_width_o, _ = ustrezno.shape

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

#kamera za komp
#vs = cv2.VideoCapture(0)


covidValidity = None
idValidity = None
qrGenerate = None
created = None
#kolikokran naj zazna qr kodo in osebno da nato spusti naprej manjša možnost napake...
qr_count = 0
IdCount = 0
validation_count = 0


#da se prikaze za nekaj sekund
notification_count = 0

organization = "FS"

rectKernel = cv2.getStructuringElement(cv2.MORPH_RECT, (13, 5))
sqKernel = cv2.getStructuringElement(cv2.MORPH_RECT, (21, 21))


#belo ozadje
white_background = np.zeros([frame_height,frame_width,3],dtype=np.uint8)
white_background.fill(255)

brightness = 8 # Svetlost ledic od 0-31
ledWhite(brightness) # LEDICE
while True:

    #preverjanje le covid potrdila
    if covidValidity == None:
        
        # ce ni veljavno najprej izvedi branj qr kode
        frame, coviddata, jsontype = mainCovidLoop(vs)
        frame_copy = frame.copy()
        frame_copy[ y:y+img_height , x:x+img_width ] = korak1
        if coviddata:
            qr_count += 1
            if qr_count == 3:
                #print(coviddata)
            
                if jsontype == "EU":
                    #ce je koda EU potrdilo
                    try:
                        covidValidity, dateValid, names, birthday = qrEuValidityCheck(coviddata)

                    except Exception as e:
                        qr_count = 0
                        
                        #lg.error(f'Exception reading {jsontype} QR: {e}')
                else:
                    covidValidity = None
                    idValidity = None
                    qrGenerate = None
                    created = None
                    qr_count = 0
                    IdCount = 0
                    validation_count = 0
                
                    
    # #ko je potrdilo veljavno preidemo na preverjanje osebne iskaznice
    elif covidValidity == True and qrGenerate == None:
        if idValidity ==  True:
            pass
        else:
            frame, roi = mainMrzLoop(vs)
            #prikazi navodilo
            frame_copy = frame.copy()
            frame_copy[ y:y+img_height , x:x+img_width ] = korak2
            if roi is not None:
            #print("slika")
                IdCount += 1
                if IdCount == 32:
                    #print("cas za prepoznavanje")
                    #lg.info('Prepoznavanje ID...')
                    try:
                        data = processMrz(roi, vflip)
                        if string_processor(data) is not None:
                            birthdayFromID, namesFromID = string_processor(data)
                            #print(birthdayFromID)
                            #print(namesFromID)
                            idValidity = identityCheck(names, birthday, namesFromID, birthdayFromID)
                            if idValidity == False:
                                validation_count += 1
                                IdCount = 0
                                #print(validation_count)
                            continue
 
                        else:
                            IdCount = 0
                            #lg.warning('Ni vseh vrstic...')
                            #print("ni vseh vrstic")
                        #frame_copy[ y_o:y_o+img_height_o , x_o:x_o+img_width_o ] = prepoznavanje
                            continue
                    except TypeError as e:
                        #lg.error(f'Napaka pri branju osebne: {e}')
                        idCount = 0
                        idValidity = None
            if validation_count >= 1:
                frame_copy[ y_o:y_o+img_height_o , x_o:x_o+img_width_o ] = poskusi
            if IdCount >= 30:
                frame_copy[ y_o:y_o+img_height_o , x_o:x_o+img_width_o ] = prepoznavanje

    # elif idValidity ==  True and qrGenerate == True:
    #     ledOff()
    #     frame_copy = white_background.copy()
    #     frame_copy[ y:y+img_height , x:x+img_width ] = korak3
    #     frame_copy[ y_o:y_o+img_height_o , x_o:x_o+img_width_o ] = zakljuci

    if covidValidity == True and idValidity == True:
        qrGenerate = True
        #print("oboje ustrezno")
        if IdCount > 0:
            frame_copy[ y_o:y_o+img_height_o , x_o:x_o+img_width_o ] = ustrezno
        notification_count += 1
        IdCount = 0
        qr_count = 0
        ledGreen(15) # LEDICE
        
        if notification_count == 2:
            validBuzz()
        if notification_count == int(fps*2.7):
            #lg.info('USTREZNO')
            #lg.info('-----------------------------')
            ledOff()
            frame_copy = white_background.copy()
            frame_copy[ y:y+img_height , x:x+img_width ] = korak3
            frame_copy[ y_o:y_o+img_height_o , x_o:x_o+img_width_o ] = zakljuci
            
            
            #covidValidity = None
            #idValidity = None
            notification_count = int(fps*2.7)
            if created == None:
                jsonData = createJson(names, dateValid, birthday, organization, "FS1:")
                created = createQr(jsonData)
                img = cv2.imread("personalqr.png")
                img = imutils.resize(img, 300)
                img = imutils.resize(img, 300)
                h, w, _ = img.shape
                hh, ww, _ = frame_copy.shape
                yoff = round((hh-h)/2)
                xoff = round((ww-w)/2)
                frame_copy[yoff:yoff+h, xoff:xoff+w] = img
                created = True
            elif created == True:
                frame_copy[yoff:yoff+h, xoff:xoff+w] = img                
                
                #ledWhite(brightness)  # LEDICE
                #qrGenerate == True


    elif covidValidity == False:
        frame_copy[ y_o:y_o+img_height_o , x_o:x_o+img_width_o ] = neustrezno
        notification_count += 1
        IdCount = 0
        qr_count = 0
        ledRed(15) # LEDICE
        if notification_count == 2:
            invalidBuzz()
        if notification_count == int(fps*0.2):
            #lg.warning(f'NEUSTREZNO - covid QR: {covidValidity} | ID status: {idValidity}')
            #lg.info('-----------------------------')
            covidValidity = None
            idValidity = None
            notification_count = 0
            validation_count = 0
            qr_count = 0
            ledWhite(brightness)  # LEDICE
 

    elif covidValidity == True and idValidity == False and validation_count == 3:
        frame_copy[ y_o:y_o+img_height_o , x_o:x_o+img_width_o ] = neustrezno
        notification_count += 1
        IdCount = 0
        qr_count = 0
        ledRed(15) # LEDICE
        if notification_count == 2:
            invalidBuzz()
        if notification_count == int(fps*0.2):
            #lg.warning(f'NEUSTREZNO - covid QR: {covidValidity} id status: {idValidity}')
            #lg.info('-----------------------------')
            covidValidity = None
            idValidity = None
            notification_count = 0
            validation_count = 0
            ledWhite(brightness) # LEDICE



# show the frame
    cv2.imshow(window_name, frame_copy)
    
    key = cv2.waitKey(1) & 0xFF
        # if the `q` key was pressed, break from the loop
    if key == ord("q"):
        ledOff()
        break

cv2.destroyAllWindows()
vs.stop()

