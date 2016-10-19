# ADXL345 Python example 
#
# author:  Jonathan Williamson
# license: BSD, see LICENSE.txt included in this package
# 
# This is an example to show you how to the Grove +-16g Accelerometer
# http://www.seeedstudio.com/depot/Grove-3Axis-Digital-Accelerometer16g-p-1156.html
# Provide average over a minute and maximum for all 6 parameters
from adxl345 import ADXL345
import time
import math
#import pynmea2
from datetime import datetime
import operator

def checksum(sentence):
    sentence = sentence.strip('\n')
    nmeadata=sentence
    #,cksum = sentence.split('*', 1)
    calc_cksum = reduce(operator.xor, (ord(s) for s in nmeadata), 0)

    #return nmeadata,int(cksum,16),calc_cksum
    return calc_cksum

adxl345 = ADXL345()
    
print("ADXL345 on address 0x%x:" % (adxl345.address))
heave=0;sway=0;surge=0;rollsum=0;pitchsum=0;pitchmax=0;rollmax=0;surgemax=0;heavemax=0;heavemin=99;swaymax=0
count=0; 
while True:
    axes = adxl345.getAxes(True)
    pitch= 180*(math.atan2(-axes['y'],axes['z']))/math.pi
    roll = 180*(math.atan2(-axes['x'],(axes['y']*axes['y']+axes['z']*axes['z'])))/math.pi
    print(( "Sway: ",axes['x'] )," Surge: ",( axes['y'] )," Heave: ",( axes['z'] ))
    print ("Pitch: ",pitch," Roll: ", roll, "degrees")
    heave+=axes['z']
    sway+=axes['x']
    surge+=axes['y']
    pitchsum+=pitch
    rollsum+=roll
    pitchmax=max(pitchmax,pitch)
    rollmax=max(rollmax,roll)
    heavemax=max(heavemax,heave)
    heavemin=min(heavemin,heave)
    swaymax=max(swaymax,sway)
    surgemax=max(surgemax,surge)
    if ((count % 60) == 0):
        roll=rollsum/60
        pitch=pitchsum/60
        #send out NMEA messages with readings
        timestamp = "{:%H%M%S}".format(datetime.now())
        msg = 'PA' + 'SHR' +','+ timestamp+',' + '0'+','+ 'T'+','+ ("%.2f" %rollmax)+','+ str(pitchmax)+',' +str(heavemax)+',0,0,0,2,1'
        chksum=checksum(msg)
        print msg+'*'+str(chksum)
        #zero values
        heave=0;sway=0;surge=0;rollsum=0;pitchsum=0;pitchmax=0;rollmax=0;surgemax=0;heavemax=0;heavemin=99;swaymax=0
        count=0  
        
    count=count+1 
    time.sleep(1)
    
 