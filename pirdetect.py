import RPi.GPIO as GPIO
import os
import time
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(11, GPIO.IN)
GPIO.setup(18, GPIO.OUT)

while True:
    i=GPIO.input(11)
    if i==0:
        print "No motion detected",i
        GPIO.output(18,0)
        os.system("python redLedOff.py")
        time.sleep(0.1)
    elif i==1:
        print "Motion detected",i
        GPIO.output(18,1)
        os.system("python redLedOn.py")
        time.sleep(0.1)