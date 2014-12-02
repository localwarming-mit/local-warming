
# Motion Control Code

from Adafruit_PWM_Servo_Driver import PWM
import math
import time
import timestamp
import datalog
import random
import GlobalSettings
from GlobalSettings import trackingTime
from GlobalSettings import waveTime
from GlobalSettings import spotsTime
from GlobalSettings import offsetBit

servoPins = [1,2,3,4,5,6]
bulbPins = [7,8,9,10,11,12]
angles = [0,0,0,0,0,0]

pwm = PWM(0x40, debug=True)

def main():
    setup()
    while(True):
	wave(2.5)
    #fourtyfive()
    tracking([(0.03,0.4),(0.8,0.8)])

def control(coords):

    # check time to determine which method to run
    time = timestamp.clock()
    
    if time == trackingTime:
        tracking(coords)
        # when running tracking, log data
        datalog.datalog(coords,time,'-273','-1')
    elif time == waveTime:
        wave(3)
    elif time == spotsTime:
        spots(3)
    else:
        pass
        #setup()
        
def distToAngle(dist,height):
    angle = (math.atan2(dist,height)*57.0)
    return angle

# returns the pulse width in milliseconds for a given servo angle
def angleToPulse(angle):
    minimumPulse = 150.0 #0.5 milliseconds pulse - angle 0
    maximumPulse = 600.0 #2.5 milliseconds pulse - angle 180
    pulse = minimumPulse+(((maximumPulse-minimumPulse)/180)*angle)
    return pulse

# write an angle to a given servo
def write(number,angle,status):
    servoPin = servoPins[number]
    bulbPin = bulbPins[number]
    #angle = 90-angle
    pulseWidth = angleToPulse(angle)

    #write servo to angle
    pwm.setPWM(servoPin,0,int(pulseWidth))

    #turn bulb on or off 
    if status == 'ON':
        pwm.setPWM(bulbPin,4096,0)
    else:
        pwm.setPWM(bulbPin,0,0)

def setup():
    pwm.setPWMFreq(60)
    for i in range(0,6):
        write(i,90,'OFF')
        time.sleep(.01)

# main control method for bulbs
# takes coordinate list of tuples and writes to PWM driver

def tracking(coords):
    
    pwm.setPWMFreq(60)
    angles = [0,0,0,0,0,0]
    
    # coords is a list of tuples coresponding to three points
    height = 2.0
    length = height*(0.75)
    print length
    yOffset = length/2.0
    xOffset = 0.5
    xPos = 0
    yPos = 0

    # nums will be filled with array numbers cooresponding to the x coordinate of detected blobs
    nums = [-1,-1]
   
    i = 0
    for coord in coords[0]:
         #if the coordinate is -1, indicating there is no blob, then pass
         if coords[0][0] == 1.1:
             pass
         #otherwise, check to see what bulb the x coordinate corresponds to
         else:   
            xPos = (1-coords[0][0]) - xOffset
	    print xPos
            yPos = coords[0][1]*length - yOffset
	    print yPos	

            if xPos>=0 and xPos<1:
                nums[i]=int(xPos/0.1666666)
                angles[nums[i]]=distToAngle(yPos,height)
		angles[nums[i]]=angles[nums[i]]*-1
    i+=1
    
    for coord in coords[1]:

	if coords[1][0] == 1.1:
	    pass
	else:
	    xPos = (1-coords[1][0]) + xOffset
	    print xPos
	    yPos = coords[1][1]*length - yOffset
	    print yPos

	    if xPos>=0 and xPos<1:
		nums[i]=int(xPos/0.1666666)
		angles[nums[i]]=distToAngle(yPos,height)
		angles[nums[i]]=angles[nums[i]]*-1
    i+=1
	
    #print coords[0],coords[1]
    # handle assinging the angles for bulbs directly adjacent to on bulbs 

    for j in range(0,len(angles)):
        #print j
        if j==0:
            if angles[j] != 0 and angles[j+1] == 0:
                angles[j+1] = angles[j]/2
        elif j==5:
            if angles[j] != 0 and angles[j-1] == 0:
                angles[j-1] = angles[j]/2
        else:   
            if angles[j] != 0 and angles[j-1] == 0:
                angles[j-1] = angles[j]/2
                if angles[j+1] == 0:
                    angles[j+1] = angles[j]/2
            #elif angles[j] != 0 and angles[j+1] == 0:
            #    print 'yipee'
            #    angles[j+1] = angles[j]/2
	
    for x in range(0,len(angles)):	
    	angles[x]+=90

    print angles

    # write the angles to the bulbs and turn correct bulbs on and off
    for k in range(0,len(angles)):
        if k in nums:
            write(k,angles[k],'ON')
	    #print 'wrote'
        else:
            write(k,angles[k],'OFF')
	    #print 'wrote'

# sweeps arrays in a wave pattern

def wave(delay):
    #sweep in wave pattern
    #arrays 1&2 on one side
    #arrays 4&5 on the other
    #array 3 is transition
    for i in range(0,6):
	angle = 60
	write(i,angle,'ON')
	write(i-1,90,'OFF')

    #if array == 1 or array == 2:
    #    for i in range(0,6):
    #        angle = 60
    #        write(i,angle,'ON')
    #        write(i-1,'OFF')
    #        time.sleep(delay)
    #elif array == 4 or array == 5:
    #    for i in range(0,6):
    #        angle = 120
    #        write(i,angle,'ON')
    #        write(i-1,'OFF')
    #        time.sleep(delay)
    #elif array == 3:
    #    for i in range(0,6):
    #        angle = (15*i)+45
    #        write(i,angle,'ON')
            write(i-1,'OFF')
            time.sleep(delay)
    else:
        pass

# writes a random bulb to a random angle with random delay

def spots(delay):
    
    randomBulb = random.random()
    randomAngle = random.random()
    randomDelay = random.random()
    angle = int((randomAngle*60)+60)
    bulb = int((randomBulb*6)+1)
    #delay = int((delay*randomDelay)+1)

    for i in range(1,6):
        if i == bulb:
            write(i,angle,'ON')
	    write(i-1,angle-5,'ON')
        else:
            write(i,90,'OFF')

    time.sleep(delay)

#sweeps the bulbs 45-45

def fourtyfive():
    for i in range(0,10):
        for j in range(0,6):
            if j%2 == 0:
                write(j,45,'OFF')
            else:
                write(j,135,'OFF')
                
        time.sleep(1)
        
        for k in range(0,6):
            if k%2 == 0:
                write(k,45,'OFF')
            else:
                write(k,135,'OFF')

        time.sleep(1)

if __name__ == "__main__":  
    main()

