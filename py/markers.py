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
