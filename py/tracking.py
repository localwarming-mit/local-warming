import cv
import cv2
from GlobalSettings import FilterWindowName, imdebug
from utils import getTrack

def FindBall(im2):
    global FilterWindowName, imdebug
    hsv = cv2.cvtColor(im2, cv.CV_RGB2HSV)
    [h, s, v] = cv2.split(hsv)

    #---------------------
    high_bnd, low_bnd = getTrack("Hue", FilterWindowName+"Hue")

    ret, hi1 = cv2.threshold(h, high_bnd, 255, cv2.THRESH_BINARY_INV)
    ret, hi2 = cv2.threshold(h, low_bnd, 255, cv2.THRESH_BINARY)

    hi = cv2.bitwise_and(hi1, hi2)
    if imdebug:
        cv2.imshow(FilterWindowName+"Hue", hi);
    #---------------------
    high_bnd, low_bnd = getTrack("Value", FilterWindowName+"Value")

    ret, vi1 = cv2.threshold(v, high_bnd, 255, cv2.THRESH_BINARY_INV)
    ret, vi2 = cv2.threshold(v, low_bnd, 255, cv2.THRESH_BINARY)

    vi = cv2.bitwise_and(vi1, vi2)

    if imdebug:
        cv2.imshow(FilterWindowName+"Value", vi);
    #---------------------
    out = cv2.bitwise_and(vi, hi)


    return out

cntrs = None
hier = None
def PickBlob(im):
    global cntrs, hier
    [conts, hier] = cv2.findContours(im, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

    high_bnd, low_bnd = getTrack("", FilterWindowName)
    cntrs = []
    for cntr in conts:
        ara = cv2.contourArea(cntr)
        if(1000 < ara):
            #print "fnd: ", str(ara)
            cntrs.append(cntr)

    centroids = []
    for cntr in cntrs:
        mu = cv2.moments(cntr)
        #print "MU: " + str(mu)
        mx = mu['m10']/mu['m00']
        my = mu['m01']/mu['m00']
        centroids.append( (mx,my) )
    return centroids
