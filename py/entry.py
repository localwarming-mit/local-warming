import cv
import cv2
import numpy
import numpy.linalg
import math
import socket
import sys
import os.path
import io
import time

from camera import Camera
from calibration import NeedsToSave, cam1
from HumanTracker import HumanTracker
from markers import CalibrationMarker
from utils import PointInQuad, setupGUI
import GlobalSettings
from GlobalSettings import FilterWindowName
from viz import CompositeShow
#import picamera
#import motioncontrol

current_milli_time = lambda: round(time.time() * 1000)








def FindBall(im2):
    global FilterWindowName
    hsv = cv2.cvtColor(im2, cv.CV_RGB2HSV)
    [h, s, v] = cv2.split(hsv)

    #---------------------
    high_bnd = cv2.getTrackbarPos("Hue Max", FilterWindowName+"Hue")
    low_bnd = cv2.getTrackbarPos("Hue Min", FilterWindowName+"Hue")

    ret, hi1 = cv2.threshold(h, high_bnd, 255, cv2.THRESH_BINARY_INV)
    ret, hi2 = cv2.threshold(h, low_bnd, 255, cv2.THRESH_BINARY)

    hi = cv2.bitwise_and(hi1, hi2)
    cv2.imshow(FilterWindowName+"Hue", hi);
    #---------------------
    high_bnd = cv2.getTrackbarPos("Value Max", FilterWindowName+"Value")
    low_bnd = cv2.getTrackbarPos("Value Min", FilterWindowName+"Value")

    ret, vi1 = cv2.threshold(v, high_bnd, 255, cv2.THRESH_BINARY_INV)
    ret, vi2 = cv2.threshold(v, low_bnd, 255, cv2.THRESH_BINARY)

    vi = cv2.bitwise_and(vi1, vi2)
    cv2.imshow(FilterWindowName+"Value", vi);
    #---------------------
    out = cv2.bitwise_and(vi, hi)


    return out

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

