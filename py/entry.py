import cv
import cv2
import numpy
import numpy.linalg
import math
import socket
import sys


class CalibrationMarker:
    def __init__(self, UID):
        self.UID = UID
        self.mon = "CALIB"+str(UID)
        self.pos = [0, 0]

    def Save(self, f, prefix):
        stng = prefix+self.mon+"="+str(self.pos)+"\n"
        f.write(stng)

    def Load(self, line, prefix):
        stng = prefix+self.mon
        if(line.startswith(stng)):
            self.pos = eval(line[line.rfind("=")+1:])
            #print "got: "+ line + " ---> " + str(self.pos)
            return True
        return False
        

calibCap = None
def MouseCalibrate(image, markers):
    windowName = "Choose Point";
    cv.NamedWindow(windowName)
    gotPoint = [False]*len(markers);
    ind = [0]
    pt = [0,0]
    def mouseback(event,x,y,flags,param):
        if event==cv.CV_EVENT_LBUTTONUP:		# here event is left mouse button double-clicked
            print x,y
            pt[0] = x
            pt[1] = y
            gotPoint[ind[0]] = True

    cv.SetMouseCallback(windowName, mouseback);
    for i in range(0, len(markers)):
        #redisplay image and title
        cv.ShowImage(windowName, image);
        ind[0] = i
        
        #ask for pt
        while not gotPoint[ind[0]]:
            ret, calibImage = calibCap.retrieve()
            cv2.imshow(windowName, calibImage);
            cv.WaitKey(1);
            
        #add point to matrix
        markers[i].pos = [pt[0], pt[1]];

    cv.DestroyWindow(windowName)

def AutoCalibrate(image):
    pass

def Save(filename, cameras):
    f = open(filename, "w")
    for camera in cameras:
        camera.Save(f)


class Camera:
    pos = [0,0,0];
    cur = None
    def __init__(self, id):
        self.red = CalibrationMarker("RED");
        self.blue = CalibrationMarker("BLUE");
        self.green = CalibrationMarker("GREEN");
        self.yellow = CalibrationMarker("YELLOW");
        
        self.calibrationmarkers = [self.red, self.blue, self.green, self.yellow]

        if(type(id) == type('imastring')):
            self.capture = cv.CaptureFromFile(id);
            id = int(id[-5])
        else: #i'm a numeric id
            self.capture = cv.CaptureFromFile("../cam1.mov")
            #self.capture = cv2.VideoCapture(id);

        self.calibrated = False
        self.id = id;

    def next(self):
        #self.cur = self.capture.retrieve()
        self.cur = None
        return self.cur;
    def Save(self, f, prefix=""):
        for calib in self.calibrationmarkers:
            calib.Save(f, "CAM"+str(self.id))
    
    def Load(self, line, prefix=""):
        iscalib = [calib.Load(line, "CAM"+str(self.id)) for calib in self.calibrationmarkers]
        self.LdCounter += iscalib.count(True)
        self.calibrated = self.calibrated or self.LdCounter == len(self.calibrationmarkers)

    def Calibrate(self, withMouse, imageOverride = None):
        if(imageOverride == None):
            imageOverride = self.cur
        if(withMouse):
            MouseCalibrate(imageOverride, self.calibrationmarkers);
        else:
            AutoCalibrate(imageOverride, self.calibrationmarkers);
        self.CalibrateFunc()
        self.calibrated = True

    def CalibrateFunc(self):
        #for each calibration marker, construct matrix to do least squares with
        numrows = 2*len(self.calibrationmarkers)
        A = numpy.zeros((numrows, 9))
        B = numpy.zeros((numrows, 1))
        # marker 1: 0,0
        # marker 2: 1,0
        # marker 3: 1,1
        # marker 4: 0,1
        #B(0),B(1) = 0   #marker 1
        B[2] = 1; B[5]=1 #marker 2,3
        B[4] = 1;
        B[6] = 0; B[7]=1 
        #B[3] = 1; B[4]=1 #marker 2,3
        #B[6] = 1; B[7]=1 #marker 4
        
        
        #create our polygon
        self.px = numpy.array([-1, 8, 13, -4])
        self.py = numpy.array([-1, 3, 11, 8])  
        i = 0
        for calib in self.calibrationmarkers:
            self.px[(3+i)%4] = calib.pos[0]
            self.py[(3+i)%4] = -calib.pos[1]
            i = i + 1
        
        
        print "PX: \n", str(self.px)
        print "PY: \n", str(self.py)
        #compute coefficients
        
        #A=numpy.mat('1 0 0 0;1 1 0 0;1 1 1 1;1 0 1 0')
        #print "A: \n", str(A)
        #AI = numpy.invert(A)
        AI = numpy.mat('1 0 0 0;-1 1 0 0;-1 0 0 1;1 -1 1 -1')

        #print "AI: \n", str(AI)
        #print "shapes: ", str(AI.shape), " and ", str(self.px.T.shape)
        self.a = numpy.dot(AI, self.px)
        self.a = numpy.squeeze(self.a)
        print "a: \n", str(self.a)
        self.b = numpy.dot(AI, self.py)
        self.b = numpy.squeeze(self.b)
        print "b: \n", str(self.b)

        #classify points as internal or external
        #plot_internal_and_external_points(px,py,a,b);

        return self.a, self.b
    
    # converts physical (x,y) to logical (l,m)
    def FrameCorrect(self, x, y):
        #quadratic equation coeffs, aa*mm^2+bb*m+cc=0
        #y = 240 - y
        y = -y
        a = self.a
        b = self.b
        aa = a[0,3]*b[0,2] - a[0,2]*b[0,3]
        bb = a[0,3]*b[0,0] -a[0,0]*b[0,3] + a[0,1]*b[0,2] - a[0,2]*b[0,1] + x*b[0,3] - y*a[0,3]
        cc = a[0,1]*b[0,0] -a[0,0]*b[0,1] + x*b[0,1] - y*a[0,1]
        #compute m = (-b+sqrt(b^2-4ac))/(2a)
        det = math.sqrt(bb*bb - 4*aa*cc);
        m = (-bb+det)/(2*aa);
        
        #compute l
        l = (x-a[0,0]-a[0,2]*m)/(a[0,1]+a[0,3]*m)
        return l,m


