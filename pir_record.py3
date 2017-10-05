import io
import random
import picamera
import datetime as dt
import boto3

import RPi.GPIO as GPIO
import os
import time
import logging
import boto3
import os

GPIO.setwarnings(True)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(11, GPIO.IN) # PIR motion sensor
GPIO.setup(40, GPIO.OUT) # red LED
GPIO.setup(12, GPIO.OUT) # green LED


def upload_to_s3(bucket_name, filename):
    # s3 upload_file() function takes filename, bucket, key
    key=filename
    s3.upload_file(filename, bucket_name, key)

# setup the ring buffer to hold 20 seconds of video
camera=picamera.PiCamera()
stream=picamera.PiCameraCircularIO(camera,seconds=20)
camera.start_recording(stream,format='h264')

# instantiate an S3 object so we can upload files
s3=boto3.client('s3')

# our S3 bucket name
bucket_name='piphotorecognition'

try:
    while True:
        camera.wait_recording(1)

        i = GPIO.input(11)
        if i == 0:
            # send a signl to turn off the red LED
            GPIO.output(40, 0)

            # send a signal to turn on the green LED
            GPIO.output(12, 1)
            time.sleep(0.01)

        elif i == 1:
            print("Motion detected")

            # send a signl to turn on the red LED
            GPIO.output(40, 1)
            print("motion detected, recording following 10 seconds")
            camera.wait_recording(10)

            timestamp = dt.datetime.now().strftime('%m-%d-%Y-%H_%M_%S')
            videofilename = 'video_' + timestamp + '.h264'

            stream.copy_to(videofilename)
            print("saved temporary file: " + videofilename)
            upload_to_s3(bucket_name,videofilename)
            print("uploaded '" + videofilename + "' to s3")
            os.remove(videofilename)
            print("deleted temporary file: " + videofilename)

            time.sleep(0.01)

except KeyboardInterrupt:
    # turn off the LEDs if we get ctrl+c
    GPIO.output(40,0)
    GPIO.output(12,0)

finally:
    camera.stop_recording()


