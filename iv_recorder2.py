'''
I-V recorder
PP 07-11-2018
usage iv_recorder  
'''
from __future__ import print_function #Python 2.7 compatibility
import gpib
import time
import numpy as np

###############################################


Nsamp=100 # number of point to record
Nstep=65 # number of point to record
Vmin=2000
Vmax=12000
dir_path = '/usr/local/home/labuser/Documents/'
rootname = 'iv_monitoring'


###############################################

usb_port=gpib.Control()

timestamp = time.strftime("D%Y%m%dT%H%M%S")

filename  = dir_path+rootname+'_'+timestamp

Npts=Nsamp*Nstep
chart_time = np.zeros((Npts))
current    = np.zeros((Npts))
voltage    = np.zeros((Npts))
voltage_set= np.linspace(Vmin, Vmax, Nstep+1)


time.sleep(0.5)

fh = open(filename, 'w')

command = str('VSET') + str(Vmin)
usb_port.x.write('++addr 13')
usb_port.x.write(command)
usb_port.x.write('HVON')
m = usb_port.x.query_ascii_values('VOUT?')


i=0
for j in range(Nstep):
   command = str('VSET') + str(voltage_set[j])
   usb_port.x.write('++addr 13')
   usb_port.x.write(command)
   usb_port.x.write('HVON')
   time.sleep(0.4)
   
   for k in range(Nsamp):
      
      if i==0:
         start_time = time.time()
         chart_time[i]=0.
      else:
         chart_time[i]=time.time()-start_time
	 
      print(i," ",k," ","  current", current[i], "voltage",voltage[i])
      time.sleep(0.5)
      fh.write(str(chart_time[i]) + '\t' + str(current[i]) + '\t' + str(voltage[i]) + '\n')
      i=i+1

fh.close()
 

