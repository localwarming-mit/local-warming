import GlobalSettings
import cv2
import cv

if GlobalSettings.capvideo:
    cap = cv2.VideoCapture(-1)
else:
    cap = cv2.VideoCapture("/home/nd/Downloads/video.avi")

if not cap.isOpened():
    print "AHH NOT OPEN"
else:
    print "OPEN!"

if GlobalSettings.cappi:
    import picamera

    class RaspiCap:
        def __init__(self):
            stream = self.stream = io.BytesIO()
            camera = self.camera = picamera.PiCamera()
            camera.resolution = (320, 240)
            camera.framerate = 20
            #camera.start_preview()
            time.sleep(2)
            camera.capture(stream, format='bmp')
        def retrieve(self):
            # Construct a numpy array from the stream
            data = numpy.fromstring(self.stream.getvalue(), dtype=numpy.uint8)
            # "Decode" the image from the array, preserving colour
            image = cv2.imdecode(data, 1)
            #image = None
            return 1, image

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
