import cv2
import cv
import numpy
import numpy.linalg


calibCap = None
def MouseCalibrate(image, markers):
    windowName = "Choose Point";
    cv2.namedWindow(windowName)
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
        cv2.imshow(windowName, image);
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

