import cv2
from GlobalSettings import FilterWindowName
from camera import Camera
from capture import GetCaptureDevice
from utils import ErodeTrick

cap = GetCaptureDevice()
fgbg = cv2.BackgroundSubtractorMOG(10, 5, 0.001, 0.1)

def BgSub(cv_image):
    filtered = fgbg.apply(cv_image)
    #flt2 = ErodeTrick(filtered)
    #ret, flt2 = cv2.threshold(flt2, 225, 255, cv2.THRESH_BINARY)
    #cv2.imshow(FilterWindowName, flt2)
    cv2.imshow(FilterWindowName, filtered)

    #mcs = PickBlob(flt2)
    #print "MCS SIZE: ", str(len(mcs))
    #ht.update(mcs)
    #cv_image = ht.drawFirstEight(cv_image)
    #mcs  = ht.getConfidentPts()
    #return mcs

def image_call():
    global FilterWindowName
    ret, cv_image = cap.retrieve()
    if(ret):
        print(".")
        #BgSub(cv_image)
        cv2.imshow(FilterWindowName, cv_image)
        cv2.waitKey(1)


cv2.namedWindow(FilterWindowName, 1)
while(True):
    image_call()
cv2.DestroyAllWindows()
