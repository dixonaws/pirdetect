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
import sys

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(11, GPIO.IN) # PIR motion sensor
GPIO.setup(40, GPIO.OUT) # red LED
GPIO.setup(12, GPIO.OUT) # green LED


def upload_to_s3(bucket_name, filename):
    # s3 upload_file() function takes filename, bucket, key
    sys.stdout.write("Uploading to S3... ")
    key=filename
    s3.upload_file(filename, bucket_name, key)
    print("done, '" + videofilename + "' saved to S3 bucket " + bucket_name + ".")

# setup the ring buffer to hold 20 seconds of video
timestamp = dt.datetime.now().strftime('%m-%d-%Y-%H_%M_%S')
print("System armed at " + timestamp)
camera=picamera.PiCamera()
camera.annotate_text=timestamp
camera.annotate_frame_num=True
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
            timestamp = dt.datetime.now().strftime('%m-%d-%Y-%H_%M_%S')
            sys.stdout.write("Motion detected at " + timestamp + ", recording following 20 seconds... ")

            # send a signal to turn on the red LED
            GPIO.output(40, 1)

            # record for 20 seconds
            camera.annotate_text=timestamp
            camera.annotate_frame_num=True
            camera.wait_recording(20)
            print("done.")

            videofilename = 'video_' + timestamp + '.h264'

            sys.stdout.write("Saving temporary file " + videofilename + "... ")
            stream.copy_to(videofilename)
            print("done.")

            upload_to_s3(bucket_name,videofilename)

            sys.stdout.write("Deleting temporary file... ")
            os.remove(videofilename)
            print("done, deleted '" + videofilename + "'")

            time.sleep(0.01)

except KeyboardInterrupt:
    # turn off the LEDs if we get ctrl+c
    GPIO.output(40,0)
    GPIO.output(12,0)

finally:
    camera.stop_recording()


