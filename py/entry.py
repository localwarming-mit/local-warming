import cv2
import time

from camera import Camera
from calibration import NeedsToSave, cam1
from HumanTracker import HumanTracker
from markers import CalibrationMarker
from utils import PointInQuad, setupGUI, ErodeTrick
import GlobalSettings
from GlobalSettings import FilterWindowName
from viz import CompositeShow
from tracking import PickBlob, FindBall
from capture import GetCaptureDevice
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

methods = {
    "bgsub": BgSub,
    "balltrack": Ball
}

methodChoice = "bgsub"

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
