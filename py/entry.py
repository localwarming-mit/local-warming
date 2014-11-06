import cv2, cv
import time

from camera import Camera, NeedsToSave, cam1
from HumanTracker import HumanTracker
from markers import CalibrationMarker
from utils import PointInQuad, setupGUI, ErodeTrick
import GlobalSettings
from GlobalSettings import FilterWindowName
from viz import CompositeShow
from tracking import PickBlob, FindBall
from capture import GetCaptureDevice

from scipy.signal import convolve2d
import numpy
#import motioncontrol

current_milli_time = lambda: round(time.time() * 1000)

cap = GetCaptureDevice()

calibCap = cap
fgbg = cv2.BackgroundSubtractorMOG2(200, 30, True) #(10, 5, 0.001, 0.1)

def Ball(cv_image):
    filtered = FindBall(cv_image)
    flt2 = ErodeTrick(filtered)
    ret, flt2 = cv2.threshold(flt2, 225, 255, cv2.THRESH_BINARY)

    if GlobalSettings.imdebug:
        cv2.imshow(FilterWindowName+" filtered", flt2)

    mcs = PickBlob(flt2)
    #im = cv2.cvtColor(im, cv.CV_BGR2RGB)
    return mcs

def BgSub(cv_image):
    filtered = fgbg.apply(cv_image)
    flt2 = ErodeTrick(filtered)
    ret, flt2 = cv2.threshold(flt2, 225, 255, cv2.THRESH_BINARY)
    if GlobalSettings.imdebug:
        cv2.imshow(FilterWindowName+" filtered", flt2)

    mcs = PickBlob(flt2)
    #print "MCS SIZE: ", str(len(mcs))
    ht.update(mcs)
    #cv_image = ht.drawFirstEight(cv_image)
    mcs  = ht.getConfidentPts()
    return mcs

def variance(im, mean):
    windowSize = 5
    begin = windowSize /2
    output = mean.copy()
    for r in range(2, im.shape[0]-2):
        for c in range(2, im.shape[1] - 2):
            var = 0.0
            # at pixel r, c - look in window size
            for i in range(-begin, begin+1):
                for j in range(-begin, begin+1):
                    tmp =  float(im[r+i, c+j]) - float(mean[r+i, c+j])
                    var = var + tmp*tmp
            var = var / float(windowSize*windowSize)
            output[r,c] = int(var)
    print "Min: ", output.min(), " and max: ", output.max()

    return output

def variance2(im, mean):
    imf = im.astype(numpy.float32)

    meanf = mean.astype(numpy.float32)

    imfsq = imf*imf

    meanfsq = meanf*meanf

    kernel = numpy.ones((5,5))

    imsqadd = convolve2d(imfsq, kernel, 'same')
    imadd = convolve2d(imf, kernel, 'same')

    out = imsqadd-2*meanf*imadd+25.0*meanfsq
    out = out / 25.0
    out = out.astype(numpy.int8)
    print "Min: ", out.min(), " and max: ", out.max()
    return out


def Motion(cv_image):
    #turn in to hsv
    #hsv = cv2.cvtColor(cv_image, cv.CV_RGB2HSV)
    #[h, s, v] = cv2.split(hsv)

    hsv = cv2.cvtColor(cv_image, cv.CV_RGB2GRAY)
    grey = cv2.boxFilter(hsv, -1, (5, 5))
    gg = variance2(hsv, grey)
    cv2.imshow("gry", gg)
    #cv2.imshow("hue", h)
    #cv2.imshow("sat", s)
    #cv2.imshow("val", v)
    #find most stable image
    #look at frame differences
    #calculate entropy image
    return []

methods = {
    "bgsub": BgSub,
    "balltrack": Ball,
    "motion": Motion
}

methodChoice = "motion"

curMethod = methods[methodChoice]

ShouldWriteOutput = False
if ShouldWriteOutput:
    outf = cv2.VideoWriter("/home/nd/out.avi", cv2.cv.CV_FOURCC(*'XVID'), 20, (640, 480))

ht = HumanTracker()
def image_call():
    global FilterWindowName, curMethod
    ret, cv_image = cap.read()
    if(ret):
        mcs = curMethod(cv_image)
        if GlobalSettings.imdebug:
            save = CompositeShow("Image window", cam1, cv_image, mcs)
            #print "SHAPE: ", str(save.shape)
            if ShouldWriteOutput:
                outf.write(save)

        #motioncontrol.control(mc[0], mc[1])

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
    elif ShouldWriteOutput:
        outf.release()

#set up with sane defaults
setupGUI("Hue", 115, 128)
setupGUI("Value", 218, 255)
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
