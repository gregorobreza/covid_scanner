import time
try:
    import RPi.GPIO as GPIO
except RuntimeError:
    print("Error importing RPi.GPIO!  This is probably because you need superuser privileges.  You can achieve this by using 'sudo' to run your script")


GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
BUZZER = 12
GPIO.setup(BUZZER, GPIO.OUT)


def validBuzz():
    
    GPIO.output(BUZZER, True)
    time.sleep(0.2)
    GPIO.output(BUZZER, False)
    #time.sleep(halveWaveTime)


def invalidBuzz():
    cycles = 3
    for i in range(0, cycles):
        GPIO.output(BUZZER, True)
        time.sleep(0.3)
        GPIO.output(BUZZER, False)
        time.sleep(0.1)

#validBuzz()
#invalidBuzz()