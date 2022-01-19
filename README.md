
<h3 align="center">PCT skener na Raspberry Pi 4 - development verzija</h3>

---

<p align="center"> PCT scanner za preverjanje ustreznosti PCT pogoja in generiranje qr kod za prehod znotraj organizacij.
    <br> 
</p>

## 📝 Vsebina

- [O projektu](#o_projektu)
- [Pozor](#pozor)
- [Namestitev](#namestitev)
- [Zahteve](#zahteve)
- [Uporaba](#uporaba)
- [Namestitve](#namestitve)
- [Nastavitev zamodejnega zagona](#samodejni)

## 🧐 O projektu <a name = "o_projektu"></a>

Projekt je bil razvit za namen preverjanja PCT pogoja in oseben izkaznice prvotno na fakulteti za strojništvo. Koda vsebuje tudi program za generiranje zasebnih QR kod za hiter prehod in za študente ki se samotestirajo.

## 🎈 Pozor <a name="pozor"></a>

Koda je ena izmed prvotnih razvojnih verzij zato nekatere datoteke niso uporabljene. 

### Zahteve <a name="Zahteve"></a>

Na RPI je najprej potrebno namestiti OpenCV, in knjižice za delo s Tesseract za prepoznavanje znakov na osebni izkaznici. Na Rpi tudi omogočimo kamere ter SPI komunikacijo za komunikacijo z LED signalom. 

```
#opencv

sudo apt update && sudo apt-get upgrade &&

sudo apt -y install build-essential cmake pkg-config &&


sudo apt -y install libjpeg-dev libtiff5-dev libjasper-dev libpng-dev &&
sudo apt -y install libxvidcore-dev libx264-dev &&

sudo apt -y install libfontconfig1-dev libcairo2-dev &&
sudo apt -y install libgdk-pixbuf2.0-dev libpango1.0-dev &&
sudo apt -y install libgtk2.0-dev libgtk-3-dev &&

sudo apt -y install libatlas-base-dev gfortran &&

sudo apt -y install libhdf5-dev libhdf5-serial-dev libhdf5-103 &&
sudo apt -y install libqtgui4 libqtwebkit4 libqt4-test python3-pyqt5 &&
sudo apt -y install python3-dev

#tesseract

sudo apt -y install tesseract-ocr libtesseract-dev libleptonica-dev pkg-config
```

### Namestive <a name = "namestitve"></a>

Repozitorj se klonira na poljubno mesto, ustvari virtualno okolje, se ga aktivira in namesti ```pip install -r requirements.txt```. Odvisno od željenega programa zaženemo skripto:

```
#za osnovni program za preverjanje
./pct/video-stream.py

#za progrma za generiranje QR kod za organizacije
./samogenerator/sam-gen.py

#za program za geenriranje kod za testiranje
./samotest/makeqr.py
```

Za prilagoditev parametrov se popravljata datoteki ```.yaml```.


## 🔧 Nastavitev zamodejnega zagona <a name = "samodejni"></a>

Za nastavitev samodejnega zagona se lahko posamezno skripto nastavi v RPI autostart torej vnesemo pot do datoteke v:


```
sudo nano /etc/xdg/lxsession/LXDE-pi/autostart
```



