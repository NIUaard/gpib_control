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


Nsamp=5 # number of point to record
Nstep=40 # number of point to record
Vmin=200
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
usb_port.x.write('++addr 14')
int_range = 2e-7
usb_port.x.write("*RST")                   
time.sleep(0.50)
usb_port.x.write("SYST:ZCH OFF")
time.sleep(0.50)
#range_comm = str('\'SENS:CURR:RANG')+str(' ')+str(int_range)+str('\'')
usb_port.x.write('SENS:CURR:RANG 2e-7')

time.sleep(0.50)
usb_port.x.write("SYST:AZER:STAT OFF") 
time.sleep(0.50)


fh = open(filename, 'w')

command = str('VSET') + str(Vmin)
usb_port.x.write('++addr 13')
usb_port.x.write(command)
usb_port.x.write('HVON')
m = usb_port.x.query_ascii_values('VOUT?')
usb_port.x.write('++addr 14')
time.sleep(1.0)



for j in range(Nstep):
   voltageoff = str('HVOF') #command to reset the voltage to zero after each step 
   command = str('VSET') + str(voltage_set[j])
   usb_port.x.write('++addr 13')
   usb_port.x.write(command)
   usb_port.x.write('HVON')
   usb_port.x.write('++addr 14')
   time.sleep(3.0) #increased the waiting time to wait for V to go to zero and V_set
   
   for k in range(Nsamp):
      	 
      tmp=usb_port.x.query_ascii_values('read?',separator='A',container=np.array)
      usb_port.x.write('++addr 13')
      tmpv = usb_port.x.query_ascii_values('VOUT?',separator='A',container=np.array)
      usb_port.x.write('++addr 14')
      current[k]=float(tmp[0])
      voltage[k] = float(tmpv) 
      print(" ",k," ","  current", current[k], "voltage",voltage[k])
      time.sleep(0.5)
      fh.write(str(current[k]) + '\t' + str(voltage[k]) + '\n')
      #usb_port.x.write('++addr 13')
#   usb_port.x.write(voltageoff) #line 1 :remove the next 4 lines if you do not want to the voltage to go back to zero at each step 
#   time.sleep(6.0)# line 2
#   d = usb_port.x.query('VOUT?') #line 3
#   print(d)# line 4




usb_port.x.write('HVOF')
fh.close()
