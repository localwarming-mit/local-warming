import smbus
import time
import datetime
import math

#This program takes an x,y coordinate and updates the point on a .txt file
#along with a timestamp from the Raspberry Pi clock (synced with RTC module)

def main():
	log()

def log(x,y):
	file = open('Coordinates.txt','a')
	now = datetime.datetime.now()
	timestamp = now.strftime('%Y%m/%d %H:%M')
	data = 'point: ' + str(x) + ',' +str(y) + ' time: ' + str(timestamp)
	file.write(data)
	file.close
	print data

if __name__ == "main":
	main()
