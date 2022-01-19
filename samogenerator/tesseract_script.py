#!/home/pi/covid/env/pct/bin/python3
import locale
locale.setlocale(locale.LC_ALL, 'C')
import sys
import pytesseract
import os
import cv2
import numpy as np
from PIL import Image
import tesserocr
#import logging as lg

def fix_name(name):
    """Zamenja stevilke za karaktereje, izloci male crke"""
    ime_list = list(name)
    for index, i in enumerate(ime_list):
        if i.islower():
            ime_list[index] = "<"
        elif i == "1":
            ime_list[index] = "I"
        elif i == "7":
            ime_list[index] = "Z"
        elif i == "8":
            ime_list[index] = "S"#tu bi bil lahko tudi B??
        elif i == "0" or i == "9":
            ime_list[index] = "O"
        elif i == "5":
            ime_list[index] = "G"
        elif i == "2":
            ime_list[index] = "Z"

    return "".join(ime_list)   

def fix_emso(birth_date):
    "zamenja mozne crke za stevilke"
    birth_date_list = list(birth_date)
    for index, i in enumerate(birth_date_list):
        if i.islower():
            birth_date_list[index] = "<"
        elif i == "I":
            birth_date_list[index] = "1"
        elif i == "Z":
            birth_date_list[index] = "7"
        elif i == "S" or i == "B":
            birth_date_list[index] = "8"#tu bi bil lahko tudi B??
        elif i == "O":
            birth_date_list[index] = "0"

    return "".join(birth_date_list)   


def string_processor(data):
    """le za uporabo v nadalnjih skriptah za obdelavo nizov"""
    #odstranimo presletke in prazne vrstice
    data = data.replace(" ", "")
    data = os.linesep.join([s for s in data.splitlines() if s])

    #naredimo seznam iz posamezne vrste 
    data = data.splitlines()

    #popravimo mozne crke in stevilke
    if len(data) ==2 and data[-1][0]=="P":
        birth_date = fix_emso(data[-1])
        ime = fix_name(data[-2])

        return birth_date, ime

    elif len(data) == 2 and data[0][:2] == "ID":
        birth_date = fix_emso(data[-1])
        ime = fix_name(data[-2] + data[-1])
        return birth_date, ime

    #popravimo mozne crke in stevilke
    elif len(data) == 3:
        birth_date = fix_emso(data[1])
        ime = fix_name(data[2])
        return birth_date, ime
    else:
        return None

def readText(img, q, vflip):
    """Za uporabo v kombinaciji z detekcijo dodajamo v query ker ga ženemo v drugem procesu"""
    import locale
    locale.setlocale(locale.LC_ALL, 'C')
    if vflip == True:
        img = cv2.flip(img, 1)
    img = Image.fromarray(img)
    mrz = tesserocr.image_to_text(img, lang="mrz")
    #mrz = pytesseract.image_to_string(img, config="--psm 6 --oem 3", lang="mrz")
    q.put(mrz)
    #return mrz

def processMrz(img, vflip):
    import locale
    locale.setlocale(locale.LC_ALL, 'C')
    if vflip ==True:
        img = cv2.flip(img, 1)
    img = Image.fromarray(img)
    data = tesserocr.image_to_text(img, lang="mrz")
    return data


def OCR_image(img):
    
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    #beremo txt iz slike
    data = pytesseract.image_to_string(gray, lang='eng', config='--psm 6 --oem 3')

    #odstranimo presletke in prazne vrstice
    data = data.replace(" ", "")
    data = os.linesep.join([s for s in data.splitlines() if s])

    #naredimo seznam iz posamezne vrste 
    data = data.splitlines()

    #popravimo mozne crke in stevilke
    birth_date = fix_emso(data[1])
    ime = fix_name(data[2])

    print(birth_date)
    print(ime)
    #lg.info(f'Ime: {ime} | rojstni datum: {birth_date}')
    return birth_date, ime


if __name__ == "__main__":
    image = cv2.imread("bla.jpg")
    OCR_image(image)
