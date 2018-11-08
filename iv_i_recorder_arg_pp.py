'''
I-V recorder, with an option for stability measurment
PP 07-11-2018
'''
#10-14-2018 
# Added a command to read the real voltage (line 78-80) : 16-07-2018 by Osama Mohsen
# Added a new path to sort measurments by date in the Documents
# Added a log file, and lines to change the range in the picoamm
# Added a constant v measurment option 
from __future__ import print_function #Python 2.7 compatibility
import gpib
import time
import numpy as np
import os
import sys

###############################################
arg    = sys.argv 

PLOT=0   # live plot turned on
if PLOT==1:
   import matplotlib.pyplot as plt 

Nsamp=int(arg[1]) # number of point to record per voltage step
Nstep=int(arg[2]) # number of point to record
Vmin=2000
Vmax=5000
dir_path = '/usr/local/home/labuser/Documents/'
rootname = 'iv_monitoring'
i_recoring = False # to set the voltage at Vmax and record the current for t points 
t  = 10000 # time for constant v measurment  
###############################################

usb_port=gpib.Control()

timestamp = time.strftime("D%Y%m%dT%H%M%S")

newdir = time.strftime("%y-%B-%d")

path = dir_path+str('/')+str(newdir)

if not os.path.isdir(path):
   os.makedirs(path)

dir_path = path

filename  = dir_path+str('/')+rootname+'_'+timestamp
print(filename)
Npts=Nsamp*Nstep
chart_time = np.zeros((Npts))
current    = np.zeros((Npts))
voltage    = np.zeros((Npts))
vcurrent   = np.zeros((Npts)) 
voltage_set= np.linspace(Vmin, Vmax, Nstep)


usb_port=gpib.Control()
# set of range options
int_range = ['SENS:CURR:RANG 2e-7','SENS:CURR:RANG 2e-6','SENS:CURR:RANG 2e-5','SENS:CURR:RANG 2e-4','SENS:CURR:RANG 2e-3','SENS:CURR:RANG 2e-2']
usb_port.x.write('++addr 14')
usb_port.x.write("*RST")                   
time.sleep(0.10)
usb_port.x.write("SYST:ZCH OFF")
time.sleep(0.10)
range_comm = str('\'SENS:CURR:RANG')+str(' ')+int_range[0]+str('\'')
usb_port.x.write('SENS:CURR:RANG 2e-5')
time.sleep(0.10)
usb_port.x.write("SYST:AZER:STAT OFF") 
time.sleep(0.10)
m = usb_port.x.query('SENS:CURR:RANG?')
print(m)

fh = open(filename, 'w')

fl = open(filename+'.LOG','w')

fi = open(filename+'.i_r','w')

command = str('VSET') + str(Vmin)
usb_port.x.write('++addr 13')
usb_port.x.write(command)
usb_port.x.write('HVON')
m = usb_port.x.query_ascii_values('VOUT?')


fl.write('IV-measurement at ' + str(newdir) +': '+ str(timestamp) + ' from ' + str(Vmin) + 'to ' + str(Vmax) + 'with number of points per step size ' + str(Nsamp) + '\n')  

if (PLOT==1):
   plt.ion()

xaxis = []
yaxis = []
# l should be equal to the current range + 1 from int_range list
l=1
i=0
for j in range(Nstep):
   voltageoff = str('HVOF') #command to reset the voltage to zero after each step 
   command = str('VSET') + str(voltage_set[j])
   usb_port.x.write('++addr 13')
   usb_port.x.write(command)
   usb_port.x.write('HVON')
   usb_port.x.write('++addr 14')
   time.sleep(1.0) #increased the waiting time to wait for V to go to zero and V_set
   
   for k in range(Nsamp):
      
      time.sleep(1.0) #increased the waiting time to wait for V to go to zero and V_set
      if i==0:
         start_time = time.time()
         chart_time[i]=0.
      else:
         chart_time[i]=time.time()-start_time

      tmp=usb_port.x.query_ascii_values('read?',separator='A',container=np.array)
      usb_port.x.write('++addr 13')
      tmpi = usb_port.x.query_ascii_values('IOUT?',separator='A',container=np.array)
      tmpv = usb_port.x.query_ascii_values('VOUT?',separator='A',container=np.array)
      usb_port.x.write('++addr 14')
      current[i]=float(tmp[0])
      voltage[i] = float(tmpv) 
      vcurrent[i] = float(tmpi)

      if (PLOT==1):
         if (i==0):
	    n=0
         else:
	    n=np.arange(i)
         plt.scatter (voltage[i], current[i])
	 plt.ylim(np.min(current[n]),np.max(current[n])*1.05)
	 plt.xlim(np.min(voltage[n]),np.max(voltage[n])*1.05)
	 plt.show()
	 plt.pause(0.0001)
      print(i," ",k," ","  current", current[i], "voltage",voltage[i], ' source_current', vcurrent[i])
      time.sleep(1.0)
      fh.write(str(chart_time[i]) + '\t' + str(current[i]) + '\t' + str(voltage[i]) + '\t' + str(vcurrent[i])+ '\n')
      i = i+1 

   
usb_port.x.write('++addr 13')
usb_port.x.write('HV OF')
fl.write('Measurment is over!')
fl.close()
fh.close()
fi.close()



