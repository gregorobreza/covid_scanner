#!/home/pi/pct_scan/env/pct/bin/python3

import RPi.GPIO as GPIO
import time
import argparse


GPIO.setmode(GPIO.BCM) # GPIO Numbers instead of board numbers
 
RELAIS_1_GPIO = 5
GPIO.setup(RELAIS_1_GPIO, GPIO.OUT) # GPIO Assign mode

def switch_reley(t, gpio):
    #GPIO.output(RELAIS_1_GPIO, GPIO.LOW)
    RELAIS_1_GPIO = gpio
    GPIO.output(RELAIS_1_GPIO, GPIO.HIGH)
    time.sleep(t)
    GPIO.output(RELAIS_1_GPIO, GPIO.LOW)
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    requiredNamed = parser.add_argument_group('required named arguments')
    requiredNamed.add_argument("-t", "--time", help="define time delay of relay", type=float, required=True)
    parser.add_argument("-p", "--pin", help="GPIO! pin number default 5", type=int, default=5)
    args = parser.parse_args()
    delay_time=args.time
    gpio_pin=args.pin
    switch_reley(delay_time, gpio_pin)
    GPIO.cleanup() 
