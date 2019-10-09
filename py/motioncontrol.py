



# Motion Control Code

from Adafruit_PWM_Servo_Driver import PWM
import math
import time

servoPins = [1,2,3,4,5,6]
bulbPins = [8,9,10,12,13,14]
numServos = len(servoPins)
numBulbs = len(bulbPins)
angles = [45,135]

pwm = PWM(0x40, debug=True)

def main():
    setup()
   # test4545()
   
    control(0.4,0)
    time.sleep(1)
    control(0.4,0.2)
    time.sleep(1)
    control(0.4,0.4)
    time.sleep(1)
    control(0.4,0.6)
    time.sleep(1)
    control(0.4,0.8)
    time.sleep(1)
    control(0.4,1.0)
    time.sleep(1)
    control(0.4,0.8)
    time.sleep(1)
    control(0.4,0.6)
    time.sleep(1)
    control(0.4,0.4)
    time.sleep(1)
    control(0.4,0.2)
    time.sleep(1)
    control(0.4,0)
    
#def __init__(self):
#    setup()
#    for i in range(0,2000):
#   	 control(0,0)

def coordToDist(coord,length):
    dist = (coord*length)
    return dist

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
def servoWrite(number,angle):
    pulseWidth = angleToPulse(angle)
    pwm.setPWM(number,0,int(pulseWidth))

def bulbWrite(number,status):
    if status == 'HIGH':
        pwm.setPWM(number,0,4096)
    else:
        pwm.setPWM(number,0,0)

def setup():
    pwm.setPWMFreq(60)
    for i in range(0,numServos):#(int i=0; i<numServos; i++)
        servoWrite(i,90)#servos[i].write(pos);
        time.sleep(.01)

def test4545():
    for i in range(0,10):
        for j in range(0,2):
	    for k in range(0,numServos):
	        servoWrite(servoPins[k],angles[j])
 		time.sleep(1)

def control(x,y):

    #set height of array and length of coordinate grid in meters
    height = 3.5
    length = height*(3.0/4.0)
    #choose array offset depending on array y position
    arrayOffset = length/2

    #determine x coordiante by diving x plane into sixths
    num = int(x/0.1666666)
    #determine y coordinate
    yDist = coordToDist(y,length)
    yDist = yDist - arrayOffset
    #print yDist
    #if coordinate within range of array
    if (yDist>=-(length/2) and yDist<=(length/2)):#or x<0 or x>1:
        theta = distToAngle(yDist,height)
        print 90-theta 
	#print 90-theta+(theta/2)
	#print servoPins[num]
	#print servoPins[num+1]
	#print servoPins[abs(num-1)]
	print str(num)+' , ',str(theta)
        servoWrite(servoPins[num],90-theta)#servos[num].write(90-theta)
        servoWrite(servoPins[abs(num+1)],90-theta+(theta/2))#servos[num+1].write(90-theta+(theta/2))
        servoWrite(servoPins[abs(num-1)],90-theta+(theta/2))#servos[num-1].write(90-theta+(theta/2))
        bulbWrite(num,'HIGH')#digitalWrite(lightPins[num],HIGH)
        for i in range(0,numServos):#for int i=0; i<numServos; i++)
            if i==num or i==num+1 or num==i-1:
                #currently code does not turn off adjacent bulbs
                #occasionally leaving two bulbs on, this can be changed here      
                pass
            else:
                servoWrite(servoPins[i],90)#servos[i].write(90);             # tell servo to go to 90
                bulbWrite(bulbPins[i],'LOW')#digitalWrite(lightPins[i], LOW)  # make sure they are all off
                time.sleep(.01)
         #       pass  

    else:
        for i in range(0,numBulbs):#for (int i=0; i<numLights; i++)
          #  pass
            bulbWrite(bulbPins[i],'LOW')#digitalWrite(lightPins[i], LOW)  #make sure they are all off
        for i in range(0,numServos):#for (int i=0; i<numServos; i++)
            servoWrite(servoPins[i],90)              #tell servo to go to 90
            time.sleep(.01)
          #  pass

if __name__ == "__main__":	
    main()
