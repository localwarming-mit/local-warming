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

CORE FUNCTIONALITY
-------------------

NEWERTEST.PY
-------------

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
 
MOTIONCONTROL.PY
-----------------

This code can either be used independently of NewerTest.py in order to directly control the bulbs
or can be called within NewerTest.py in order to control the arrays in real time using image processing.
Using the code without NewerTest.py is particularly useful when mechanically calibrating the arrays.

Before running the code, make sure support files like Adafruit_PWM_Servo_Driver and the I2C files are there

When running the code independently, use the main() method to call any of the motion control methods.

Below is a short desctiption of the main methods:

control() - designed to be able to run different functions depending on the timestamp

setup() - sets all of the bulbs to 90 degrees and turns the bulbs off, useful for calibrating

fourtyfive() - sweeps the bulbs in a 45-45 pattern, useful for testing servos

tracking(coords) - takes coordinates and translates them to angle commands

write() - sends on/off and angle commands over I2C to the pwm driver

See the motioncontrol.py file for descriptions of the other minor methods

Before calibrating the motion of the arrays it's important to understand way in which the
coordinate grid is defined.

- The x coordinate is defined as the axis parallel to the array (aka the point along the array)
- The y coordinate is defined as the axis perpendicular to the array (aka the distance from the array)
- The z coodinate is defined as the axis from the bulb vertically. Typical bulb to person distance is 2 meters

This is the way the x,y axis is defined (looking down from above the floor)

 0                                                                                      0               
0 --------------------------------------x axis------------------------------------------ 320    ^
 |                                                                                       |      |
 |                                                                                       |      |
 |                                                                                       |      |
y axis                                                                                   |    y offset
 |                                                                                       |      |
 |                                                                                       |      |
 |****************************************************************************************      |
 |              *              *              *              *             *             |      |             
 |    bulb 6    *    bulb 5    *    bulb 4    *    bulb 3    *    bulb 2   *    bulb 1 CAMERA   v
 |              *              *              *              *             *             |       
 |***************************************************************************************|
 |                                                                                       |
 |                                                                                       |
 |<-------------------------------------x offset---------------------------------------->|
 |                                                                                       |
 |                                                                                       |
 |                                                                                       |
 240-------------------------------------------------------------------------------------320
  0                                                                                     240
  
Note: The x and y axis are normalized before being sent to the motioncontrol code, such that
both axis' default to a maximum coordinate of 1.0. Thus a coordinate of 1.1 can be sent 
as a 'dummy' to indicate the no coordinate has been detected by motion tracking

This is the way the y angle is calculated (looking from the side of the array)
       ___
      | O |
      |   | <- bulb
  ____|   |____
 |_____________|
  ^     |\
  |     | \
  |     |_/\
  |     |(theta)   
  |     |    \
  |     |     \             height is defined as the distance from the bulb to the average person's chest
  |     |      \                                          (typically 2.0 meters)
height  |       \
  |     |        \
  |     |         \                                   theta = arctan(ydistance/height)
  |     |          \
  |     |           \    ____          this angle is either added or subtracted to the default (90 degrees)
  |     |            \  /    \        in order to give an angle command between 45 and 135 degrees (90 +/- 45) 
  |     |             \ \    /
  v     |__y distance__\ \__/
        90       \_______/  \_______/
                         |  |
                         |  |
                         |__|
                         /  \
                        /    \
                        |    |       
                      __|    |__
                      

Using these definitions for the coodinate grid, the motion control code first determines an x coordinate simply by
dividing the x axis into six sections corresponding to the six bulbs to find which bulb(s) must be actuated. Then,
the angle for the given bulb is calculated using the y position and finding the angle with the arctan function above.
