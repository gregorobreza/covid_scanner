#!/home/pi/pct_scan/env/pct/bin/python3
#0.1.1
from os import name
import sys
from imutils.video import VideoStream
import datetime
import imutils
import time
import cv2
import multiprocessing as mp
import numpy as np
import yaml
from leds import ledWhite, ledGreen, ledRed, ledOff
import getpass
from subprocess import Popen, PIPE

#uvoz nasih funkcij
from qrDetectorFin import mainCovidLoop
from autoDetectMrzFin import mainMrzLoop
from tesseract_script import readText, string_processor, processMrz
from validation import qrEuValidityCheck, identityCheck, qrOrgValidityCheck
from sound import validBuzz, invalidBuzz

#uvoz fullscreen
import screeninfo

# uvoz logging
#import logging as lg
#lg.basicConfig(filename='/home/pi/pct_scan/pct/video-stream.log', level=lg.INFO, filemode='a', format='%(asctime)s - %(levelname)s : %(message)s')

user_name = getpass.getuser()
#uvoz konfiguracije
pathConfig = f'/home/{user_name}/pct_scan/'

with open(pathConfig + "main.yaml", "r") as stream, open(pathConfig + "organization.yaml", "r") as stream_org:
    try:
        data = yaml.safe_load(stream)
        data_org = yaml.safe_load(stream_org)
    except yaml.YAMLError as exc:
        print(exc)

#splosne
veljavnost_pcr = data["veljavnost_pcr"]
veljavnost_hitri = data["veljavnost_hitri"]
podaljsek_prebolelosti = data["podaljsek_prebolelosti"]
cepiva = data["cepiva"]
qr_verzija = data["qr_verzija"]
timer = data["korak2_timer"]
#vezane na organizacijo
vrsta_potrditve = data_org["vrsta_potrditve"]
timer_full_banner = data_org["banner_timer"]
organizacija_test = data_org["organizacija_test"]
organizacija_staff = data_org["organizacija_staff"]
ocr_algorythm = data_org["ocr_algorythm"]
cas_zazanavanja = data_org["cas_zazanavanja"]
brightness = data_org["osvetlitev"]
vrata = data_org["vrata"]
vrata_timer = data_org["vrata_timer"]

def back(event,x, y, flags, param):
    global covidValidity
    global idValidity
    global qr_count
    global IdCount
    global validation_count
    global notification_count
    global fps
    global timer
    global korak2_timer
    global banner_to_full
    global vrsta_potrditve
    global banner_timer
    global banner_to_full_korak2
    if event == cv2.cv2.EVENT_LBUTTONDOWN:
        mouseX,mouseY = x,y
        if covidValidity == True:
            if mouseX <= 50 and mouseY < frame_height-400:
                # button back
                ledWhite(brightness)
                covidValidity = None
                idValidity = None
                qr_count = 0
                IdCount = 0
                validation_count = 0
                notification_count = 0
                korak2_timer = fps * timer
                banner_timer = fps * timer_full_banner
                banner_to_full, banner_to_full_korak2 = potrditev(vrsta_potrditve)
        elif vrsta_potrditve == "full_page" and banner_to_full == True:
            # All for full page aceptance
            if mouseY > frame_height-80 and banner_to_full_korak2 == None:
                banner_to_full = None
                banner_timer = fps * timer_full_banner
            elif mouseY > frame_height-80 and banner_to_full_korak2 == True:
                banner_to_full = True
                banner_to_full_korak2 = None
            elif mouseY < frame_height-95 and mouseY > frame_height -135:
                banner_to_full_korak2 = True
        #All for mini banner
        elif covidValidity == None and banner_to_full == True:
            # Exit banner
            if mouseY > frame_height-80:
                banner_to_full = None
        elif covidValidity == None and vrsta_potrditve == "banner":
            # Click for banner
            if mouseX >= 270 and mouseY > frame_height-20:
                banner_to_full = True



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



# Dodaj path do mape kjer se nahaja skripta in mapa s slikami za GUI
pathNavodila = f'/home/{user_name}/pct_scan/pct'
# Dodaj path do mape kjer se nahajo slike za strinjanje s pogoji
pathGDPR = f'/home/{user_name}/Pictures'

