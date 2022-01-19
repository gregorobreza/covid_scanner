import qrcode
import json
from pyzbar.pyzbar import decode
from PIL import Image
import base64
from datetime import datetime, timedelta
import numpy as np
import zlib
import cv2
import imutils

def validityDate():
    ''' Vrne datum, ko je bila koda narejena in datum do katerega je veljavna '''
    # Kako dolgo velja QR koda
    validityInDays = 7
    # Danasnji datum
    todayDate = datetime.today()
    # Veljavno do danasnji dan + 7 dni
    validUntilDate = todayDate + + timedelta(days=validityInDays)
    todayDate = todayDate.strftime('%Y-%m-%dT%H:%M:%SZ')
    validUntilDate = validUntilDate.strftime('%Y-%m-%dT%H:%M:%SZ')
    print("Valid until: ", validUntilDate)
    return todayDate, validUntilDate

def encryptJson(rawJson):
    jsonBytes = rawJson.encode('ascii')
    #Zakompresirano JSON
    jsonBytes = zlib.compress(jsonBytes)
    encryptedJsonBytes = base64.b64encode(jsonBytes)
    encryptedJson = encryptedJsonBytes.decode('ascii')
    #print("Encrypted JSON: ",encryptedJson)
    return encryptedJson

def decodeJson(encryptedJson):
    #odstranimo začetni string
    encryptedJson = encryptedJson[4:]
    encryptedJsonBytes = encryptedJson.encode('ascii')
    message_bytes = base64.b64decode(encryptedJsonBytes)
    message_bytes = zlib.decompress(message_bytes)
    decodedJson = message_bytes.decode('ascii')
    #print("Decoded JSON: ",decodedJson)
    return decodedJson

def createJson(names: str, dateValid: str , dateOfBirth: str, organization: str, startstring: str)->str:
    ''' Glavna funkcija, ki naredi JSON dokument in ga zakodira. '''
    # Pridobimo datum izdelave QR kode in datum veljavnosti
    #dateCreated, dateValid = validityDate()
    dateCreated = datetime.today()
    dateCreated = dateCreated.strftime('%Y-%m-%dT%H:%M:%SZ')
    #vzamemo se veljavnost s covid potrdila
    print(dateValid)
    if dateValid == True:
        dateValid = "2022-09-30T00:00:00Z"
        dateValid = datetime.strptime(dateValid, '%Y-%m-%dT%H:%M:%SZ')
        dateValid = dateValid.strftime('%Y-%m-%dT%H:%M:%SZ')
    else:
        dateValid = dateValid.strftime('%Y-%m-%dT%H:%M:%SZ')
    print(dateValid)
    ##########
    dataSet = {"Names": names, "Date of birth": dateOfBirth, "Organization": organization, "Date created": dateCreated, "Valid until": dateValid}
    jsonData = json.dumps(dataSet)
    print("Original JSON:\t", jsonData)
    # Zakodiramo JSON
    jsonData = encryptJson(jsonData)
    
    #dodamo se zacetni string da bomo locili med kodami string naj bo dolg 4 znake
    if len(startstring) != 4:
        raise ValueError('startstring shuld be 4 caracters long!')
    jsonData = startstring + jsonData
    print("Encrypted JSON:\t", jsonData)
    return jsonData

def createQr(jsonData):
    ''' Generira QR kodo iz JSON dokumenta '''
    # Generira QR kodo
    generatedQR =  qrcode.make(jsonData)
    # Shrani QR kodo
    generatedQR.save('personalqr.png')
    #img = imutils.resize(200)
    return True



def displayDataFromId(names, dateOfBirth):
    ''' Vrne dva stringa, ki se ju prikaže na ekranu pred potrditvijo '''
    namesLine = " "
    # Pripravi string iz imen
    namesString =  namesLine.join(names)
    
    # Naredi string iz datuma rojstva na osebni
    if int(dateOfBirth[:2]) > 21 and int(dateOfBirth[:2]) <=99:
        yearString = "19" + dateOfBirth[:2]
    else:
        yearString = "20" + dateOfBirth[:2]

    birthdayString =  dateOfBirth[4:6]+"." + dateOfBirth[2:4] + "." + yearString

    print("Ime in priimek: {}\nDatum rojstva: {}".format(namesString, birthdayString))
    return namesString, birthdayString
    



# ZA TESTIRANJE
def barcodeDetector(frame):
    """ Prebere qr kodo, jo označi da je prebrana in vrne prebrani niz """
    codes = decode(frame)
    for barcode in codes:
        if len(codes) > 1:
            print("Skeniraj le eno kodo na kmalu")
            break
        else:
            myData = barcode.data.decode("utf-8")
            print("JSON from QR:\t", myData)
            myData = decodeJson(myData)
            print("Decoded JSON:\t", myData)
            return myData






# # Test Data
# names = ["Speh", "Jure"]
# dateOfBirth = "980226"
# organization = "FS"

# # Create JSON
# jsonData = createJson(names, dateOfBirth, organization)
# # Create QR Code
# createQr(jsonData)
# # Open QR Code
# frame = Image.open('qrtest1.png')
# # Print contetnt
# barcodeDetector(frame)

# displayDataFromId(names, dateOfBirth)