#point in quad
def PointInQuad(m,l):
    #is the point outside the quad?
    if (m<0 or m>1 or l<0 or l>1):
        return True
    return False

def Load(filename, cameras):
    f = open(filename, "r")
    for camera in cameras:
        camera.LdCounter = 0
    line = f.readline()
    while(len(line) != 0):
        #test line on all cameras
        for camera in cameras:
            camera.Load(line)
        line = f.readline()





def CompositeShow(windowName, camera, image, settings, pts=[]):
    global Uncalibrated
    cv.NamedWindow(windowName)
    comp = cv.CloneImage(image)
    if(Uncalibrated):
        CalibrateCameras(comp)
        Uncalibrated = False
    
    if(settings.showGrid):
        #draw lines

        #p1 - p2
        cv.Line(comp, tuple(camera.calibrationmarkers[0].pos), \
                      tuple(camera.calibrationmarkers[1].pos), cv.Scalar(0, 255, 0), 1, cv.CV_AA)
        
        #p1 - p4
        cv.Line(comp, tuple(camera.calibrationmarkers[0].pos), \
                      tuple(camera.calibrationmarkers[3].pos), cv.Scalar(0, 255, 0), 1, cv.CV_AA)
                
        #p3 - p4
        cv.Line(comp, tuple(camera.calibrationmarkers[2].pos), \
                      tuple(camera.calibrationmarkers[3].pos), cv.Scalar(0, 255, 0), 1, cv.CV_AA)
        
        #p2 - p3
        cv.Line(comp, tuple(camera.calibrationmarkers[1].pos), \
                      tuple(camera.calibrationmarkers[2].pos), cv.Scalar(0, 255, 0), 1, cv.CV_AA)
    
    for pt in pts:
        cv.Circle(comp, (int(pt[0]), int(pt[1])), 3, cv.Scalar(255, 0, 0))
    cv.ShowImage(windowName, comp)


cam1 = Camera(-1);
cam2 = Camera("../cam2.mov");
cam3 = Camera("../cam3.mov");
cam4 = Camera("../cam4.mov");

cameras = [cam1]#,cam2,cam3,cam4]

im1 = cam1.next()
#cv.SaveImage("test.jpg", im1)
#im2 = cam2.next()
#im3 = cam3.next()
#im4 = cam4.next()

Load("prefs.txt", cameras);
ManualCalibrate = True;
#print "calibs: " + str([x.calibrated for x in cameras])
NeedsToSave = False
Uncalibrated = not reduce(lambda a,b: a and b, [x.calibrated for x in cameras])

if(not Uncalibrated):
   [cam.CalibrateFunc() for cam in cameras]
def CalibrateCameras(imageOverRide = None):
    global NeedsToSave, cameras, Uncalibrated
    if(Uncalibrated):
        #recalibrate
        NeedsToSave = True
        Uncalibrated = True
        [cam.Calibrate(ManualCalibrate, imageOverRide) for cam in cameras]


g_a = None
g_b = None

#Calibrate unit->world

#lightblue/pink/green/darkblue
g_px = numpy.array([0.4, 2.3, 4.2, 2.3])
g_py = numpy.array([2.44, 0.4, 2.44, 4.48])
#g_px = numpy.array([2.3,  0.4,  2.3, 4.2])
#g_py = numpy.array([4.48, 2.44, 0.4, 2.44])

#compute coefficients
AI = numpy.mat('1 0 0 0;-1 1 0 0;-1 0 0 1;1 -1 1 -1')


g_a = numpy.dot(AI, g_px)
g_a = numpy.squeeze(g_a)
#print "g_a: \n", str(g_a)
g_b = numpy.dot(AI, g_py)
g_b = numpy.squeeze(g_b)
#print "g_b: \n", str(g_b)


