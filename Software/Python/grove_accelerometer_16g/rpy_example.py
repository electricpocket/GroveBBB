# ADXL345 Python example 
#
# author:  Jonathan Williamson
# license: BSD, see LICENSE.txt included in this package
# 
# This is an example to show you how to the Grove +-16g Accelerometer
# http://www.seeedstudio.com/depot/Grove-3Axis-Digital-Accelerometer16g-p-1156.html

from adxl345 import ADXL345
import time
import math

adxl345 = ADXL345()
    
print("ADXL345 on address 0x%x:" % (adxl345.address))
while True:
    axes = adxl345.getAxes(True)
    roll= 180*(math.atan2(-axes['y'],axes['z']))/math.pi
    pitch = 180*(math.atan2(-axes['x'],(axes['y']*axes['y']+axes['z']*axes['z'])))/math.pi
    print(( axes['x'] ),"\t",( axes['y'] ),"\t",( axes['z'] ))
    print ("Pitch: ",pitch,"Roll: ", roll, "degrees")
    time.sleep(.1)
 