#uvoz slik za prikaz UI
korak1 = cv2.imread(pathNavodila+"/navodila/korak1.png")
korak2 = cv2.imread(pathNavodila+"/navodila/korak2.png")
ustrezno = cv2.imread(pathNavodila+"/navodila/ustrezno.png")
neustrezno = cv2.imread(pathNavodila+"/navodila/neustrezno.png")
prepoznavanje = cv2.imread(pathNavodila+"/navodila/prepoznavanje.png")
poskusi = cv2.imread(pathNavodila+"/navodila/poskusi_ponovno.png")
#zasloni za GDPR vedno preveri path!
mini_banner = cv2.imread(pathGDPR+"/mini_banner.png")
info_izjava = cv2.imread(pathGDPR+"/info_izjava.png")
full_izjava = cv2.imread(pathGDPR+"/full_izjava.png")
full_izjava_korak2 = cv2.imread(pathGDPR+"/full_izjava_korak_2.png")

img_height, img_width, _ = korak1.shape
img_height_o, img_width_o, _ = ustrezno.shape

banner_height, banner_width, _ = mini_banner.shape
info_height, info_width, _ = info_izjava.shape


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

x_banner = int((frame_width-banner_width)/2)
y_banner = frame_height - banner_height

#kamera za komp
#vs = cv2.VideoCapture(0)


covidValidity = None
idValidity = None

def potrditev(vrsta_potrditve):
    if vrsta_potrditve == "full_page":
        banner_to_full = True
        banner_to_full_korak2 = None
    else:
        banner_to_full = None
        banner_to_full_korak2 = None
    return banner_to_full, banner_to_full_korak2

banner_to_full, banner_to_full_korak2 = potrditev(vrsta_potrditve)
#kolikokran naj zazna qr kodo in osebno da nato spusti naprej manjša možnost napake...
qr_count = 0
IdCount = 0
validation_count = 0

#da se prikaze za nekaj sekund
notification_count = 0

#timer = 30
korak2_timer = fps * timer

#timer_full_banner
banner_timer = fps * timer_full_banner


rectKernel = cv2.getStructuringElement(cv2.MORPH_RECT, (13, 5))
sqKernel = cv2.getStructuringElement(cv2.MORPH_RECT, (21, 21))

