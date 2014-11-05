import cv2
import numpy
from GlobalSettings import FilterWindowName, imdebug

#point in quad
def PointInQuad(m,l):
    #is the point outside the quad?
    if (m<0 or m>1 or l<0 or l>1):
        return True
    return False

#Test 1
##CompositeShow("Camera 1", cam1, settings)
##def mouseback_rect(event,x,y,flags,param):
##    if event==cv.CV_EVENT_LBUTTONUP:		# here event is left mouse button double-clicked
##        new = cam1.FrameCorrect(x,y)
##        print x,y, "->", new
##
##
##
##cv.SetMouseCallback("Camera 1", mouseback_rect);
##cv.WaitKey()

#cv.NamedWindow("Image window", 1)

def nothing(da):
    pass

tracks = {}

def setupGUI(tag, min_default=128, max_default=128):
    global FilterWindowName
    if imdebug:
        cv2.namedWindow(FilterWindowName+tag, 2)
        cv2.createTrackbar(tag+" Min", FilterWindowName+tag, min_default, 255, nothing)
        cv2.createTrackbar(tag+" Max", FilterWindowName+tag, max_default, 255, nothing)
    else:
        tracks[tag+" Min"] = min_default
        tracks[tag+" Max"] = max_default


def ErodeTrick(im):
    kernel = numpy.ones((10,10),numpy.uint8)
    im = cv2.erode(im, kernel, iterations=2)
    im = cv2.dilate(im, kernel, iterations = 2)

    #kernel = numpy.ones((10,10),numpy.uint8)
    #im = cv2.erode(im, kernel, iterations=2)
    #im = cv2.dilate(im, kernel, iterations = 2)

    #cv2.dilate(im, im, None, 3)
    #cv2.erode(im, im, None, 3)
    return im


def getTrack(name, window):
    if imdebug:
        high_bnd = cv2.getTrackbarPos(name, window)
        low_bnd = cv2.getTrackbarPos(name, window)
    else:
        high_bnd = tracks[name+" Max"]
        low_bnd = tracks[name+" Min"]
    return high_bnd, low_bnd
