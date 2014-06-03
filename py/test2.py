def PointOnLine(x1, x2, x0):
    n = math.sqrt(numpy.dot(x2-x1,x2-x1))
    #print "n: ", str(n)
    detmat = numpy.zeros((2,2))
    detmat[:,0] = x2-x1
    detmat[:,1] = x1-x0
    d = numpy.linalg.det(detmat)/n
    #print "d: ", str(d)
    v = numpy.zeros(2)
    v[0] = x2[1]-x1[1]
    v[1] = -(x2[0]-x1[0])
    #print "v: ", str(v)
    v = v / math.sqrt(numpy.dot(v,v));
    ot = x0-v*d
    #print "OT: ", str(ot)
    return ot
    #normalized coords
    nc = (ot-x1) / n
    #print "nc: ", str(nc)
    p = math.sqrt(numpy.dot(nc*nc))
    
    
    #print "p: ", str(p)
    return p

def GetFourPoints(camera, pt):
     #p1 - p2
    pt12 = PointOnLine(numpy.array(camera.calibrationmarkers[0].pos), \
                        numpy.array(camera.calibrationmarkers[1].pos), pt)

    #p1 - p4
    pt14 = PointOnLine(numpy.array(camera.calibrationmarkers[3].pos), \
                        numpy.array(camera.calibrationmarkers[0].pos), pt)
    
    #p3 - p4
    pt34 = PointOnLine(numpy.array(camera.calibrationmarkers[2].pos), \
                        numpy.array(camera.calibrationmarkers[3].pos), pt)
    
    #p2 - p3
    pt23 = PointOnLine(numpy.array(camera.calibrationmarkers[1].pos), \
                        numpy.array(camera.calibrationmarkers[2].pos), pt)
    return [pt12, pt14]#, pt34, pt23]

#Test 2
ptsyu = []
CompositeShow("Camera 1", cam1, settings) 
def mouseback_rect(event,x,y,flags,param):
    global ptsyu
    if event==cv.CV_EVENT_LBUTTONUP:		# here event is left mouse button double-clicked
        #x1 = [77, 92]
        #x2 = [147, 74]
        #new = PointOnLine(numpy.array(x1), numpy.array(x2), numpy.array([110, 96]))
        #print x,y, "->", new
        ptsyu = GetFourPoints(cam1, numpy.array([x, y]))
        
        

cv.SetMouseCallback("Camera 1", mouseback_rect);
cv.WaitKey(1)
while(True):
    CompositeShow("Camera 1", cam1, settings, ptsyu)
    cv.WaitKey(1)