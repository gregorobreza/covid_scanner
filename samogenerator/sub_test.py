import subprocess
import os
import time


p = subprocess.Popen("/home/pi/covid/pct/app/tesseract_subprocess.py", stdout=subprocess.PIPE)
os.set_blocking(p.stdout.fileno(), False)

while True:
    line = p.stdout.readline().decode("utf-8")
    if line == "":
        pass
    else:
        print(line)
    #time.sleep(0.5)




