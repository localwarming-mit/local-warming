import picamera
import picamera.array
import socket
from time import sleep
import numpy as np
import cv2 as cv2
import cv as cv 
import re
import io
import sys

camera = picamera.PiCamera()
camera.start_preview()
sleep(120)

class RaspiCap:
	def __init__(self):
		camera = self.camera = picamera.PiCamera()
		stream = self.stream = picamera.array.PiRGBArray(camera)
		camera.capture(stream,format='bgr')
	def retrieve(self):
		stream = self.stream = picamera.array.PiRGBArray(self.camera)
		self.camera.capture(self.stream,format='bgr')
		image = self.stream.array
		return 1,image

#cap = RaspiCap()

#fgbg = cv2.BackgroundSubtractorMOG()
#fgbg = cv2.imread('image.jpg')
#image = fgbg.array
#cv.NamedWindow('frame')
#cv.ShowImage('frame',fgbg)

#while(1):
	#ret,frame = cap.retrieve()
	#fgmask = fgbg.apply(frame)
	#fgmask2 = cv.fromarray(fgmask)
	#cv.ShowImage('frame',fgbg)
	#k = cv2.waitKey(30) & 0xFF
	#if k == 27:
	#	break

#cap.release()
#cv2.destroyAllWindows()
