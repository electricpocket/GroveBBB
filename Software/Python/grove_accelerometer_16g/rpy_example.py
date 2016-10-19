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
import socket

def checksum(sentence):
    sentence = sentence.strip('\n')
    nmeadata=sentence
    #,cksum = sentence.split('*', 1)
    calc_cksum = reduce(operator.xor, (ord(s) for s in nmeadata), 0)

    #return nmeadata,int(cksum,16),calc_cksum
    return calc_cksum

adxl345 = ADXL345()
server_address = ('crowdais.com', 5114)

  
print("ADXL345 on address 0x%x:" % (adxl345.address))
heave=0;sway=0;surge=0;rollsum=0;pitchsum=0;pitchmax=0;rollmax=0;surgemax=0;heavemax=0;heavemin=99;swaymax=0
heaveV=0;swayV=0;surgeV=0;surgesum=0;heavesum=0;swaysum=0
count=0; 
while True:
    axes = adxl345.getAxes(True)
    pitch= 180*(math.atan2(-axes['y'],axes['z']))/math.pi
    roll = 180*(math.atan2(-axes['x'],(axes['y']*axes['y']+axes['z']*axes['z'])))/math.pi
    heave=axes['z']
    sway=axes['x']
    surge=axes['y']
    print(( "Sway: ",axes['x'] )," Surge: ",( axes['y'] )," Heave: ",( axes['z'] ))
    print ("Pitch: ",pitch," Roll: ", roll, "degrees")
    heaveV+=heave
    swayV+=sway
    surgeV+=surge
    heavesum+=heaveV
    swaysum+=swayV
    surgesum+=surgeV
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
        #proprietary Pocket Mariner NMEA sentence A
        #see https://docs.google.com/document/d/1P1K23f8aAzeZkK1TB_iIkhLFMHQiSzMuK3u-V7evQaM/edit?usp=sharing
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(server_address)
        msg = 'P' + 'PMR' +'A,'+ timestamp+',' + '0'+','+ 'T'+','+ ("%.2f" %rollmax)+','+ str(pitchmax)+',' +str(heavemax)+',0,0,0,'+str(swaymax)+','+str(surgemax)+',0,0'
        chksum=checksum(msg)
        nmea='$' + msg+'*'+ ("%X" %chksum)
        jsonmsg = '{"timestamp":'+ timestamp+',"id":'+'7114'+',"rollmax":'+("%.2f" %rollmax)+',"pitchmax":'+ str(pitchmax)+',"heavemax":' +str(heavemax)+',"swaymax":'+str(swaymax)+',"surgemax":'+str(surgemax)+'}'
        print jsonmsg 
        s.sendall(jsonmsg)
        msg = 'P' + 'PMR' +'B,'+ timestamp+',' + '0'+','+ 'T'+','+ ("%.2f" %roll)+','+ str(pitch)+',' +str(heavesum)+',0,0,0,'+str(swaysum)+','+str(surgesum)+',0,0'
        chksum=checksum(msg)
        nmea= '$' + msg+'*'+ ("%X" %chksum)
        jsonmsg = '{"timestamp":'+ timestamp+',"id":'+'7114'+',"rollmax":'+("%.2f" %roll)+',"pitchmax":'+ str(pitch)+',"heavemax":' +str(heavesum)+',"swaymax":'+str(swaysum)+',"surgemax":'+str(surgesum)+'}'
        print jsonmsg 
        s.sendall(jsonmsg)
        s.close()
        
        #zero values
        heave=0;sway=0;surge=0;rollsum=0;pitchsum=0;pitchmax=0;rollmax=0;surgemax=0;heavemax=0;heavemin=99;swaymax=0
        surgesum=0;heavesum=0;swaysum=0
        #don't zero velocities unless they are mad - just decay them for now in case of offsets.
        heaveV=heaveV/2
        surgeV=surgeV/2
        swayV=swayV/2
        count=0  
        
    count=count+1 
    time.sleep(1)
    
 