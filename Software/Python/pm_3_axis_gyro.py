#!/usr/bin/python
# vim: ai:ts=4:sw=4:sts=4:et:fileencoding=utf-8
#
# ITG3200 gyroscope control class
#
# Copyright 2013 Michal Belica <devel@beli.sk>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see http://www.gnu.org/licenses/.
#

import smbus
import sys #for args
import socket
import time
from datetime import datetime

import operator
import math
import numpy as np
from array import *
import plotly
from plotly.graph_objs import Scatter, Layout
import json

def showFFT(data,dataTitle,plotit=False):
      Fs = 1.0;  # sampling rate
      Ts = 1.0/Fs; # sampling interval
      t = np.arange(0,60,Ts) # time vector
      n = len(data) # length of the signal
      k = np.arange(n)
      T = n/Fs
      frq = k/T # two sides frequency range
      frq = frq[range(n/2)] # one side frequency range
      Y = np.fft.rfft(data)/n # fft computing and normalization
            #Y = Y[range(n/2)]
      #print Y
      #get max A and f
      if (plotit == False):
            return (Y,np.abs(Y).max(),np.abs(Y).argmax() ) # maximum absolute value,maxF)  
      plotly.offline.plot({
    "data": [Scatter (x=t, y=data)],
    "layout": Layout(title=dataTitle ,
     xaxis=dict(
        autorange=True,
        showgrid=False,
        zeroline=False,
        showline=False,
        autotick=True,
        ticks='outside',
        showticklabels=True,
        title='time (s)'
    ),
    yaxis=dict(
        autorange=True,
        showgrid=False,
        zeroline=False,
        showline=False,
        autotick=True,
        ticks='outside',
        showticklabels=True,
        title='amplitude (degrees)'
    ))},
    filename=dataTitle+'_time.html')

      plotly.offline.plot({
    "data": [Scatter (x=frq, y=abs(Y))],
    "layout": Layout(title=dataTitle, 
     xaxis=dict(
        autorange=True,
        showgrid=False,
        zeroline=False,
        showline=False,
        autotick=True,
        ticks='outside',
        showticklabels=True,
    title='frequency (Hz)'
    ),
    yaxis=dict(
        autorange=True,
        showgrid=False,
        zeroline=False,
        showline=False,
        autotick=True,
        ticks='outside',
        showticklabels=True,
    title='amplitude (degrees)'

    ))},filename=dataTitle+'_freq.html')  
      return (Y,np.abs(Y).max(),np.abs(Y).argmax() ) # maximum absolute value,maxF)     
        


def int_sw_swap(x):
    """Interpret integer as signed word with bytes swapped"""
	xl = x & 0xff
	xh = x >> 8
	xx = (xl << 8) + xh
    return xx - 0xffff if xx > 0x7fff else xx

#http://stackoverflow.com/questions/27909658/json-encoder-and-decoder-for-complex-numpy-arrays
class JsonCustomEncoder(json.JSONEncoder):
    """ <cropped for brevity> """
    def default(self, obj):
        if isinstance(obj, (np.ndarray, np.number)):
            return obj.tolist()
        elif isinstance(obj, (complex, np.complex)):
            return [obj.real, obj.imag]
        elif isinstance(obj, set):
            return list(obj)
        elif isinstance(obj, bytes):  # pragma: py3
            return obj.decode()
        return json.JSONEncoder.default(self, obj)


class SensorITG3200(object):
    """ITG3200 digital gyroscope control class.
    Supports data polling at the moment.
    """
    def __init__(self, bus_nr, addr):
        """ Sensor class constructor
        Params:
            bus_nr .. I2C bus number
            addr   .. ITG3200 device address
        """
        self.bus = smbus.SMBus(bus_nr)
        self.addr = addr
    
    def zero_Calibrate(self, samples, sampleDelayMS):
        gx, gy, gz = sensor.read_data()
        x_offset_temp = 0
        y_offset_temp = 0
        z_offset_temp = 0
        for num in range(0,samples):
            time.sleep(sampleDelayMS/1000)
            gx, gy, gz = sensor.read_data()
            x_offset_temp += gx
            y_offset_temp += gy
            z_offset_temp += gz
  

        self.x_offset = abs(x_offset_temp)/samples
        self.y_offset = abs(y_offset_temp)/samples
        self.z_offset = abs(z_offset_temp)/samples
        if(x_offset_temp > 0):self.x_offset = -self.x_offset
        if(y_offset_temp > 0):self.y_offset = -self.y_offset
        if(z_offset_temp > 0):self.z_offset = -self.z_offset

    def sample_rate(self, lpf, div):
        """Set internal sample rate, low pass filter frequency.
        Sets device parameters DLPF_CFG and SMPLRT_DIV.
        Also sets FS_SEL to 0x03 which is required to initialize the device.
        Params:
            lpf .. (code from the list)
              code   LPF  sample rate
                 0 256Hz  8kHz
                 1 188Hz  1kHz
                 2  98Hz  1kHz
                 3  42Hz  1kHz
                 4  20Hz  1kHz
                 5  10Hz  1kHz
                 6   5Hz  1kHz
            div .. internal sample rate divider (SMPLRT_DIV will be set to div-1)
        """
        if not (lpf >= 0 and lpf <= 0x6):
            raise ValueError("Invalid low pass filter code (0-6).")
        if not (div >= 0 and div <= 0xff):
            raise ValueError("Invalid sample rate divider (0-255).")
        self.bus.write_byte_data(self.addr, 0x15, div-1)
        self.bus.write_byte_data(self.addr, 0x16, 0x18 | lpf)

    def default_init(self):
        """Initialization with default values:
        8kHz internal sample rate, 256Hz low pass filter, sample rate divider 8.
        """
        self.sample_rate(0, 8)
        self.zero_Calibrate(10,100)

    def read_data(self):
        """Read and return data tuple for x, y and z axis
        as signed 16-bit integers.
        """
		gx = int_sw_swap(self.bus.read_word_data(self.addr, 0x1d))
		gy = int_sw_swap(self.bus.read_word_data(self.addr, 0x1f))
		gz = int_sw_swap(self.bus.read_word_data(self.addr, 0x21))
        return (gx, gy, gz)

