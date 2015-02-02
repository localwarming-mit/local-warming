LOCAL WARMING SOFTWARE README
------------------------------

INTRODUCTION
-------------

These files control the operation of the Local Warming heating arrays 
and are designed to be run on Raspberry Pi microprocessors running
Debian or similar Linux distributions.

Before running the software, read setup.txt in order to configure the
Raspberry Pi to run the code

FILE DESCRIPTIONS
------------------

GlobalSettings.py - Contains several important settings for the code,
including setting the IP address of the Pi, and choosing whether or
not to stream images from the camera or to run the code using a video file

NewerTest.py - The main program that runs the image processing and calls
the file to run motion control

MotionControl.py - File which takes a coordinate and translates it to
angle and on/off commands sent over I2C to the PWM driver

Timestamp.py - Set of methods for saving timestamps and parsing through timestamps

FUNCTION
---------

In order to run the code, begin by running NewerTest.py
Keep in mind that certain files such as the Adafruit Raspberry Pi files
will need to be in the same directory as NewerTest.py and the rest of the code

When you open NewerTest.py you will first see all of the import statements for the
python libraries as well as our own files and methods which are needed to run the code

You will see the method 'test' which does the image processing using simple thresholding

After this you will see the following:

with picamera.PiCamera() as camera:
with picamera.array.PiRGBArray(camera) as stream:
camera.resolution = (CAMERA_WIDTH, CAMERA_HEIGHT)

      while(True):
            camera.capture(stream, 'bgr', use_video_port=True)
            
            
Everything inside the while loop is essentially the 'meat' of the image processing code.
Here the camera captures an image using the camera.capture method, then processes the image using test,
then sends that coordinate to motioncontrol.py in order to send commands to the pwm driver. The loop runs
continuously so the program must be terminate using ctl-c so be careful when running this code in the background

Also important to know is all of the cv.imshow statements such as this one in the while loop:

 #cv2.imshow('frame',stream.array)
 
 These are used in order to be able to visualize either what the camera is seeing or 
 what the image processing is doing. It can be useful to uncomment these statements
 in order to debug the code. However, this will not work when running the code from 
 the command line since they open a window so it must be done when in the Pi's GUI mode
 
