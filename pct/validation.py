import re
import sys
import json
from datetime import datetime, timedelta
import logging as lg


def qrOrgValidityCheck(coviddata: str):
    covidDict = json.loads(coviddata)
    #print(coviddata)

    names = covidDict['Names']
    birthday = covidDict['Date of birth']

    validity = checkCustomValidity(covidDict)

    return validity, names, birthday


def qrEuValidityCheck(coviddata: str, extendedRecoveryDays, possibleVaccines, pcrValid, hagValid) -> bool:
    """
    Preveri veljavnost le covid potrdila vrne True če je potrdilo v skladu s
    PCT in False če ni v skladu s trenutnimi PCT.
    Vrne tudi listo z vsemi imeni in priimki na QR kodi (names) in string z datumom rojstva na QR kodi (birthday)
    """
    covidDict = json.loads(coviddata)
    #poberemo le informacije, ki nas zanimajo
    #print(coviddata)
    #print(covidDict)
    # Preberemo v katero skupino spada certifikat
    groupIdentifier, covidListData = checkStatus(covidDict)

    # Izvedemo preverjanje veljavnosti glede na skupino
    if groupIdentifier == "r":
        validity = recoveredCheck(covidListData, extendedRecoveryDays)
    elif groupIdentifier == "v":
        validity = vaccinatedCheck(covidListData, possibleVaccines)
    elif groupIdentifier == "t":
        validity = testedCheck(covidListData, pcrValid, hagValid)
    else:
        #lg.warning(f'Napacen EU COVID certifikat.')
        print("Error: Undefined group of certificate...")
    
    # 'names' vkljucuje imena in priimke v obliki python liste
    # 'birthday' je v obliki YYMMDD, kot je na osebni izkaznici (2. vrstica)
    names, birthday = makeIdentityList(covidDict)

    return validity, names, birthday



def checkStatus(jsonData: str) -> str:
    """Preveri status certifikata: prebolel: 'r', cepljen: 'v', testiran: 't' 
    vrne string, ki vsebuje r, v ali t. V argument jsonData podamo JSON dokument.
    """
    if '-260' in jsonData:
        if '1' in jsonData['-260']:
            if 'r' in jsonData['-260']['1']:
                #print("RECOVERED")
                covidListData = jsonData['-260']['1']['r'] 
                return "r", covidListData
            elif 'v' in jsonData['-260']['1']:
                #print("VACCINATED")
                covidListData = jsonData['-260']['1']['v']
                return "v", covidListData
            elif 't' in jsonData['-260']['1']:
                #print("TESTED")
                covidListData = jsonData['-260']['1']['t']
                return "t", covidListData
        else:
            #lg.info('Ni pozicije st. 1 v EU certifikatu.')
            print("Error: No value '1'...")
    else:
        #lg.info('Ni pozicije st. -260 v EU certifikatu.')
        print("Error: No value '-260'... ")


def recoveredCheck(covidListData: str, extendedRecoveryDays=0)-> bool:
    """
    Funkcija preveri ce je status prebolevnika ze/se veljaven. Argument je list
    """
    #print("Performing recovered group certificate check...")

    # Pridobi slovar znotraj liste za 'r'
    nestedDict = covidListData[0]
    #print("Nested dict: ", nestedDict)

    # Pridobi prvi in zadnji veljaven datum za prebolevnika
    strFirstValid = nestedDict['df']
    strLastValid = nestedDict['du']
    # V SLO je veljavost prebolevnega certifikata podaljsana iz originalne EU 180 dni na 240 dni
    #extendedRecoveryDays = 0
    #print("Certificate valid from {} to {}. Type of date: {}".format(strFirstValid, strLastValid, type(strFirstValid)))

    # Iz stringa datuma dobimo realen datum (tip datetime.datetime)
    dateFirstValid = datetime.strptime(strFirstValid, '%Y-%m-%d')
    dateLastValid = datetime.strptime(strLastValid, '%Y-%m-%d')

    # Pristejemo dodatnih 60 dni za veljavnost statusa prebolevnika
    dateLastValid = dateLastValid + timedelta(days=extendedRecoveryDays)
    todayDate = datetime.today()
    # Preverimo, ce smo znotraj datuma veljavnosti
    if todayDate >= dateFirstValid and todayDate <= dateLastValid:
        #print("Certificate valid! Valid until: {}".format(dateLastValid))
        #lg.info('Certifikat veljaven.')
        return True
    elif todayDate < dateFirstValid or todayDate > dateLastValid:
        #print("Certificate invalid!")
        #lg.info('Certifikat ni veljaven.')
        return False


