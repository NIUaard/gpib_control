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


Nsamp=100 # number of point to record per voltage step
Nstep=500 # number of point to record
Vmin=4000 
Vmax=11000
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
print(filename)
Npts=Nsamp*Nstep
chart_time = np.zeros((Npts))
current    = np.zeros((Npts))
voltage    = np.zeros((Npts))
vcurrent   = np.zeros((Npts)) 
voltage_set= np.linspace(Vmin, Vmax, Nstep+1)


usb_port=gpib.Control()

int_range = ['SENS:CURR:RANG 2e-7','SENS:CURR:RANG 2e-6','SENS:CURR:RANG 2e-5','SENS:CURR:RANG 2e-4','SENS:CURR:RANG 2e-3','SENS:CURR:RANG 2e-2']
usb_port.x.write('++addr 14')
usb_port.x.write("*RST")                   
time.sleep(0.50)
usb_port.x.write("SYST:ZCH OFF")
time.sleep(0.50)
range_comm = str('\'SENS:CURR:RANG')+str(' ')+int_range[0]+str('\'')
usb_port.x.write('SENS:CURR:RANG 2e-7')
time.sleep(0.50)
usb_port.x.write("SYST:AZER:STAT OFF") 
time.sleep(0.50)
m = usb_port.x.query('SENS:CURR:RANG?')
print(m)

fh = open(filename, 'w')

fl = open(filename+'.LOG','w')


command = str('VSET') + str(Vmin)
usb_port.x.write('++addr 13')
usb_port.x.write(command)
usb_port.x.write('HVON')
m = usb_port.x.query_ascii_values('VOUT?')


fl.write('IV-measurment at ' + str(newdir) +': '+ str(timestamp) + ' from ' + str(Vmin) + 'to ' + str(Vmax) + 'with number of points per step size ' + str(Nsamp) + '\n')  



l=1
i=0
for j in range(Nstep):
   voltageoff = str('HVOF') #command to reset the voltage to zero after each step 
   command = str('VSET') + str(voltage_set[j])
   usb_port.x.write('++addr 13')
   usb_port.x.write(command)
   usb_port.x.write('HVON')
   usb_port.x.write('++addr 14')
   time.sleep(5.0) #increased the waiting time to wait for V to go to zero and V_set
   
   for k in range(Nsamp):
      
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
      if current[i] > 10.0:
         print(current[i],l) 
         current[i] = 0.0
         fl.write('Range increased at ' + str(voltage[i]) + '\t'+ str(i)+ 'from '+ str(int_range[l-1]) + 'to ' + str(int_range[l])+ '\n')
         print('increasing the range')
         usb_port.x.write(int_range[l])
         l = l +1
         time.sleep(5.0)
	 m = usb_port.x.query('SENS:CURR:RANG?')
         print(m)
      else:
         pass

      print(i," ",k," ","  current", current[i], "voltage",voltage[i], ' source_current', vcurrent[i])
      time.sleep(1.0)
      fh.write(str(chart_time[i]) + '\t' + str(current[i]) + '\t' + str(voltage[i]) + '\t' + str(vcurrent[i])+ '\n')
      #usb_port.x.write('++addr 13')
      i = i+1 
#   usb_port.x.write(voltageoff) #line 1 :remove the next 4 lines if you do not want to the voltage to go back to zero at each step 
#   time.sleep(6.0)# line 2
#   d = usb_port.x.query('VOUT?') #line 3
#   print(d)# line 4
usb_port.x.write('++addr 13')
usb_port.x.write('HV OF')
fl.write('Measurment is over!')
fl.close
fh.close()

