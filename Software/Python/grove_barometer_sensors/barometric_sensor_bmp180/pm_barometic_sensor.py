#!/usr/bin/python

import smbus
import Adafruit_BBIO.GPIO as GPIO
#import grovepi
from grove_i2c_barometic_sensor_BMP180 import BMP085
from datetime import datetime
import socket
import json
import time

# ===========================================================================
# Example Code
# ===========================================================================

# Initialise the BMP085 and use STANDARD mode (default value)
# bmp = BMP085(0x77, debug=True)
bmp = BMP085(0x77, 1)

# To specify a different operating mode, uncomment one of the following:
# bmp = BMP085(0x77, 0)  # ULTRALOWPOWER Mode
# bmp = BMP085(0x77, 1)  # STANDARD Mode
# bmp = BMP085(0x77, 2)  # HIRES Mode
# bmp = BMP085(0x77, 3)  # ULTRAHIRES Mode

#rev = GPIO.RPI_REVISION
#if rev == 2 or rev == 3:
#    bus = smbus.SMBus(1)
#else:
#    bus = smbus.SMBus(0)
bus = smbus.SMBus(2)
temp = bmp.readTemperature()

# Read the current barometric pressure level
pressure = bmp.readPressure()

# To calculate altitude based on an estimated mean sea level pressure
# (1013.25 hPa) call the function as follows, but this won't be very accurate
# altitude = bmp.readAltitude()

# To specify a more accurate altitude, enter the correct mean sea level
# pressure level.  For example, if the current pressure level is 1023.50 hPa
# enter 102350 since we include two decimal places in the integer value
altitude = bmp.readAltitude(101560)
connected=False
server_address = ('crowdais.com', 5114)
while True:
    print("Temperature: %.2f C" % temp)
    print("Pressure:    %.2f hPa" % (pressure / 100.0))
    print("Altitude:    %.2f m" % altitude)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    connected=False
    try: #dont exit if the receiving server is not running yet
            s.connect(server_address)
            connected=True
    except socket.error:
            connected=False
            pass
    #send out  messages with readings
    timestamp = "{:%H%M%S}".format(datetime.now())
    timestamp = datetime.now().strftime("%s")
    jsonmsg = ('["barometric":{"timestamp":'+ timestamp+',"id":'+'7114'+',"temp":'+("%.1f" %temp)+',"pressure":'+ ("%.2f" %( pressure / 100.0))
                   +',"altitude":'+("%.2f" %altitude)+'}]')
    #print jsonmsg 
    if(connected) :
            s.send(jsonmsg+"\r\n")
            s.close()
            connected=False
    time.sleep(60)
