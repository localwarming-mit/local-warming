
# Motion Control Code

#from Adafruit_PWM_Servo_Driver import PWM
import math
import time
import timestamp
import datalog
import random
import GlobalSettings
from GlobalSettings import trackingTime
from GlobalSettings import waveTime
from GlobalSettings import spotsTime

servoPins = [1,2,3,4,5,6]
bulbPins = [7,8,9,10,11,12]
angles = [90,90,90,90,90,90]

#pwm = PWM(0x40, debug=True)

def main():
    #setup()
    #fourtyfive()
    control([(-1,-1),(-1,-1)])

def control(coords):

    # check time to determine which method to run
    time = timestamp.clock()
    
    if time == trackingTime:
        tracking(coords)
        # when running control2, log data
        datalog.datalog(coords,time,'-273','-1')
    elif time == waveTime:
        wave(3)
    elif time == spotsTime:
        spots(3)
    else:
        pass
        #setup()
        
def coordToAngle(coord,length,height):
    dist = (coord*length)
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
    angle = 90-angle
    pulseWidth = angleToPulse(angle)

    #write servo to angle
    #pwm.setPWM(servoPin,0,int(pulseWidth))

    #turn bulb on or off 
    if status == 'ON':
        pass
        #pwm.setPWM(bulbPin,4096,0)
    else:
        pass
        #pwm.setPWM(bulbPin,0,0)

def setup():
    #pwm.setPWMFreq(60)
    for i in range(0,6):
        write(i,90,'OFF')
        time.sleep(.01)

# main control method for bulbs
# takes coordinate list of tuples and writes to PWM driver

def tracking(coords):

    angles = [90,90,90,90,90,90]
    
    # coords is a list of tuples coresponding to three points
    height = 1#3.5
    length = 1#height*(3/4)
    yOffset = 0
    xOffset = 0 #could be -height/2 depending on side 
    xPos = 0
    yPos = 0

    # nums will be filled with array numbers cooresponding to the x coordinate of detected blobs
    nums = [-1,-1]

    i = 0
    for coord in coords:
        # if the coordinate is -1, indicating there is no blob, then pass
        if coord[0] == -1:
            pass
        # otherwise, check to see what bulb the x coordinate corresponds to
        else:   
            xPos = coord[0] - xOffset
            yPos = coord[1] - yOffset

            if coord[0]>=0:
                nums[i]=int(xPos/0.1666666)
                angles[nums[i]]=coordToAngle(yPos,length,height)
        i+=1

    # handle assinging the angles for bulbs directly adjacent to on bulbs 

    for j in range(0,len(angles)):
        print j
        if j==0:
            if angles[j] != 90 and angles[j+1] == 90:
                angles[j+1] = angles[j]/2
        elif j==5:
            if angles[j] != 90 and angles[j-1] == 90:
                angles[j-1] = angles[j]/2
        else:   
            if angles[j] != 90 and angles[j-1] == 90:
                angles[j-1] = angles[j]/2
                if angles[j+1] == 90:
                    angles[j+1] = angles[j]/2
            #elif angles[j] != 90 and angles[j+1] == 90:
            #    print 'yipee'
            #    angles[j+1] = angles[j]/2

    print angles

    # write the angles to the bulbs and turn correct bulbs on and off
    for k in range(0,numServos):
        if k in nums:
            write(k,angles[k],'ON')
        else:
            write(k,angles[k],'OFF')

# sweeps arrays in a wave pattern

def wave(delay,array):
    #sweep in wave pattern
    #arrays 1&2 on one side
    #arrays 4&5 on the other
    #array 3 is transition
    
    if array == 1 or array == 2:
        for i in range(0,6):
            angle = 60
            write(i,angle,'ON')
            write(i-1,'OFF')
            time.sleep(delay)
    elif array == 4 or array == 5:
        for i in range(0,6):
            angle = 120
            write(i,angle,'ON')
            write(i-1,'OFF')
            time.sleep(delay)
    elif array == 3:
        for i in range(0,6):
            angle = (15*i)+45
            write(i,angle,'ON')
            write(i-1,'OFF')
            time.sleep(delay)
    else:
        pass

# writes a random bulb to a random angle with random delay

def spots(delay):
    
    randomBulb = random.random()
    randomAngle = random.random()
    randomDelay = random.random()
    angle = int((randomAngle*90)+45)
    bulb = int((randomBulb*6)+1)
    delay = int((delay*randomDelay)+1)

    for i in range(0,6):
        if i == bulb:
            write(i,angle,'ON')
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
