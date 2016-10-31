#!/usr/bin/python

import smbus

#import grovepi
from grove_i2c_barometic_sensor_BMP280 import BMP280

# ===========================================================================
# Example Code
# ===========================================================================

# Initialise the BMP280 and use STANDARD mode (default value)
# bmp = BMP280(0x77, debug=True)
bmp = BMP280(0x77, 0)

# To specify a different operating mode, uncomment one of the following:
# bmp = BMP280(0x77, 0)  # ULTRALOWPOWER Mode
# bmp = BMP280(0x77, 1)  # STANDARD Mode
# bmp = BMP280(0x77, 2)  # HIRES Mode
# bmp = BMP280(0x77, 3)  # ULTRAHIRES Mode

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

print("Temperature: %.2f C" % temp)
print("Pressure:    %.2f hPa" % (pressure / 100.0))
print("Altitude:    %.2f m" % altitude)
