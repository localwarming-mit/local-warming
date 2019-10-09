import time
import datetime

def main():
    print clock()

# return a date and time from the computer clock

def timestamp():
    t = time.time()
    stamp = datetime.datetime.fromtimestamp(t).strftime('%Y-%m-%d %H:%M:%S')
    return stamp

# parse a time stamp first into the time, and then into the hour

# split(" ",1) will split a string into an array containing the strings
# before the selected character and after the character

def clock():
    stamp = timestamp()
    stamp_list = stamp.split(" ",1)
    time = stamp_list[1]
    return time

def hour():
    stamp = timestamp()
    stamp_list = stamp.split(" ",1)
    time = stamp_list[1]
    hour = time.split(":",1)
    return hour[0]

# parse a time stamp first into the time, and then into the hour

def minute():
    stamp = timestamp()
    stamp_list = stamp.split(" ",1)
    time = stamp_list[1]
    minsec = time.split(":",1)
    minute = minsec[1].split(":",1)
    return minute[0]

def second():
    stamp = timestamp()
    stamp_list = stamp.split(" ",1)
    time = stamp_list[1]
    minsec = time.split(":",1)
    second = minsec[1].split(":",1)
    return second[1]
    
if __name__ == "__main__":
    main()

