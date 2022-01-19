#!/home/pi/pct_scan/env/pct/bin/python3
import yaml

pathConfig = "/home/pi/pct_scan/"

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
#vezane na organizacijo
vrsta_potrditve = data_org["vrsta_potrditve"]
organizacija_test = data_org["organizacija_test"]
organizacija_staff = data_org["organizacija_staff"]
ocr_algorythm = data_org["ocr_algorythm"]
cas_zazanavanja = data_org["cas_zazanavanja"]
osvetlitev = data_org["osvetlitev"]