portnumber = sys.argv[1]
server_address = ('crowdais.com', 5114)
if __name__ == '__main__':
    import time
    sensor = SensorITG3200(2, 0x68) # update with your bus number and address
    sensor.default_init()
gxsum=0;gysum=0;gzsum=0;gxavg=0;gyavg=0;gzavg=0;gxmax=0;gxmin=0;gymax=0;gymin=0;gzmax=0;gzmin=0;
count=1; 
connected=False
pitch_array = []
roll_array = []
turn_array = []
while True:
    gx, gy, gz = sensor.read_data()
    gx =(gx+sensor.x_offset)/14.375
    gy = (gy+sensor.y_offset)/14.375
    gz= (gz+sensor.z_offset)/14.375
    pitch_array.append(gx)
    roll_array.append(gy)
    turn_array.append(gz)
    print ("%.2f" %(gx)), ("%.2f" %(gy)), ("%.2f" %(gz)) , "deg/s"
    gxmax = max(gxmax,gx)
    gymax = max(gymax,gy)
    gzmax = max(gzmax,gz)
    gxmin = min(gxmin,gx)
    gymin = min(gymin,gy)
    gzmin = min(gzmin,gz)
    gxsum=gxsum+gx
    gysum=gysum+gy
    gzsum=gzsum+gz
    if ((count % 60) == 0):
        gxavg=gxsum/count
        gyavg=gysum/count
        gzavg=gzsum/count
        timestamp = datetime.now().strftime("%s")
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        connected=False
        try: #dont exit if the receiving server is not running yet
            s.connect(server_address)
            connected=True
        except socket.error:
            connected=False
            pass
        jsonmsg = ('["gyro":{"timestamp":'+ timestamp+',"id":'+str(portnumber)
                   +',"gxmax":'+("%.2f" %gxmax)+',"gymax":'+ ("%.2f" %gymax)+',"gzmax":'+ ("%.2f" %gzmax)
                   +',"gxmin":'+("%.2f" %gxmin)+',"gymin":'+ ("%.2f" %gymin)+',"gzmin":'+ ("%.2f" %gzmin)
                   +',"gxavg":'+("%.2f" %gxavg)+',"gyavg":'+ ("%.2f" %gyavg)+',"gzavg":'+ ("%.2f" %gzavg)
                   +'}]')
        #print jsonmsg 
        pitchFFT,pitchMaxA,pitchMaxF=showFFT(pitch_array,"Pitch",True)
        pitchFFTList={'pitchFFT':pitchFFT}
        pitchJson= json.dumps(pitchFFTList, cls=JsonCustomEncoder)
            
        jsonmsg = ('["gyro_pitch_fft":{"timestamp":'+ timestamp+',"id":'+str(portnumber)+',"pma":'+ str(pitchMaxA) +',"pmf":'+ str(pitchMaxF) +',"pfft":'+pitchJson +'}]' )
        if(connected) :
            s.send(jsonmsg+"\r\n")
        rollFFT,rollMaxA,rollMaxF=showFFT(roll_array,"Roll")
        rollFFTList={'rollFFT':rollFFT}
        rollJson= json.dumps(rollFFTList, cls=JsonCustomEncoder)
            
        jsonmsg = ('["gyro_roll_fft":{"timestamp":'+ timestamp+',"id":'+str(portnumber)+',"rma":'+ str(rollMaxA) +',"rmf":'+ str(rollMaxF) +',"rfft":'+rollJson +'}]' )
        if(connected) :
            s.send(jsonmsg+"\r\n")
        
        turnFFT,turnMaxA,turnMaxF=showFFT(turn_array,"Turn")
        turnFFTList={'turnFFT':turnFFT}
        turnJson= json.dumps(turnFFTList, cls=JsonCustomEncoder)
            
        jsonmsg = ('["gyro_turn_fft":{"timestamp":'+ timestamp+',"id":'+str(portnumber)+',"tma":'+ str(turnMaxA) +',"tmf":'+ str(turnMaxF) +',"tfft":'+turnJson +'}]' )
        if(connected) :
            s.send(jsonmsg+"\r\n")
        gxsum=0;gysum=0;gzsum=0;gxavg=0;gyavg=0;gzavg=0;gxmax=0;gxmin=0;gymax=0;gymin=0;gzmax=0;gzmin=0;
        if(connected) :
            s.send(jsonmsg+"\r\n")
            s.close()
            connected=False
        pitch_array = []
        roll_array = []
        turn_array = []
        count=0
    count=count+1
    time.sleep(1)
