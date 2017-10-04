import io
import random
import picamera
import datetime as dt
import boto3

def motion_detected():
    return random.randint(0,10)==0

def upload_to_s3(bucket_name, filename):
    # s3 upload_file() function takes filename, bucket, key
    key=filename
    s3.upload_file(filename, bucket_name, key)

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
        if motion_detected():
            print("motion detected, recording following 10 seconds")
            camera.wait_recording(10)

            timestamp = dt.datetime.now().strftime('%m-%d-%Y-%H_%M_%S')
            videofilename = 'video_' + timestamp + '.h264'

            stream.copy_to(videofilename)
            print("saved " + videofilename)
            upload_to_s3(bucket_name,videofilename)
            print("uploaded '" + videofilename + "' to s3")

finally:
    camera.stop_recording()


