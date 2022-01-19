import sys
import cv2
import numpy as np
from pyzbar.pyzbar import decode

import json
import zlib
import base45
import base64
import cbor2
from cose.messages import CoseMessage

import datetime



def decodeCovid(decodedString, QRVersion, orgStaff, orgTest):
    """Dekodira prebrani niz iz qr kode ter vrne json zapis"""
    if decodedString[:3] in QRVersion:
        return decodeJsonCovid(decodedString), "EU"
    elif decodedString[:3] == orgTest:
        return decodeJsonOrg(decodedString), "ORG-TEST"
    elif decodedString[:3] == orgStaff:
        return decodeJsonOrg(decodedString), "ORG-STAFF"
    else:
        return None, None


def decodeJsonOrg(encryptedJson):
    """za dekodiranje jsona costum organizacijske kode"""
    #odstranimo začetni string
    try:
        encryptedJson = encryptedJson[4:]
        encryptedJsonBytes = encryptedJson.encode('ascii')
        message_bytes = base64.b64decode(encryptedJsonBytes)
        message_bytes = zlib.decompress(message_bytes)
        decodedJson = message_bytes.decode('ascii')
    except ValueError or TypeError:
        print("poskusi ponovno")
    #print("Decoded JSON: ",decodedJson)
    return decodedJson


def decodeJsonCovid(encryptedJson):
    """Za dekodiranje official covid potrdil"""
    try:
        decoded = base45.b45decode(encryptedJson[4:])
        decompressed = zlib.decompress(decoded)
        cose = CoseMessage.decode(decompressed)
    except ValueError:
        print("poskusi ponovno")
    return json.dumps(cbor2.loads(cose.payload), indent=2)

def barcodeDetector(frame):
    """prebere qr kodo, jo označi da je prebrana in vrne prebrani niz"""
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    codes = decode(gray)
    for barcode in codes:
        pts = np.array([barcode.polygon], np.int32)
        pts = pts.reshape((-1, 1, 2))
        cv2.polylines(frame, [pts], True, (0, 255, 0), 3)
        if len(codes) > 1:
            print("Skeniraj le eno kodo na kmalu")
            break
        else:
            myData = barcode.data.decode("utf-8")
            return myData

def mainCovidLoop(video_stream, QRVersion, orgStaff, orgTest):
    """glavni loop za brnaje qr kode"""

    vs = video_stream

	# grab the frame from the threaded video stream and resize it
	# to have a maximum width of 400 pixels
    #za navadno kamero definiran se _
    frame = vs.read()

    qrdata = barcodeDetector(frame)
    if qrdata:
        decodeddata, jsontype = decodeCovid(qrdata, QRVersion, orgStaff, orgTest)
        return frame, decodeddata, jsontype
    return frame, None, None
            