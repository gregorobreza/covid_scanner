import apa

def ledWhite(brightness):
    numleds = 8
    ledstrip = apa.Apa(numleds)
    for i in range(0, 8):
        ledstrip.led_set(i, brightness, 255,255,255)
    ledstrip.write_leds()


def ledGreen(brightness):
    numleds = 8
    ledstrip = apa.Apa(numleds)
    for i in range(0, 8):
        ledstrip.led_set(i, brightness, 0,255,0)
    ledstrip.write_leds()

def ledRed(brightness):
    numleds = 8
    #blabla
    ledstrip = apa.Apa(numleds)
    for i in range(0, 8):
        ledstrip.led_set(i, brightness, 0,0,255)
    ledstrip.write_leds()

def ledOff():
    numleds = 8
    ledstrip = apa.Apa(numleds)
    ledstrip.reset_leds()
    #ledstrip.flush_leds()