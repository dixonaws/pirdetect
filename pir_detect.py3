import RPi.GPIO as GPIO
import os
import time
import io
import picamera
import logging
import socketserver
from threading import Condition
from http import server
import datetime as dt
import boto3
import os

GPIO.setwarnings(True)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(11, GPIO.IN)
GPIO.setup(40, GPIO.OUT)

# classes for camera streaming
PAGE="""\
<html>
<head>
<title>picamera MJPEG streaming demo</title>
</head>
<body>
<h1>PiCamera MJPEG Streaming Demo</h1>
<img src="stream.mjpg" width="640" height="480" />
<img src="videostill.jpg" width="640" height="480" />
</body>
</html>
"""

class StreamingOutput(object):
    def __init__(self):
        self.frame = None
        self.buffer = io.BytesIO()
        self.condition = Condition()

    def write(self, buf):
        if buf.startswith(b'\xff\xd8'):
            # New frame, copy the existing buffer's content and notify all
            # clients it's available
            self.buffer.truncate()
            with self.condition:
                self.frame = self.buffer.getvalue()
                self.condition.notify_all()
            self.buffer.seek(0)
        return self.buffer.write(buf)

class StreamingHandler(server.BaseHTTPRequestHandler):
    def LEDon(intPIN):
        GPIO.output(intPIN, GPIO.HIGH)

    def LEDoff(intPIN):
        GPIO.output(intPIN, GPIO.LOW)

    def do_GET(self):
        if self.path == '/':
            self.send_response(301)
            self.send_header('Location', '/index.html')
            self.end_headers()
        elif self.path == '/index.html':
            content = PAGE.encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', len(content))
            self.end_headers()
            self.wfile.write(content)
        elif self.path == '/stream.mjpg':
            self.send_response(200)
            self.send_header('Age', 0)
            self.send_header('Cache-Control', 'no-cache, private')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
            self.end_headers()
            try:
                while True:
                    with output.condition:
                        output.condition.wait()
                        frame = output.frame
                    self.wfile.write(b'--FRAME\r\n')
                    self.send_header('Content-Type', 'image/jpeg')
                    self.send_header('Content-Length', len(frame))
                    self.end_headers()
                    self.wfile.write(frame)
                    self.wfile.write(b'\r\n')

                    # detect motion by polling GPIO pin 11
                    i = GPIO.input(11)
                    if i == 0:
                        # send a signl to turn off the red LED
                        GPIO.output(40, 0)
                        time.sleep(0.01)
                    elif i == 1:
                        print("Motion detected")
                        GPIO.output(40, 1)
                        time.sleep(0.01)

            except Exception as e:
                logging.warning(
                    'Removed streaming client %s: %s',
                    self.client_address, str(e))
        else:
            self.send_error(404)
            self.end_headers()

class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
    allow_reuse_address = True
    daemon_threads = True

# instantiate an S3 object so that we can upload files
s3 = boto3.client('s3')

# our S3 bucket name
bucket_name = 'piphotorecognition'

with picamera.PiCamera(resolution='800x600', framerate=30) as camera:
    print("Visit http://172.20.10.102:8000 to see live video from piCamera.")
    output = StreamingOutput()
    camera.start_recording(output, format='mjpeg')
    timestamp = dt.datetime.now().strftime('%m-%d-%Y-%H:%M:%S')

    videostillfilename = 'videostill_' + timestamp + '.jpg'
    #camera.capture(videostillfilename, use_video_port=True)
    #print('Captured image: ' + videostillfilename)

    camera.wait_recording(5)

    try:
        address = ('', 8000)
        server = StreamingServer(address, StreamingHandler)
        server.serve_forever()

    finally:
        camera.stop_recording()