def vaccinatedCheck(covidListData: str, possibleVaccines)-> bool:
    """
    Funkcija preveri ce je status cepljenega ze veljaven.
    """
    #print("Performing vaccinated group certificate check...")

    # Slovar proizvajalcev za vsak slucaj
    vaccBrands = {"ORG-100001699": "AstraZeneca AB","ORG-100030215":  "Biontech Manufacturing GmbH", "ORG-100001417":"Janssen-Cilag International", "ORG-100031184": "Moderna Biotech Spain S.L.", "ORG-100006270":"Curevac AG", "ORG-100013793":"CanSino Biologics" ,"ORG-100020693":"China Sinopharm International Corp. - Beijing location" , "ORG-100010771":"Sinopharm Weiqida Europe Pharmaceutical s.r.o. - Prague location","ORG-100024420":"Sinopharm Zhijun (Shenzhen) Pharmaceutical Co. Ltd. - Shenzhen location",  "ORG-100032020": "Novavax CZ AS", "Gamaleya-Research-Institute":"Gamaleya Research Institute", "Vector-Institute":"Vector Institute","Sinovac-Biotech":"Sinovac Biotech","Bharat-Biotech":"Bharat Biotech"   }
    # Pridobi slovar znotraj liste za 'v'
    nestedDict = covidListData[0]
    #print("Nested dict: ", nestedDict)
    #Pridobimo ime cepiva
    vaccineBrand = nestedDict['mp']
    # Mozna cepiva pri nas
    #possibleVaccines = ["EU/1/20/1528", "EU/1/20/1507","Sputnik-V" ,"CoronaVac" , "InactivatedSARS-CoV-2-Vero-Cell","EU/1/21/1529","CVnCoV"]
    # Preverimo, ce se ime cepiva ujema z enim od nastetih
    if vaccineBrand in possibleVaccines:
        #print("Cepivo: {}".format(vaccineBrand))
        # 'dn' stevilo prejetih doz, 'sd' stevilo potrebnih doz
        if nestedDict['dn'] == nestedDict['sd']:
            #print("Certificate valid! Vaccine: {}".format(vaccineBrand))
            return True
        elif nestedDict['dn'] < nestedDict['sd']:
            #print("Certificate invalid! Too few doses of vaccine")
            #lg.info('Certifikat ni veljaven. Premalo odmerkov cepiva.')
            return False
    elif vaccineBrand == "EU/1/20/1525":
        #print("Certificate valid! Vaccine: {}".format(vaccineBrand))
        return True
 
    
    

def testedCheck(covidListData: str, pcrValid, hagValid)-> bool:
    """
    Funkcija preveri ce je status testiranega se veljaven.
    """
    #print("Performing tested group certificate check...")
    nestedDict = covidListData[0]
    #print("Nested dict: ", nestedDict)

    # Datum in ura odvzema vzorca
    strTestedDate = nestedDict['sc']
    # Iz stringa datuma dobimo realen datum (tip datetime.datetime)
    dateTimeTested = datetime.strptime(strTestedDate, '%Y-%m-%dT%H:%M:%SZ')
    
    # Pridobi rezultat testiranja
    testResult = nestedDict['tr']
    testType = nestedDict['tt']
    if testType == "LP217198-3":
        #print("HAG test ")
        dateTimeValid = dateTimeTested + timedelta(hours=hagValid)
    elif testType == "LP6464-4":
        #print("PCR test ")
        dateTimeValid = dateTimeTested + timedelta(hours=pcrValid)
    todayDate = datetime.today()

    if testResult == "260415000" and todayDate <= dateTimeValid:
        #print("Certificate valid from {} until {}!".format(dateTimeTested,dateTimeValid))
        #lg.info('Certifikat veljaven. (TEST)')
        return True
    else:
        #print("Certificate invalid!")
        #lg.warning('Certifikat ni veljaven. (TEST)')
        return False


