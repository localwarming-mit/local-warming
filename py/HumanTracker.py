import cv2
import collections
import copy

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
        self.kalman = cv2.KalmanFilter()

class HumanTracker:
    def __init__(self):
        self.initialize(conf_freq=10, conf_thresh=45)

    def initialize(self, conf_freq, conf_thresh):
        self.confidence_freq = conf_freq
        self.confidence_thresh = conf_thresh
        self.history = collections.deque(maxlen=self.confidence_freq)
        self.filters = []

    def update(self, mcs):
        #check for new tracks starting at beginning
        if len(self.history) == self.history.maxlen:
            for q in self.history:
                if not type(q) == PtKalman:
                    # try to find its partner
                    [filt, track, meanerr] = recurTrack(PtKalman(q), copy.copy(self.history))
                    #take a penalty if few pts absorbed
                    penalty_per_missed = 25
                    meanerr = meanerr + (penalty_per_missed*(len(self.history)-len(track)))
                    if meanerr < self.confidence_thresh:
                        self.addTrack(filt, track)


        #ask filters to update themselves on the new pts
        filtUpdates()
        #update history
        self.append(mcs)

    def addTrack(self, filte, track):
        #add to filters
        self.filters.append([filte, track])
        #go through history and update the tracks with the attached filters
