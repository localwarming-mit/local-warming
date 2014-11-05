import cv
import cv2
import GlobalSettings
from calibration import Uncalibrated

def CompositeShow(windowName, camera, image, pts=[]):
    global Uncalibrated

    if not GlobalSettings.imdebug:
        return image

    cv2.namedWindow(windowName)
    comp = image.copy() #cv.CloneImage(image)
    if(Uncalibrated):
        CalibrateCameras(comp)
        Uncalibrated = False

    if(GlobalSettings.showGrid):
        #draw lines

        #p1 - p2
        cv2.line(comp, tuple(camera.calibrationmarkers[0].pos), \
                      tuple(camera.calibrationmarkers[1].pos), cv.Scalar(0, 255, 0), 1, cv.CV_AA)

        #p1 - p4
        cv2.line(comp, tuple(camera.calibrationmarkers[0].pos), \
                      tuple(camera.calibrationmarkers[3].pos), cv.Scalar(0, 255, 0), 1, cv.CV_AA)

        #p3 - p4
        cv2.line(comp, tuple(camera.calibrationmarkers[2].pos), \
                      tuple(camera.calibrationmarkers[3].pos), cv.Scalar(0, 255, 0), 1, cv.CV_AA)

        #p2 - p3
        cv2.line(comp, tuple(camera.calibrationmarkers[1].pos), \
                      tuple(camera.calibrationmarkers[2].pos), cv.Scalar(0, 255, 0), 1, cv.CV_AA)

    for pt in pts:
        cv2.circle(comp, (int(pt[0]), int(pt[1])), 10, cv.Scalar(0, 0, 255), thickness=-1)
    cv2.imshow(windowName, comp)
    return cv2.resize(comp, (640, 480))