def unit2world(pos):
    g = pos[0]
    h = pos[1]
    k = g*h
    unit = numpy.bmat([[[1], [g], [h], [k]]])
    world_x = numpy.asscalar(numpy.dot(g_a, unit.T))
    world_y = numpy.asscalar(numpy.dot(g_b, unit.T))
    return (world_x, world_y)

#test 
#print "unit2world 0,0: \n", str(unit2world([0,0]))
#print "unit2world 1,0: \n", str(unit2world([1,0]))
#print "unit2world 0 1: \n", str(unit2world([0,1]))
#print "unit2world 1 1: \n", str(unit2world([1,1]))
# 4 different colors, find those, autocalibrate


# -> calib per camera
class Settings:
    def __init__(self):
        self.showGrid = True
        
settings = Settings()


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

cv.NamedWindow("Image window", 1)


FilterWindowName = "Filter Window "
def nothing(da):
    pass
    
def setupGUI(tag, min_default=128, max_default=128):
    global FilterWindowName
    cv2.namedWindow(FilterWindowName+tag, 2)
    cv2.createTrackbar(tag+" Min", FilterWindowName+tag, min_default, 255, nothing)
    cv2.createTrackbar(tag+" Max", FilterWindowName+tag, max_default, 255, nothing)
    
    
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
    cv2.erode(im, im, None, 3)
    cv2.dilate(im, im, None, 3)
    
    cv2.dilate(im, im, None, 3)
    cv2.erode(im, im, None, 3)
    return im

cntrs = None
hier = None
def PickBlob(im):
    global cntrs, hier
    [cntrs, hier] = cv2.findContours(im, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE, cntrs, hier)

    high_bnd = cv2.getTrackbarPos(" Max", FilterWindowName)
    low_bnd = cv2.getTrackbarPos(" Min", FilterWindowName)
    cntrs = []
    for cntr in cntrs:
        ara = cv2.contourArea(cntr)
        if(low_band < ara < high_bnd):
            cntrs.append(cntr)
    
    centroids = []
    for cntr in cntrs:
        mu = cv2.moments(cntr)
        #print "MU: " + str(mu)
        mx = mu['m10']/mu['m00']
        my = mu['m01']/mu['m00']
        centroids.append( (mx,my) )
    return centroids


cap = cv2.VideoCapture(-1)
cap.set(cv.CV_CAP_PROP_FRAME_WIDTH , 320); 
cap.set(cv.CV_CAP_PROP_FRAME_HEIGHT , 240);
cap.set(cv.CV_CAP_PROP_FPS, 20); 
cap.set(cv.CV_CAP_PROP_FOURCC, cv.CV_FOURCC('R', 'G', 'B', '3'))
for i in range(0,20):
    ret, cv_image = cap.retrieve()
    cv.WaitKey(100)

class TCPClient:
    def __init__(self, Address, Port):
        self.open_server()

    def open_server(self):
        # Create a TCP/IP socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Connect the socket to the port where the server is listening
        server_address = (Address, Port)
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

    
tcpc = TCPClient('localhost', 4558)


calibCap = cap    
def image_call():
    global FilterWindowName
    ret, cv_image = cap.retrieve()
    if(ret):
        filtered = FindBall(cv_image)
        cv2.imshow(FilterWindowName, filtered)
        mcs = PickBlob(filtered)
        for mc in mcs:
            cv2.circle(cv_image, (int(mc[0]), int(mc[1])), 3, cv.Scalar(255, 0, 0))
        #cv_image = cv2.cvtColor(cv_image, cv.CV_BGR2RGB)
        cvIm = cv.CreateImageHeader((cv_image.shape[1], cv_image.shape[0]), cv.IPL_DEPTH_8U, 3)
        cv.SetData(cvIm, cv_image.tostring(), 
               cv_image.dtype.itemsize * 3 * cv_image.shape[1])
        CompositeShow("Image window", cam1, cvIm, settings)
        #correct the frame 
        tosend = []
        for mc in mcs:
            new = cam1.FrameCorrect(mc[0],mc[1])
            
            rectified = unit2world(new)
            
            #print "Ball: ", str(mc), " -> ", str(new)
            #print "Ball: ", str(mc), " -> ", str(rectified)
            tosend.append(rectified)
        
        #now send it!
        tcpc.send(tosend)

        cv.WaitKey(3)

#set up with sane defaults
setupGUI("Hue", 115, 128)
#setupGUI("Hue")
setupGUI("Value", 218, 255)
# setupGUI("Value")
setupGUI("", 218, 1000)

if(NeedsToSave):
    Save("prefs.txt", cameras);

while(True):
    image_call()
    if(NeedsToSave):
        Save("prefs.txt", cameras);
        NeedsToSave = False
cv.DestroyAllWindows()

   


#play all until one dies
#while(im1 != None and im2 != None and
#      im3 != None and im4 != None):
    # color thresh video
    # -overlay transparent
    
    # + mask 
    # +erode, dilate, flip
    
    # + overlay tracking transparent
    

# + all of these filters as GUI
# + all of these layers as GUI
# + affine - two cameras    
    
# fake distances to get cm accuracy