ledWhite(brightness) # LEDICE
while True:

    #preverjanje le covid potrdila
    if covidValidity == None:
        # ce ni veljavno najprej izvedi branj qr kode
        frame, coviddata, jsontype = mainCovidLoop(vs, qr_verzija, organizacija_staff, organizacija_test)
        frame_copy = frame.copy()
        frame_copy[ y:y+img_height , x:x+img_width ] = korak1
        if vrsta_potrditve == "banner" and banner_to_full == None:
            frame_copy[ y_banner:y_banner+img_height , x_banner:x_banner+img_width ] = mini_banner
        elif vrsta_potrditve == "banner" and  banner_to_full == True:
            frame_copy[ y:480, x:800 ] = info_izjava
            banner_timer -= 1
        elif vrsta_potrditve == "full_page" and banner_to_full == True and banner_to_full_korak2 == True:
            frame_copy[ y:480, x:800 ] = full_izjava_korak2
            banner_timer -= 0.5
        elif vrsta_potrditve == "full_page" and banner_to_full == True:
            frame_copy[ y:480, x:800 ] = full_izjava
        elif vrsta_potrditve == "full_page" and banner_to_full == None:
            banner_timer -= 1
        if coviddata and banner_to_full == None:
            qr_count += 1
            if qr_count == 2:
                #print(coviddata)
            
                if jsontype == "EU":
                    #ce je koda EU potrdilo
                    try:
                        covidValidity, names, birthday = qrEuValidityCheck(coviddata, podaljsek_prebolelosti, cepiva, veljavnost_pcr, veljavnost_hitri)
                        
                    except Exception as e:
                        pass
                        #lg.error(f'Exception reading {jsontype} QR: {e}')
                elif jsontype == "ORG-TEST":
                    #ce je koda vezana le na organizacijo
                    try:
                        covidValidity, names, birthday = qrOrgValidityCheck(coviddata)
                        
                    except Exception as e:
                        pass
                        #lg.error(f'Exception reading {jsontype} QR: {e}')
                    if covidValidity == True:
                        idValidity = True
                elif jsontype == "ORG-STAFF":
                    #ce je koda vezana le na organizacijo
                    try:
                        covidValidity, names, birthday = qrOrgValidityCheck(coviddata)
                    except Exception as e:
                        pass
                        #lg.error(f'Exception reading {jsontype} QR: {e}')
                    if covidValidity == True:
                        idValidity = True
        if banner_timer == 0 and vrsta_potrditve == "banner":
            banner_to_full = None
            banner_timer = fps * timer_full_banner
        elif banner_timer == 0 and vrsta_potrditve == "full_page" and banner_to_full_korak2==True:
            banner_to_full = True
            banner_to_full_korak2 = None
            banner_timer = fps * timer_full_banner
        elif banner_timer == 0 and vrsta_potrditve == "full_page":
            banner_to_full = True
            banner_timer = fps * timer_full_banner

                    
                
                    
    # #ko je potrdilo veljavno preidemo na preverjanje osebne iskaznice
    elif covidValidity == True:
        korak2_timer -= 1
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
                if IdCount == cas_zazanavanja:
                    #print("cas za prepoznavanje")
                    #lg.info('Prepoznavanje ID...')
                    try:
                        data = processMrz(roi, vflip, ocr_algorythm)
                        if string_processor(data) is not None:
                            birthdayFromID, namesFromID = string_processor(data)
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
                            continue
                    except TypeError as e:
                        #lg.error(f'Napaka pri branju osebne: {e}')
                        idCount = 0
                        idValidity = None
            if validation_count >= 1:
                frame_copy[ y_o:y_o+img_height_o , x_o:x_o+img_width_o ] = poskusi
            if IdCount >= cas_zazanavanja-2:
                frame_copy[ y_o:y_o+img_height_o , x_o:x_o+img_width_o ] = prepoznavanje
            if korak2_timer == 0:
                IdCount = 0
                qr_count = 0
                covidValidity = None
                idValidity = None
                notification_count = 0
                validation_count = 0
                korak2_timer = fps * timer
                banner_to_full, banner_to_full_korak2 = potrditev(vrsta_potrditve)
                banner_timer = fps * timer_full_banner
                ledWhite(brightness)
    

    if covidValidity and idValidity is True:
        #print("oboje ustrezno")
        
        frame_copy[ y_o:y_o+img_height_o , x_o:x_o+img_width_o ] = ustrezno
        notification_count += 1
        IdCount = 0
        qr_count = 0
        ledGreen(15) # LEDICE
        if vrata == True and notification_count == 1:
            Popen(["./reley.py", "-t", str(vrata_timer)])
        if notification_count == 2:
            validBuzz()
        if notification_count == int(fps*2.7):
            #lg.info('USTREZNO')
            #lg.info('-----------------------------')
            covidValidity = None
            idValidity = None
            notification_count = 0
            validation_count = 0
            korak2_timer = fps * timer
            banner_timer = fps * timer_full_banner
            ledWhite(brightness)  # LEDICE
            banner_to_full, banner_to_full_korak2 = potrditev(vrsta_potrditve)


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
            korak2_timer = fps * timer
            banner_timer = fps * timer_full_banner
            ledWhite(brightness)  # LEDICE
            banner_to_full,banner_to_full_korak2 = potrditev(vrsta_potrditve)
 

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
            korak2_timer = fps * timer
            banner_timer = fps * timer_full_banner
            ledWhite(brightness) # LEDICE
            banner_to_full, banner_to_full_korak2 = potrditev(vrsta_potrditve)



# show the frame
    cv2.imshow(window_name, frame_copy)
    
    key = cv2.waitKey(1) & 0xFF
        # if the `q` key was pressed, break from the loop
    if key == ord("q"):
        ledOff()
        break

cv2.destroyAllWindows()
vs.stop()


