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


###############################################


Nsamp=100 # number of point to record per voltage step
Nstep=101 # number of point to record
Vmin=7000
Vmax=11000
dir_path = '/usr/local/home/labuser/Documents/'
rootname = 'iv_monitoring'
i_recoring = False # to set the voltage at Vmax and record the current for t points 
t  = 10000 # time for constant v measurment  
###############################################
cathode_name = 'MIT_cathode'
localdir = dir_path+cathode_name
if not os.path.isdir(localdir):
   os.makedirs(localdir)

usb_port=gpib.Control()

timestamp = time.strftime("D%Y%m%dT%H%M%S")

newdir = time.strftime("%y-%B-%d")

path = localdir+str('/')+str(newdir)

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
int_range = ['SENS:CURR:RANG 2e-8','SENS:CURR:RANG 2e-7','SENS:CURR:RANG 2e-6','SENS:CURR:RANG 2e-5','SENS:CURR:RANG 2e-4','SENS:CURR:RANG 2e-3','SENS:CURR:RANG 2e-2']
usb_port.x.write('++addr 14')
usb_port.x.write("*RST")                   
time.sleep(0.50)
usb_port.x.write("SYST:ZCH OFF")
time.sleep(0.50)
range_comm = str('\'SENS:CURR:RANG')+str(' ')+int_range[0]+str('\'')
usb_port.x.write('SENS:CURR:RANG 2e-8')
time.sleep(0.50)
usb_port.x.write("SYST:AZER:STAT OFF") 
time.sleep(0.50)
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


fl.write('IV-measurment at ' + str(newdir) +': '+ str(timestamp) + ' from ' + str(Vmin) + 'to ' + str(Vmax) + 'with number of points per step size ' + str(Nsamp) + '\n')  

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
      if current[i] > 10.0: # In case of overflow, in case you need constant range, comment the next 11 lines
         print(current[i],l) 
         current[i] = 0.0
         fl.write('Range increased at ' + str(voltage[i]) + '\t'+ str(i)+ 'from '+ str(int_range[l-1]) + 'to ' + str(int_range[l])+ '\n')
         print('increasing the range')
         usb_port.x.write(int_range[l]) #changing the range to the next avalaible option from int_range
         l = l +1 #increase l to get the next value for the range again
         time.sleep(5.0)
	 m = usb_port.x.query('SENS:CURR:RANG?') #confirm the range change
         print(m)
      else:
         pass

      print(i," ",k," ","  current", current[i], "voltage",voltage[i], ' source_current', vcurrent[i])
      time.sleep(1.0)
      fh.write(str(chart_time[i]) + '\t' + str(current[i]) + '\t' + str(voltage[i]) + '\t' + str(vcurrent[i])+ '\n')
      i = i+1 

#constant v measurment, same as above expect no change in V. V is set to Vmax
chart_time = np.zeros((t))

if i_recoring == True:
   usb_port.x.write('++addr 13')
   command = str('VSET') + str(Vmax)
   usb_port.x.write(command)
   i = 0
   fl.write('Constant V at '+ str(Vmax)+ ' for '+str(t) +  ' points measurment')
   for k in range(t):
      
      if i==0:
         start_time = time.time()
         chart_time[i]=0.
      else:
         chart_time[i]=time.time()-start_time
      usb_port.x.write('++addr 13')
      time.sleep(0.5)   
      tmpv = usb_port.x.query_ascii_values('VOUT?',separator='A',container=np.array)
      tmpi = usb_port.x.query_ascii_values('IOUT?',separator='A',container=np.array)
      voltage = float(tmpv) 
      vcurrent = float(tmpi)
      usb_port.x.write('++addr 14')
      time.sleep(0.5)   
      tmp=usb_port.x.query_ascii_values('read?',separator='A',container=np.array)
      current=float(tmp[0])

      if current > 10.0:
         print(current,l) 
         current = vcurrent
         fl.write('Range increased at ' + str(voltage[i]) + '\t'+ str(i)+ 'from '+ str(int_range[l-1]) + 'to ' + str(int_range[l])+ '\n')
         print('increasing the range')
         usb_port.x.write(int_range[l])
         l = l +1
         time.sleep(5.0)
	 m = usb_port.x.query('SENS:CURR:RANG?')
         print(m)
      else:
         pass

      print(i,"  current ", current, ' voltage set ',Vmax, " voltage ",voltage, ' Source current ',vcurrent)
      fi.write(str(chart_time[i]) + '\t' + str(current) + '\t' + str(voltage) + '\t' + str(vcurrent) +'\n')
      i = i+1
      
else:
    pass
   
usb_port.x.write('++addr 13')
usb_port.x.write('HV OF')
fl.write('Measurment is over!')
fl.close()
fh.close()
fi.close()



