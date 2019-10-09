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
fgbg = cv2.BackgroundSubtractorMOG()

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

def variance3(im, mean):
    windowSize = 5
    begin = windowSize /2
    output = mean.copy()
    for r in range(2, im.shape[0]-2):
        for c in range(2, im.shape[1] - 2):
            var = 0.0
            # at pixel r, c - look in window size
            for i in range(-begin, begin+1):
                for j in range(-begin, begin+1):
                    tmp =  float(im[r+i, c+j]) - float(mean[r, c])
                    var = var + tmp*tmp
            var = var / float(windowSize*windowSize)
            output[r,c] = int(var)
    print "Min: ", output.min(), " and max: ", output.max()

    return output

def variance1(im, mean):
    windowSize = 5
    begin = windowSize /2

    output1 = im.astype(numpy.float32)
    output2 = mean.astype(numpy.float32)
    for r in range(2, im.shape[0]-2):
        for c in range(2, im.shape[1] - 2):
            var = 0.0
            sum1 = 0.0
            sum2 = 0.0
            # at pixel r, c - look in window size
            for i in range(-begin, begin+1):
                for j in range(-begin, begin+1):
                    sum1 = sum1 + float(im[r+i,c+j])*float(im[r+i,c+j])
                    sum2 = sum2 + float(mean[r+i, c+j])*float(mean[r+i,c+j])
            output1[r,c] = sum1
            output2[r,c] = sum2
    print "Min: ", output1.min(), " and max: ", output1.max()
    print "Min: ", output2.min(), " and max: ", output2.max()


    return output1


def variance2(im, mean):
    imf = im.astype(numpy.float32)
    print "im-Min: ", imf.min(), " and max: ", imf.max()

    meanf = mean.astype(numpy.float32)
    print "mu-Min: ", meanf.min(), " and max: ", meanf.max()

    imfsq = imf*imf
    print "imsq-Min: ", imfsq.min(), " and max: ", imfsq.max()

    meanfsq = meanf*meanf
    print "musq-Min: ", meanfsq.min(), " and max: ", meanfsq.max()


    kernel = numpy.ones((5,5))

    imsqadd = convolve2d(imfsq, kernel, 'same')
    imadd = convolve2d(imf, kernel, 'same')
    print "cnv-imsq-Min: ", imsqadd.min(), " and max: ", imsqadd.max()
    print "cnv-im-Min: ", imadd.min(), " and max: ", imadd.max()

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
    gg = variance3(hsv, grey)
    cv2.imshow("gry", gg)
    #cv2.imshow("hue", h)
    #cv2.imshow("sat", s)
    #cv2.imshow("val", v)
    #find most stable image
    #look at frame differences
    #calculate entropy image
    return []


def edge(cv_image):
    gry = cv2.cvtColor(cv_image, cv.CV_RGB2GRAY)
    edg = cv2.Sobel(gry, cv.CV_8U, 2,2)
    filt3 = cv2.blur(edg, (3,3))
    ret, flt2 = cv2.threshold(filt3, 10, 255, cv2.THRESH_BINARY)
    flt3 = ErodeTrick(flt2)

    filtered = fgbg.apply(flt3)

    cv2.imshow("edg", filtered)

    return []

prvs = None
def flow(cv_image):
    global prvs
    next = cv2.cvtColor(cv_image,cv2.COLOR_BGR2GRAY)

    if prvs == None:
       prvs = next
    flow = cv2.calcOpticalFlowFarneback(prvs,next, None, 0.5, 3, 15, 3, 5, 1.2, 0)

    mag, ang = cv2.cartToPolar(flow[...,0], flow[...,1])
    hsv[...,0] = ang*180/np.pi/2
    hsv[...,2] = cv2.normalize(mag,None,0,255,cv2.NORM_MINMAX)
    rgb = cv2.cvtColor(hsv,cv2.COLOR_HSV2BGR)
    prvs = next
    cv2.imshow('frame2',rgb)

def test(cv_image):
    gry = cv2.cvtColor(cv_image, cv.CV_RGB2GRAY)
    #gryi = 255 - gry

    #Method 1
    ret, thr = cv2.threshold(gry, 10, 255, cv2.THRESH_BINARY_INV)

    #Method 2
    #thr = cv2.adaptiveThreshold(gryi, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 3, -1.0)

    #Method 3
    #mu = gryi.mean()
    #print "Mu: ", mu
    #ret, thr = cv2.threshold(gry, mu-130, 255, cv2.THRESH_BINARY_INV)

    err = ErodeTrick(thr)



    cv2.imshow("edg", err)
    mcs = PickBlob(err)

    #ht.update(mcs)
    #cv_image = ht.drawFirstEight(cv_image)
    #mcs  = ht.getConfidentPts()


    return mcs


methods = {
    "bgsub": BgSub,
    "balltrack": Ball,
    "motion": Motion,
    "edge": edge,
    "flow": flow,
    "test": test
}

methodChoice = "test"

curMethod = methods[methodChoice]

ShouldWriteOutput = False
if ShouldWriteOutput:
    outf = cv2.VideoWriter("/home/nd/out.mpg", cv2.cv.CV_FOURCC(*'MPEG'), 20, (320, 240))

rect = numpy.asarray( [ [ (0,0), (160, 0), (160, 240), (0, 240) ]] )
ht = HumanTracker()
def image_call():
    global FilterWindowName, curMethod
    ret, cv_image = cap.read()
    if(ret):
        #cv2.rectangle(cv_image,(0,0),(160,240),cv.Scalar(255,255,255))
        cv2.fillPoly(cv_image, rect, cv.Scalar(255,255,255))
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
