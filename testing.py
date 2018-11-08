'''
I-V recorder
PP 07-11-2018
usage iv_recorder  
'''
# Added a command to read the real voltage (line 78-80) : 16-07-2018 by Osama Mohsen
# Added a new path to sort measurments by date in the Documents 
from __future__ import print_function #Python 2.7 compatibility
import gpib
import time
import numpy as np
import os
###############################################


Nsamp=100 # number of point to record
Nstep=40 # number of point to record
Vmin=2000
Vmax=8000
dir_path = '/usr/local/home/labuser/Documents/'
rootname = 'iv_monitoring'


###############################################


usb_port=gpib.Control()

timestamp = time.strftime("D%Y%m%dT%H%M%S")

newdir = time.strftime("%y-%B-%d")

path = dir_path+str('/')+str(newdir)

if not os.path.isdir(path):
   os.makedirs(path)

dir_path = path

filename  = dir_path+str('/')+rootname+'_'+timestamp

Npts=Nsamp*Nstep
chart_time = np.zeros((Npts))
current    = np.zeros((Npts))
voltage    = np.zeros((Npts))
voltage_set= np.linspace(Vmin, Vmax, Nstep+1)


usb_port=gpib.Control()

int_range = 2e-7
usb_port.x.write("*RST")                   
time.sleep(0.50)
usb_port.x.write("SYST:ZCH OFF")
time.sleep(0.50)
range_comm = str('\'SENS:CURR:RANG')+str(' ')+str(int_range)+str('\'')
usb_port.x.write(range_comm)
time.sleep(0.50)
usb_port.x.write("SYST:AZER:STAT OFF") 
time.sleep(0.50)


command = str('VSET') + str(Vmin)
usb_port.x.write('++addr 13')
usb_port.x.write(command)
usb_port.x.write('HVON')
m = usb_port.x.query_ascii_values('VOUT?')
print(m)

for i in range(Nsamp):
    tmp=usb_port.x.query_ascii_values('read?',separator='A',container=np.array)
    print(tmp[0])


