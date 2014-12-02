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
motioncontrol.setup()

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

def test(cv_image):
        #create camera blind spot to avoid blob detection in non-tracking portion of canera field  
        rect = cv2.rectangle(cv_image,(200,0),(320,240),cv.Scalar(255,255,255),-1)
        #cv.FillPoly(cv.fromarray(cv_image),[(0,0),(160,0),(160,240),(0,240)],cv.Scalar(255,255,255))
        #cv2.imshow('frame',cv_image)
	gry = cv2.cvtColor(cv_image,cv.CV_RGB2GRAY)

	gryi = 255-gry

	ret,thr = cv2.threshold(gryi,215,255,cv2.THRESH_BINARY)

	err = ErodeTrick(thr)

	#cv2.imshow('frame',thr)
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
       while(True):
           camera.capture(stream, 'bgr', use_video_port=True)
           #cv2.imshow('frame', stream.array)
		
	   (x,y) = (352,264)

	   x,y = test(stream.array)
	   x = x/320.0
	   y = y/240.0
	   
	   print x,y
	   #tcp = TCP()
	   (x2,y2) = tcp.server()		
	   motioncontrol.tracking([(x,y),(x2,y2)])
	   	
           #cv2.imshow('frame',stream.array)
           if cv2.waitKey(1) & 0xFF == ord('q'):
               break
           stream.seek(0)
           stream.truncate()

#       cv2.destroyAllWindows()

