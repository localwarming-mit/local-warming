import GlobalSettings
import cv2
import cv
import numpy
import io
import time

if GlobalSettings.capvideo:
    cap = cv2.VideoCapture(-1)
else:
    cap = cv2.VideoCapture("/home/nd/Downloads/out.avi")

if not cap.isOpened():
    print "AHH NOT OPEN"
else:
    print "OPEN!"

if GlobalSettings.cappi:
    import picamera
    import picamera.array

    class RaspiCap:
        def __init__(self):
            camera = self.camera = picamera.PiCamera()
            stream = self.stream = picamera.array.PiRGBArray(camera)
            camera.resolution = (320, 240)
            #camera.framerate = 2
            #camera.shutter_speed = 5000000
            #camera.exposure_mode = 'off'
            #camera.iso = 800
            time.sleep(2)
        def retrieve(self):
            self.camera.capture(self.stream, 'bgr', use_video_port=True)
            self.stream.seek(0)
            self.stream.truncate()
            return 1, self.stream.array

    cap = RaspiCap()
else:
    cap.set(cv.CV_CAP_PROP_FRAME_WIDTH , 320);
    cap.set(cv.CV_CAP_PROP_FRAME_HEIGHT , 240);
    cap.set(cv.CV_CAP_PROP_FPS, 20);
    cap.set(cv.CV_CAP_PROP_FOURCC, cv.CV_FOURCC('R', 'G', 'B', '3'))
    if GlobalSettings.capvideo:
        for i in range(0,20):
            ret, cv_image = cap.retrieve()
            cv.WaitKey(100)


def GetCaptureDevice():
    return cap
