pirdetect v0.1
PIR Record - Record video to the cloud when motion is detected.

<h1>Bill of Materials</h1>
What you need to build this demo:
<ol>
<li>Raspberry Pi 3</li>
<li>Pi Camera</li>
<li>PIR Motion Sensor</li>
<li>Breadboard</li>
<li>Green and Red LEDs</li>
<li>2x 200k Ohm Resistors</li>


<h1>Software Setup</h1>
Clone the repo locally:
1. <code>git clone https://github.com/dixonaws/pirdetect</code>

Setup the environment and install required modules:
1. <code>virtualenv -p python3 pirdetect</code>
2. <code>source pirdetect/bin/activate</code>
3. <code>cd pirdetect; pip3 install -r requirements.txt</code>

Run pir_record:
1. python3 pir_record.py3

pir_record records video from the prior 20 seconds when motion is detected by the PIR (passive infrared sensor) and uploads it to AWS S3.

Details:
The green LED wired to BOARD PIN 12 lights when 
the system is "armed" and ready to record. When the PIR sensor 
wired to BOARD PIN 11 detects motion, the red LED is lit (BOARD PIN 40) 
and the Pi Camera saves the last 20 seconds and further records the 
following 20 seconds of video in h.264 format to a timestamped 
file on the local filesystem. The program then uploads the file to 
an S3 bucket called piphotorecognition (variable: bucket_name) and 
deletes the local file. 

In order to upload to S3, you must have configured your AWS credentials
on the local machine.


