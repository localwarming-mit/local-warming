import cv
import cv2
import time
import picamera
import picamera.array
import numpy
#from fractions import Fraction
from utils import ErodeTrick
from tracking import PickBlob
from HumanTracker import HumanTracker
from TCP import TCP
import motioncontrol as motioncontrol
#from motioncontrol import tracking

CAMERA_WIDTH  = 320
CAMERA_HEIGHT = 240

fgbg = cv2.BackgroundSubtractorMOG(200, 30, 0.001, 0.1)
ht = HumanTracker()

tcp = TCP()
#initiate I2C communication between pi and pwm driver
motioncontrol.setup()

# background subtraction method which is no longer used but potentially could be revived
def BgSub(cv_image):
    filtered = fgbg.apply(cv_image)
    flt2 = ErodeTrick(filtered)
    ret, flt2 = cv2.threshold(flt2, 225, 255, cv2.THRESH_BINARY)

    mcs = PickBlob(flt2)
    #print "MCS SIZE: ", str(len(mcs))
    ht.update(mcs)
    cv_image = ht.drawFirstEight(cv_image)
    mcs  = ht.getConfidentPts()
    return filtered #cv_image 
    #return mcs

# This is the current motion tracking method, which uses a simple threshold to
# determine a coordinate to track, if any
def test(cv_image):
        #create camera blind spot to avoid blob detection in non-tracking portion of canera field  
        rect = cv2.rectangle(cv_image,(200,0),(320,240),cv.Scalar(255,255,255),-1)
        #cv.FillPoly(cv.fromarray(cv_image),[(0,0),(160,0),(160,240),(0,240)],cv.Scalar(255,255,255))
        #cv2.imshow('frame',cv_image)
	gry = cv2.cvtColor(cv_image,cv.CV_RGB2GRAY)

	gryi = 255-gry

	ret,thr = cv2.threshold(gryi,215,255,cv2.THRESH_BINARY)

	# erode trick reduces blob size and then re-expands in order to eliminate smaller blobs
	err = ErodeTrick(thr)

	#cv2.imshow('frame',thr)
	#call the function that picks the biggest blob
	mcs = PickBlob(err)

	#return err
	return mcs

#cv2.namedWindow('frame')

#cap = cv2.VideoCapture("/home/pi/vid.h264")
#while(True):
#	ret, cv_image = cap.read()
#	mcs = test(cv_image)
#	for mc in mcs:
#		print mc
#	cv2.imshow('frame',cv_image)
#	cv2.waitKey(1)


with picamera.PiCamera() as camera:
   with picamera.array.PiRGBArray(camera) as stream:
       camera.resolution = (CAMERA_WIDTH, CAMERA_HEIGHT)
       #camera.framerate = Fraction(1, 6)
       #camera.shutter_speed = 600000
       #camera.exposure_mode = 'off'
       #camera.iso = 800
       
       #this while loop is the 'meat' of the code which continuously 
       #runs object tracking (called 'test') and motion control
       while(True):
           camera.capture(stream, 'bgr', use_video_port=True)
           #cv2.imshow('frame', stream.array)
		
	   #set default coordinates to 352,264 since when divided by 320 and 240
	   #the normalized x,y values will be 1.1,1.1 and thus will not be
	   #processed by the motion control function if test does not find a point
	   
	   (x,y) = (352,264)

	   # calls the function which determines a coordinate (if any) or a tracked object
	   x,y = test(stream.array)
	   x = x/320.0
	   y = y/240.0
	   
	   print x,y
	   #tcp = TCP()
	   (x2,y2) = tcp.server()
	   #send the coordinate(s) to motion control for tracking. If coordinate is 1.1,1.1
	   #the motion control function will default to setting all bulbs to 90 degrees and off
	   motioncontrol.tracking([(x,y),(x2,y2)])
	   	
           #cv2.imshow('frame',stream.array)
           
           #this bit of code is needed in order to be able to capture the next image
           #not sure exactly what it does
           if cv2.waitKey(1) & 0xFF == ord('q'):
               break
           stream.seek(0)
           stream.truncate()

#       cv2.destroyAllWindows()

