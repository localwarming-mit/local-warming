from markers import CalibrationMarker
import cv
import numpy

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
