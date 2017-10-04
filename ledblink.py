import RPi.GPIO as GPIO
import time
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(21,GPIO.OUT)

while True:
        GPIO.output(21,GPIO.HIGH)
        print("light on")
        time.sleep(1)

        GPIO.output(21,GPIO.LOW)
        print("light off")
        time.sleep(1)

