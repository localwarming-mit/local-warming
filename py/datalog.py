# Data Logging

import time
import datetime
import timestamp

# create a file object: open it with "write" mode

def main():
    time = timestamp.timestamp()
    log([(0,1,0.1),(0.2,0.4)],time,'-273','98')

def log(coords,time,temp,humidity):
    FileName = 'Log.txt'
    File = open(FileName,"a")
    File.write(str(coords)+';'+time+';'+temp+';'+humidity+'\n')
    File.close()

if __name__ == "__main__":
    main()
