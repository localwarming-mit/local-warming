import numpy as np
import cv2

cap = cv2.VideoCapture(-1)

fgbg = cv2.BackgroundSubtractorMOG()

while(1):
    ret, frame = cap.read()
    if frame != None:
        fgmask = fgbg.apply(frame)
        if fgmask != None:
            cv2.imshow('frame',fgmask)
    k = cv2.waitKey(30) & 0xff
    if k == 27:
        break

cap.release()
cv2.destroyAllWindows()
