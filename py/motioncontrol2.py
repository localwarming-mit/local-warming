# Motion Control Code

from Adafruit_PWM_Servo_Driver import PWM
import math
import time

servoPins = [1,2,3,4,5,6]
lightPins = [7,8,9,10,11,12]
numServos = len(servoPins)
numLights = len(lightPins)

pwm = PWM(0x40, debug=True)

def main():
    setup()
    control4545()
    #wave1(2)

def coordToFeet(coord):
    feet = (coord*12.0)+4.0
    return feet

def feetToAngle(feet):
    angle = (math.atan2(feet,12.0)*57.0)
    return angle

# returns the pulse width in milliseconds for a given servo angle
def angleToPulse(angle):
    minimumPulse = 150.0 #0.5 milliseconds pulse - angle 0
    maximumPulse = 600.0 #2.5 milliseconds pulse - angle 180
    pulse = minimumPulse+(((maximumPulse-minimumPulse)/180)*angle)
    return int(pulse)

# write an angle to a given servo
def servoWrite(number,angle):
    pulseWidth = angleToPulse(angle)
    pwm.setPWM(number,0,pulseWidth)

def bulbWrite(number,status):
    if status == 'ON':
        pwm.setPWM(number,4096,0)
    else:
        pwm.setPWM(number,0,0)

def setup():
    pwm.setPWMFreq(60)
    for i in range(0,numServos+1):#(int i=0; i<numServos; i++)
        servoWrite(i,90)#servos[i].write(pos);
        time.sleep(.01)

def wave1(delay):
    #stamp = timestamp.seconds()
    stamp = delay
    time.sleep(delay)
    if stamp == delay:
 	for i in range(1,6):
	    servoWrite(i,60)
	    bulbWrite(i+6,'ON')
            bulbWrite(i+5,'OFF')
            time.sleep(1)
	else:
	    pass

def wave2(delay):
    #stamp = timestamp.seconds()
    stamp = delay
    time.sleep(delay)
    if stamp == delay:
	servoWrite(i,(15*i)+45)
        bulbWrite(i+6,'ON')
        bulbWrite(i+5,'OFF')
        time.sleep(1)    
    else:
        pass

def wave3(delay):
    #stamp = timestamp.seconds()
    stamp = delay
    time.sleep(delay)
    if stamp == delay:
        servoWrite(i,120)
        bulbWrite(i+6,'ON')
        bulbWrite(i+5,'ON')
        time.sleep(1)
    else:
	pass


def control4545():
    time.sleep(600)
    for x in range(0,10):
    	servoWrite(1,45)
        bulbWrite(7,'ON') 
    	servoWrite(3,45)
        bulbWrite(8,'ON') 
    	servoWrite(5,45)
        bulbWrite(11,'ON') 
    	servoWrite(2,135)
        bulbWrite(9,'OFF')
    	servoWrite(4,135)
        bulbWrite(10,'OFF')
    	servoWrite(6,135)
        bulbWrite(12,'OFF')
    	time.sleep(2)
    	servoWrite(1,135)
        bulbWrite(7,'OFF')
    	servoWrite(3,135)
        bulbWrite(8,'OFF') 
    	servoWrite(5,135)
        bulbWrite(11,'OFF')
    	servoWrite(2,45)
        bulbWrite(9,'ON')
    	servoWrite(4,45)
        bulbWrite(10,'ON')
    	servoWrite(6,45)
        bulbWrite(12,'ON')
    	time.sleep(2)

def control(x, y):

    #choose array offset depending on array y position

    #array 1
    arrayOffset = 0
    #array 2
    #arrayOffset = 10.0
    #array 3
    #float arrayOffset = 20

    #determine x coordiante by diving x plane into sixths
    num = int(x/0.1666666)

    #determine y coordinate
    yFeet = coordToFeet(y)
    yFeet = int(yFeet - arrayOffset)

    #if coordinate within range of array
    if (yFeet>-8 and yFeet<8):#or x<0 or x>1:
        theta = feetToAngle(yFeet)
        servoWrite(num,90-theta)#servos[num].write(90-theta)
        servoWrite(num+1,90-theta+(theta/2))#servos[num+1].write(90-theta+(theta/2))
        servoWrite(num-1,90-theta+(theta/2))#servos[num-1].write(90-theta+(theta/2))
        bulbWrite(num,'HIGH')#digitalWrite(lightPins[num],HIGH)
        for i in range(0,numServos):#for int i=0; i<numServos; i++)
            if i==num or i==num+1 or num==i-1:
                pass
            else:
                servoWrite(i,90)#servos[i].write(90);             # tell servo to go to 90
                bulbWrite(i,'LOW')#digitalWrite(lightPins[i], LOW)  # make sure they are all off
                time.sleep(.01)

    else:
        for i in range(0,numLights):#for (int i=0; i<numLights; i++)
            bulbWrite(i,'LOW')#digitalWrite(lightPins[i], LOW)  #make sure they are all off
        for i in range(0,numServos):#for (int i=0; i<numServos; i++)
            servos[i].write(90)              #tell servo to go to 90
            time.sleep(.01)

if __name__ == "__main__":
	main()