def identificationData(covidDict: str)->str:
    """
    Funkcija, ki v JSON dokumentu poisce ime, priimek in datum rojstva in jih vrne.
    """
    if '-260' in covidDict:
        if '1' in covidDict['-260']:
            name = covidDict['-260']['1']['nam']['gnt']
            surname = covidDict['-260']['1']['nam']['fnt']
            birthday=covidDict['-260']['1']['dob']
            #print("Identity: {} {}: {}".format(name, surname, birthday))
            return name, surname, birthday


def makeIdentityList(covidDict: str)->str:
    """
    Funkcija sprejme slovar JSON podatkov in naredi listo vseh imen, ki jih ima oseba.
    Vrne skupno listo vseh imen in priimkov
    """

    # Pridobimo imena, priimke in rojstni datum osebe
    name, surname, birthday = identificationData(covidDict)
    # V primeru vec imen jih razbijemo na posamezne odseke in shranimo v listo
    namesList = name.split("<")
    # V primeru vec priimkov jih razbijemo na posamezne odseke in shranimo v listo
    surnameList = surname.split("<")
    # Lista z vsemi imeni in priimiki osebe
    idList = namesList + surnameList
    # Pridobi zadnji dve letnici
    yy = birthday[2:4]
    # Pridobi mesec rojstva
    mm = birthday[5:7]
    # Pridovi dan rojstva
    dd = birthday[8:10]
    # Naredi datum rojstva, kot je v drugi vrstici osebne
    birthday = yy+mm+dd

    #print(idList, birthday)

    return idList, birthday


def identityCheck(namesFromQR: str, birthdayFromQR: str, namesLineID:str, birthdayLineID: str )-> bool:
    """

    Funkcija sprejeme:
    - imena in priimke iz QR kode (argument namesFromQR => spremenljivka 'names' iz funkcije qrValidityCheck)
    - rojstni datum iz QR kode (argument birthdayFromQR => spremenljivka 'birthday' iz funkcije qrValidityCheck) 
    - string z vrsico imen in priimkov na osebni (argument namesLineID => spremenljivka 'name' iz funkcije string_processor(data))
    - string z vrstico z datumom rojstva na osebni (argument birthdayLineID => spremenljivka 'birth_date' iz funkcije string_processor(data))

    Funkcija Vrne True, ce se identiteti iz QR kode in osebne izkaznice ujemata
    """
    resNames = [ele for ele in namesFromQR if(ele in namesLineID)]
    # Ce se dolzini obeh list ujemata, pomeni, da se imena ujemajo
    if (len(resNames) == len(namesFromQR)) and (birthdayFromQR in birthdayLineID):
        #lg.info(f'Identiteta potrjena.')
        #print("Identiteta potrjena: {} : {}, datum rojstva: {}".format(namesFromQR, resNames, birthdayFromQR))
        #lg.info(f'NEUSTREZNO - covid QR: {covidValidity} id status: {idValidity}')
        identity = True
    else:
        if len(resNames) != len(namesFromQR):
            #lg.warning(f'Identiteta ni ustrezna - napacno ime oz. priimek: QR: {namesFromQR} | ID:{resNames}')
            print("Identiteta ni ustrezna. Napacno ime oz. priimek.")
        elif not (birthdayFromQR in birthdayLineID):
            #lg.warning(f'Identiteta ni ustrezna - rojstna datuma se ne ujemata: QR: {birthdayFromQR} | ID:{birthdayLineID}')
            print("Identiteta ni ustrezna - rojstna datuma se ne ujemata.")
        identity = False

    return identity

    

def checkCustomValidity(covidDict):
    strTestedDate = covidDict['Date created']
    strValidUntil = covidDict['Valid until']
    todayDateTime = datetime.today()

    dateTimeTested = datetime.strptime(strTestedDate, '%Y-%m-%dT%H:%M:%SZ')
    dateTimeValid = datetime.strptime(strValidUntil, '%Y-%m-%dT%H:%M:%SZ')
    if (todayDateTime > dateTimeTested) and (todayDateTime < dateTimeValid):
        validity = True
    else:
        validity = False
    return validity