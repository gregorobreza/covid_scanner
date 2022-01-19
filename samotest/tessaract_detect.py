#odpravi nekbug
import locale
locale.setlocale(locale.LC_ALL, 'C')

import tesserocr
from PIL import Image
import cv2
import imutils
import os


#vzorec = Image.open("vzorec.jpg")
# vzorec = cv2.imread("vzorec.jpg")
# vzorec = imutils.resize(vzorec, width=400)
# vzorec = cv2.cvtColor(vzorec, cv2.COLOR_BGR2GRAY)
# vzorec = Image.fromarray(vzorec)
#tesserocr.PyTessBaseAPI(path='/usr/share/tesseract-ocr/4.00/tessdata')


def string_processor(data):
    """le za uporabo v nadalnjih skriptah za obdelavo nizov"""
    #odstranimo presletke in prazne vrstice
    data = data.replace(" ", "")
    data = os.linesep.join([s for s in data.splitlines() if s])

    #naredimo seznam iz posamezne vrste 
    data = data.splitlines()

    #popravimo mozne crke in stevilke
    if len(data) ==2 and data[-1][0]=="P":
        birth_date = data[-1]
        ime = data[-2]
        ime = ime.split("<")
        
        if len(ime[0])==1:
            ime.remove(ime[0])
            
        if len(ime[0]) > 1:
            #V imenu se odstrani prve tri crke, ki pomenijo drzavo
            imeInDrzava = ime[0]
            ime[0] = imeInDrzava[3:]
            
        ime = [x for x in ime if x]


        return birth_date, ime

    elif len(data) == 2 and data[0][:2] == "ID":
        druga = data[-1]
        druga = druga.split("<")
        birth_date = druga[-1]
        ime = druga
        ime[0] = ime[0][13:]
        ime = [x for x in ime if x]
        ime.pop()
  

        priimek = data[0]
        priimek = priimek.split("<")
        priimek[0] = priimek[0][5:]
        priimek = [x for x in priimek if x]
        priimek.pop()

        
        ime = priimek + ime

        return birth_date, ime

        
    elif len(data) == 3:
        birth_date = data[-2]
        ime = data[-1]
        ime = ime.split("<")
        ime = [x for x in ime if x]

        return birth_date, ime
    else:
        return None

def processMrz(img, vflip):
    import locale
    locale.setlocale(locale.LC_ALL, 'C')
    if vflip ==True:
        img = cv2.flip(img, 1)
    img = Image.fromarray(img)
    data = tesserocr.image_to_text(img, lang="mrz")
    return data


def displayDataFromId(names, dateOfBirth):
    ''' Vrne dva stringa, ki se ju prikaže na ekranu pred potrditvijo '''
    namesLine = " "
    # Pripravi string iz imen
    namesString =  namesLine.join(names)

    try:

        # Naredi string iz datuma rojstva na osebni
        if int(dateOfBirth[:2]) > 21 and int(dateOfBirth[:2]) <=99:
            yearString = "19" + dateOfBirth[:2]
        else:
            yearString = "20" + dateOfBirth[:2]

        birthdayString =  dateOfBirth[4:6]+"." + dateOfBirth[2:4] + "." + yearString

        #print("Priimek in ime: {}\nDatum rojstva: {}".format(namesString, birthdayString))
        return namesString, birthdayString
    except ValueError:
        return None

def displayDataPassport():
    pass