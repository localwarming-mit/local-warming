import cv
import numpy
import numpy.linalg

# A = SVD - pseudoinverse 
#
# * * 1,1 
# * *
#
#  ^
#  |
#
# *     *
#    *        *
#
#  

# [5/29/14, 12:29:29 PM] Nick DePalma: 1- tracking ball - pictures throughout the day
# [5/29/14, 12:30:58 PM] Nick DePalma: 2 - actually track the ball with these challenge datasets
# [5/29/14, 12:31:30 PM] Nick DePalma: 3 - experiment with how many cameras a single machine can handle
# [5/29/14, 12:31:40 PM] Nick DePalma: 4 - experiment with how many cameras at a distance



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
            self.capture = cv.CaptureFromCAM(id);

        self.calibrated = False
        self.id = id;

    def next(self):
        self.cur = cv.QueryFrame(self.capture)
        return self.cur;
    def Save(self, f, prefix=""):
        for calib in self.calibrationmarkers:
            calib.Save(f, "CAM"+str(self.id))
    
    def Load(self, line, prefix=""):
        iscalib = [calib.Load(line, "CAM"+str(self.id)) for calib in self.calibrationmarkers]
        self.LdCounter += iscalib.count(True)
        self.calibrated = self.calibrated or self.LdCounter == len(self.calibrationmarkers)

    def Calibrate(self, withMouse):
        if(withMouse):
            MouseCalibrate(self.cur, self.calibrationmarkers);
        else:
            AutoCalibrate(self.cur, self.calibrationmarkers);
        self.CalibrateFunc()
        self.calibrated = True

    def CalibrateFunc(self):
        #for each calibration marker, construct matrix to do least squares with
        numrows = 2*len(self.calibrationmarkers)
        A = numpy.zeros((numrows, 9))
        B = numpy.zeros((numrows, 1))
        # marker 1: 0,0
        # marker 2: 1,0
        # marker 3: 0,1
        # marker 4: 1,1
        #B(0),B(1) = 0   #marker 1
        B[2] = 1; B[5]=1 #marker 2,3
        B[4] = 1;
        B[6] = 0; B[7]=1 
        #B[3] = 1; B[4]=1 #marker 2,3
        #B[6] = 1; B[7]=1 #marker 4
        i = 0
        for calib in self.calibrationmarkers:
            A[2*i, 0] = calib.pos[0]; A[2*i, 1] = calib.pos[1]
            A[2*i+1, 3] = calib.pos[0]; A[2*i+1, 4] = calib.pos[1]
            A[2*i,2] = 1; A[2*i+1,5] = 1
            A[2*i,6] = -B[2*i]*calib.pos[0]
            A[2*i,7] = -B[2*i]*calib.pos[1]
            A[2*i,8] = -B[2*i]
            
            A[2*i+1,6] = -B[2*i+1]*calib.pos[0]
            A[2*i+1,7] = -B[2*i+1]*calib.pos[1]
            A[2*i+1,8] = -B[2*i+1]
            
            i = i + 1
            
        #print "A shape: " + str(A.shape) + " and B shape: " + str(B.shape)
        #find pseudoinverse to unit frame -- least squares
        #ata = A.T*A
        U, s, V = numpy.linalg.svd(A, full_matrices=True)
        #sh = s
        #print "USV: \n" + str(U) + "\n" + str(s) + "\n" + str(V)
        #n = min(s.shape)
        #print "got n: ", str(n), " and ", str(s.shape)
        #print "U shape: " + str(U.shape) + " and V shape: " + str(V.shape)
        #for i in range(0, n):
        #    if(sh[i] != 0):
        #        sh[i] = 1.0/sh[i]
        
        #ata_inv = V.conj().T*numpy.diag(sh)*U.conj().T
        
        # get eigenvalues
        #L = numpy.dot(A.T,B)
        #L = numpy.dot(ata_inv, B)
        #print "Here we are: ", str(L.shape)
        #affine is reconstruction of lambda
        L = V[8,:].T
        #L = L / numpy.linalg.norm(L)
        H = numpy.zeros((3,3))
        for i in range(0,9):
            H[i/3,i%3] = L[i]
        #H[2,2] = 1
        self.homography = H
        
        print "Got Homography: \n", H
        print "Got L: \n", L
        print "From: \n", A
        self.W = numpy.array([H[2,0], H[2,1], 1])
        return H

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

def FrameCorrect(point, transform, W):
    hmgneus = numpy.zeros(3)
    hmgneus[0] = point[0]
    hmgneus[1] = point[1]
    hmgneus[2] = 1
    xw = numpy.dot(transform,hmgneus)
    Ws = numpy.dot(W, hmgneus)
    
    return (xw[0]/Ws, xw[1]/Ws)

def CompositeShow(windowName, camera, settings):
    cv.NamedWindow(windowName)
    comp = cv.CloneImage(camera.cur)
    
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
        
    cv.ShowImage(windowName, comp)

cam1 = Camera("../cam1.mov");
cam2 = Camera("../cam2.mov");
cam3 = Camera("../cam3.mov");
cam4 = Camera("../cam4.mov");

cameras = [cam1,cam2,cam3,cam4]

im1 = cam1.next()
cv.SaveImage("test.jpg", im1)
im2 = cam2.next()
im3 = cam3.next()
im4 = cam4.next()

Load("prefs.txt", cameras);
ManualCalibrate = True;

NeedsToSave = False
print "calibs: " + str([x.calibrated for x in cameras])


if(not reduce(lambda a,b: a and b, [x.calibrated for x in cameras])):
    #recalibrate
    NeedsToSave = True
    [cam.Calibrate(ManualCalibrate) for cam in cameras]
else:
    [cam.CalibrateFunc() for cam in cameras]
    
if(NeedsToSave):
    Save("prefs.txt", cameras);



# 4 different colors, find those, autocalibrate

# teamviewer - disconnected

# two cameras working real time
# affine transform


# -> calib per camera
class Settings:
    def __init__(self):
        self.showGrid = True
        
settings = Settings()


#Test 1
##CompositeShow("Camera 1", cam1, settings) 
##def mouseback_rect(event,x,y,flags,param):
##    if event==cv.CV_EVENT_LBUTTONUP:		# here event is left mouse button double-clicked
##        new = FrameCorrect([x,y], cam1.homography, cam1.W)
##        print x,y, "->", new
##        
##        
##
##cv.SetMouseCallback("Camera 1", mouseback_rect);
##cv.WaitKey()


#Test 2
CompositeShow("Camera 1", cam1, settings) 
def mouseback_rect(event,x,y,flags,param):
    if event==cv.CV_EVENT_LBUTTONUP:		# here event is left mouse button double-clicked
        new = FrameCorrect([x,y], cam1.homography, cam1.W)
        print x,y, "->", new
        
        

cv.SetMouseCallback("Camera 1", mouseback_rect);
cv.WaitKey()

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
