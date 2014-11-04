import collections
import copy
import numpy
import cv2.cv as cv
import cv2

def pt_dist_L1(pt1, pt2):
    return (pt2[0]-pt1[0])+(pt2[1]-pt1[1]);

def recurTrack(filt, history, trace=[], meanerror=0):
    #returns path through history given filter, along with the mean-sq error

    #first get prediction
    next_pt = filt.predict()

    #next find its nearest neighbor
    pts_t = history.pop(0)
    min_dist = float("inf")
    nn = None
    for q in pts_t:
        if not type(q) == PtKalman:
            # is a point - see if its closest
            dist = pt_dist_L1(q, next_pt)
            if dist < min_dist:
                min_dist = dist;
                nn = q

    #if neighbor, update and recur
    if nn != None:
        filt.correct(nn)
        trace.append(nn)
        meanerror = meanerror + (min_dist*min_dist)

    #check for termination
    if(len(history) == 0):
        return [filt, trace, meanerror/len(trace)]

    #iterate
    recurTrack(filt, history, trace, meanerror)

class PtKalman:
    def __init__(self, pt):
        self.pt = pt
        self.history = [pt]
        self.mse = 0.0
        self.ns = 1
        self.lifespan = 1

        self.kalman = cv.CreateKalman(4, 2, 0)
        self.kalman_state = cv.CreateMat(4, 1, cv.CV_32FC1)
        self.kalman_process_noise = cv.CreateMat(4, 1, cv.CV_32FC1)
        self.kalman_measurement = cv.CreateMat(2, 1, cv.CV_32FC1)


        # set previous state for prediction
        self.kalman.state_pre[0,0]  = pt[0]
        self.kalman.state_pre[1,0]  = pt[1]
        self.kalman.state_pre[2,0]  = 0
        self.kalman.state_pre[3,0]  = 0

        # set kalman transition matrix
        self.kalman.transition_matrix[0,0] = 1
        self.kalman.transition_matrix[0,1] = 0
        self.kalman.transition_matrix[0,2] = 0
        self.kalman.transition_matrix[0,3] = 0
        self.kalman.transition_matrix[1,0] = 0
        self.kalman.transition_matrix[1,1] = 1
        self.kalman.transition_matrix[1,2] = 0
        self.kalman.transition_matrix[1,3] = 0
        self.kalman.transition_matrix[2,0] = 0
        self.kalman.transition_matrix[2,1] = 0
        self.kalman.transition_matrix[2,2] = 0
        self.kalman.transition_matrix[2,3] = 1
        self.kalman.transition_matrix[3,0] = 0
        self.kalman.transition_matrix[3,1] = 0
        self.kalman.transition_matrix[3,2] = 0
        self.kalman.transition_matrix[3,3] = 1

        # set Kalman Filter
        cv.SetIdentity(self.kalman.measurement_matrix, cv.RealScalar(1))
        cv.SetIdentity(self.kalman.process_noise_cov, cv.RealScalar(1e-5))
        cv.SetIdentity(self.kalman.measurement_noise_cov, cv.RealScalar(1e-1))
        cv.SetIdentity(self.kalman.error_cov_post, cv.RealScalar(1))

        self.assignObs(pt, 3)


    def getHistory(self):
        return self.history
    def assignObs(self, pt, err):
        #update the kalman
        self.kalman_measurement[0, 0] = float(pt[0])
        self.kalman_measurement[1, 0] = float(pt[1])

        kalman_estimated = cv.KalmanCorrect(self.kalman, self.kalman_measurement)
        state_pt = (kalman_estimated[0,0], kalman_estimated[1,0])
        #print "State estimate: ", state_pt

        print "Adding pt, ", pt, " to history: ", self.history

        #self.kalman.correct(pt)
        self.history.append(pt)
        self.mse = self.mse + err*err
        self.ns = self.ns + 1

    def one_up(self):
        #print "Filter lifespan before: ", self.lifespan
        self.lifespan = self.lifespan + 1
        #print "Filter lifespan after: ", self.lifespan

    def drawOnImage(self, im, color):
        # go through history and make a line
        #only pick 10 - will make a snake like trace
        li = len(self.history) -1
        prev = self.history[li]
        li = li -1
        scolor = cv.Scalar(color[0], color[1], color[2])
        for i in range(10):
            if(li > 0):
                nextl = self.history[li]
                #print "", prev, " -> ", nextl, " in ", color
                cv2.line(im, tuple((int(prev[0]), int(prev[1]))), tuple((int(nextl[0]), int(nextl[1]))), scolor, 1, cv.CV_AA)
                prev = nextl
                li = li -1

    def predict(self):
        kalman_prediction = cv.KalmanPredict(self.kalman)
        predict_pt  = (kalman_prediction[0,0], kalman_prediction[1,0])

        return predict_pt

    def getMSE(self):
        return self.mse / self.ns

class HumanTracker:
    def __init__(self):
        self.initialize(conf_freq=10, conf_thresh=10)

    def initialize(self, conf_freq, conf_thresh):
        self.confidence_freq = conf_freq
        self.confidence_thresh = conf_thresh
        self.history = collections.deque(maxlen=self.confidence_freq)
        self.filters = []

    def update(self, mcs):
        min_dist_g = 15
        num_updates = 20

        #go through points, absorb the ones that already have tracks
        for filt in self.filters:
            #predict
            next_pt = filt.predict()

            #you only get one
            min_dist = float("inf")
            min_ind = -1
            min_pt = None

            ind = 0
            for mc in mcs:
                # is a point - see if its closest
                dist = abs(pt_dist_L1(mc, next_pt))
                #print "Dist: ", dist, " -> ", mc, " - ", next_pt
                if dist < min_dist:
                    min_pt = mc
                    min_dist = dist
                    min_ind = ind
                ind = ind + 1

            #print "checking out dist: ", min_dist
            #if meets criteria, then remove from history and move on to next filter
            if min_dist < min_dist_g:
                #print "the min dist: ", min_dist
                filt.assignObs(min_pt, min_dist)
                mcs.pop(min_ind)
            filt.one_up()

        #go through remaining - create temp kalmans for them
        for mc in mcs:
            self.filters.append(PtKalman(mc))

        #clear out kalmans that were updated more than x times and
        # have less than y confidence

        # history, mse, lifespan
        toclear = []
        ind = 0
        for filt in self.filters:
            if (len(filt.history) > num_updates and filt.getMSE() > self.confidence_thresh) or (filt.lifespan > 30 and filt.lifespan / len(filt.history) > 0.80):
                toclear.append(ind)
            ind = ind + 1

        #print "TOCLEAR: ", toclear
        #go through indices and clear them out of the filter list
        toclear.reverse()
        for index in toclear:
            self.filters.pop(index)

        print "Num Filters: ", str(self.countConfidentFilters())

    def calcColor(self, indnum):
        r = indnum & 0x1
        g = indnum & 0x2
        b = indnum & 0x4
        return (255*r, 255*g, 255*b)

    def drawFirstEight(self, im):
        ind = 0
        for filt in self.filters:
            filt.drawOnImage(im, self.calcColor(ind))
            ind = ind + 1
        return im

    def countConfidentFilters(self):
        conf = []
        for filt in self.filters: #and filt.getMSE() < self.confidence_thresh
            if (len(filt.history) > 8 ):
                conf.append(filt)
        return conf

    def getConfidentPts(self):
        mcs = []
        for filt in self.countConfidentFilters():
            hlen = len(filt.history)
            mc = filt.history[hlen-1]
            mcs.append(mc)
        return mcs
