import cv


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
# [5/29/14, 12:32:00 PM] Nick DePalma: http://www.newegg.com/Product/Product.aspx?gclid=CjgKEAjwtZucBRD77aiiq_v4xnASJABkAg8Jog9e7koZY3sZPBI-7GbRgiTaUCGgrpG4ysgxIjYcPfD_BwE&Item=N82E16812504005&nm_mc=KNC-GoogleAdwords&cm_mmc=KNC-GoogleAdwords-_-pla-_-Extenders+%26+Repeaters-_-N82E16812504005&ef_id=Ut9QawAABfTaLDX8:20140529163153:s
# [5/29/14, 12:32:41 PM] Leigh Christie: http://www.amazon.it/dp/B00JAA0FVA/ref=pe_386201_37038291_TE_dp_6
# [5/29/14, 12:36:22 PM] Nick DePalma: 5 calibration between multiple viewpoints
# [5/29/14, 12:53:46 PM] Nick DePalma: github + python + opencv
# [5/29/14, 1:05:11 PM] Nick DePalma: I think I lost you


# 4 different colors, find those, autocalibrate

# teamviewer - disconnected
# fake distances to get cm accuracy
# two cameras working real time
# affine transform



# color thresh video
# + mask -overlay transparent
# +erode, dilate, flip
# -> calib per camera
# + overlay tracking transparent
# + all of these filters as GUI
# + all of these layers as GUI
# + affine - two cameras

# red
# blue
# green
# yellow


class Marker:
	pos = [0,0];
	prefix = "BAD";
	def __init__(self, x, y):
		self.pos = [x,y];

class CalibrationMarker(Marker):
	prefix = "CALIB";
	UID = "-"
	def __init__(self, UID):
		self.__init__(0,0)
		self.UID = UID
		self.prefix = self.prefix + self.UID

CalibrationMarker red = CalibrationMarker("RED"), blue = CalibrationMarker("BLUE"), \
				  green = CalibrationMarker("GREEN"), yellow = CalibrationMarker("YELLOW")

calibrationmarkers = [red, blue, yellow, green]

Camera cam1 = Camera("cam1.mov"), cam2 = Camera("cam2.mov"),  \
	   cam3 = Camera("cam3.mov"), cam4 = Camera("cam4.mov")
cameras = [cam1, cam2, cam3, cam4]

def CalibrateFunc(calibMarkerArray):
	#for each calibration marker, construct matrix to do least squares with
	#find pseudoinverse to unit frame -- least squares
	#affine is pseudoinverse

def FrameCorrect(point, transform):
	return transform*point;