cntrs = None
hier = None
def PickBlob(im):
    global cntrs, hier
    [conts, hier] = cv2.findContours(im, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    high_bnd = cv2.getTrackbarPos(" Max", FilterWindowName)
    low_bnd = cv2.getTrackbarPos(" Min", FilterWindowName)
    cntrs = []
    for cntr in conts:
        ara = cv2.contourArea(cntr)
        if(3000 < ara):
            #print "ara: ", str(ara)
            cntrs.append(cntr)

    centroids = []
    for cntr in cntrs:
        mu = cv2.moments(cntr)
        #print "MU: " + str(mu)
        mx = mu['m10']/mu['m00']
        my = mu['m01']/mu['m00']
        centroids.append( (mx,my) )
    return centroids


cap = cv2.VideoCapture("/home/nd/Downloads/out.avi")
if not cap.isOpened():
    print "AHH NOT OPEN"
else:
    print "OPEN!"
cap.set(cv.CV_CAP_PROP_FRAME_WIDTH , 320);
cap.set(cv.CV_CAP_PROP_FRAME_HEIGHT , 240);
#cap.set(cv.CV_CAP_PROP_FPS, 20);
#cap.set(cv.CV_CAP_PROP_FOURCC, cv.CV_FOURCC('R', 'G', 'B', '3'))

for i in range(0,20):
    ret, cv_image = cap.retrieve()
    cv.WaitKey(100)

class TCPClient:
    def __init__(self, Address, Port):
	self.Address = Address
	self.Port = Port
        self.open_server()

    def open_server(self):
        # Create a TCP/IP socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Connect the socket to the port where the server is listening
        server_address = (self.Address, self.Port)
        print >>sys.stderr, 'connecting to %s port %s' % server_address
        self.sock.connect(server_address)

    def send(self, pts):
        try:
            i = 0
            for pt in pts:
                # the data should be sent as 3 comma separated values with a total length of 19 characters.
                # 1 for id, 8 for x, 8 for y
                # [ i,xxxxxxxx,yyyyyyyy ]
                message = '' + str(i) + ',' + ("%8f" % pt[0]) + ',' + ("%8f" % pt[1])

                # Send data
                sock.sendall(message)
                i = i + 1
                if(i == 10):
                    break
        except:
            pass


#tcpc = TCPClient('localhost', 4558)

#class RaspiCap:
#    def __init__(self):
#        stream = self.stream = io.BytesIO()
#        camera = self.camera = picamera.PiCamera()
#	camera.resolution = (320, 240)
#	camera.framerate = 20
#        #camera.start_preview()
#        time.sleep(2)
#        camera.capture(stream, format='bmp')
#    def retrieve(self):
#        # Construct a numpy array from the stream
#        data = numpy.fromstring(self.stream.getvalue(), dtype=numpy.uint8)
#        # "Decode" the image from the array, preserving colour
#        image = cv2.imdecode(data, 1)
	#image = None
        #return 1, image

#cap = RaspiCap()
calibCap = cap

fgbg = cv2.BackgroundSubtractorMOG2(200, 30, True) #(10, 5, 0.001, 0.1)

outf = cv2.VideoWriter("/home/nd/out.avi", cv2.cv.CV_FOURCC(*'XVID'), 20, (640, 480))

ht = HumanTracker()
def image_call():
    global FilterWindowName, aux_img
    #ret, cv_image = cap.read()
    ret, cv_image = cap.read()
    #cv2.imwrite("/home/nd/blah.jpg", cv_image)
    if(ret):
        #filtered = FindBall(cv_image)
        filtered = fgbg.apply(cv_image)
        flt2 = ErodeTrick(filtered)
        ret, flt2 = cv2.threshold(flt2, 225, 255, cv2.THRESH_BINARY)
        cv2.imshow(FilterWindowName+" filtered", flt2)

        mcs = PickBlob(flt2)
        #print "MCS SIZE: ", str(len(mcs))
        ht.update(mcs)
        #cv_image = ht.drawFirstEight(cv_image)
        mcs  = ht.getConfidentPts()
        #motioncontrol.control(mc[0], mc[1])
        #cv_image = cv2.cvtColor(cv_image, cv.CV_BGR2RGB)
        #cvIm = cv.CreateImageHeader((cv_image.shape[1], cv_image.shape[0]), cv.IPL_DEPTH_8U, 3)
        #cv.SetData(cvIm, cv_image.tostring(),
        #       cv_image.dtype.itemsize * 3 * cv_image.shape[1])
        save = CompositeShow("Image window", cam1, cv_image, mcs)
        #print "SHAPE: ", str(save.shape)
        outf.write(save)
        #correct the frame
        #tosend = []
        #for mc in mcs:
        #    new = cam1.FrameCorrect(mc[0],mc[1])

        #    rectified = unit2world(new)

            #print "Ball: ", str(mc), " -> ", str(new)
        #    print "Ball: ", str(mc), " -> ", str(rectified)
        #    tosend.append(rectified)

        #now send it!
        #tcpc.send(tosend)
        #if cv2.waitKey(3) & 0xFF == ord(' '):
        #    #snap background
        #    print "BACKGROUND"
        #    pass
        cv2.waitKey(3)
    else:
        outf.release()

#set up with sane defaults
#setupGUI("Hue", 115, 128)
#setupGUI("Hue")
#setupGUI("Value", 218, 255)
# setupGUI("Value")
setupGUI("", 218, 1000)

if(NeedsToSave):
    Save("prefs.txt", cameras);

start_time = current_milli_time()
frames = 0

#motioncontrol.setup()

target_fps = 15
last_t = 0
while(True):
    image_call()
    frames = frames + 1
    diff = current_milli_time() - start_time
    if diff > 0:
       print "Frames Per Second: ", str(frames / (float(diff)/1000))
    cur_t = current_milli_time()
    if(cur_t - last_t < 1000 / target_fps):
        time.sleep((1000/target_fps - (cur_t-last_t))/1000)
    last_t = cur_t
    if(NeedsToSave):
        Save("prefs.txt", cameras);
        NeedsToSave = False
cv.DestroyAllWindows()
