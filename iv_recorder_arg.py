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
import argparse
from util import *

############################################### parser only Vmin adn Vmax are required

parser = argparse.ArgumentParser(description='records I-V curse')

# Required positional argument
parser.add_argument('Vmin', type=float,
                    help='minimum voltage (Volt)')
parser.add_argument('Vmax', type=float,
                    help='maximum voltage (Volt)')
# Optional positional argument
parser.add_argument('--Nstep', type=int, nargs='?',default=21, 
                    help='number of voltage setpoints (default=21)')
parser.add_argument('--Nsamp', type=int, nargs='?', default=5, 
                    help='number of samples at each voltage setpoints (default=5)')
# Switch
parser.add_argument('--cycle', action='store_true',
                    help='do the cycle Vmin->Vmax->0')
parser.add_argument('--display', action='store_true',
                    help='display data during the scan')

args = parser.parse_args()

############################################### initialize all the variables

Vmin=args.Vmin
Vmax=args.Vmax
Nsamp=args.Nsamp   # number of point to record per voltage step
Nstep=args.Nstep   # number of point to record

# directory & rootname:
 
dir_path = '/usr/local/home/labuser/Documents/'
rootname = 'i_vs_v'

data_file = filename+'.data'       # data file
stat_file = filename+'.stat','w')  # processed file (mean RMS)
log_file  - filename+'.log', 'w')  # log file (input parameters and other info)

timestamp = time.strftime("D%Y%m%dT%H%M%S")

newdir = time.strftime("%y-%B-%d")

path = dir_path+str('/')+str(newdir)

if not os.path.isdir(path):
   os.makedirs(path)

dir_path = path

filename  = dir_path+str('/')+rootname+'_'+timestamp
print(filename)

Npts=Nsamp*Nstep
chart_time  = np.zeros((Npts))
current     = np.zeros((Npts))
voltage     = np.zeros((Npts))
vcurrent    = np.zeros((Npts)) 
voltage_set = np.linspace(Vmin, Vmax, Nstep)

record_status(log_file, args)
############################################### initialize usb Port connection

usb_port=gpib.Control()
# set of range options
int_range = ['SENS:CURR:RANG 2e-7','SENS:CURR:RANG 2e-6','SENS:CURR:RANG 2e-5','SENS:CURR:RANG 2e-4','SENS:CURR:RANG 2e-3','SENS:CURR:RANG 2e-2']
usb_port.x.write('++addr 14')
usb_port.x.write("*RST")                   
time.sleep(0.50)
usb_port.x.write("SYST:ZCH OFF")
time.sleep(0.50)
range_comm = str('\'SENS:CURR:RANG')+str(' ')+int_range[0]+str('\'')
usb_port.x.write('SENS:CURR:RANG 2e-5')
time.sleep(0.50)
usb_port.x.write("SYST:AZER:STAT OFF") 
time.sleep(0.50)
m = usb_port.x.query('SENS:CURR:RANG?')
print(m)
# wait for the picoammeter to be ready
time.sleep(5.0)


usb_port.x.write('++addr 13')
command = str('VSET') + str(Vmin)
usb_port.x.write(command)
usb_port.x.write('HVON')
m = usb_port.x.query_ascii_values('VOUT?')



if (PLOT==1):
   plt.ion()

xaxis = []
yaxis = []
# l should be equal to the current range + 1 from int_range list
l=1
i=0
for j in range(Nstep):
   usb_port.x.write('++addr 13')
   command = str('VSET') + str(voltage_set[j])
   usb_port.x.write(command)
   usb_port.x.write('HVON')
   time.sleep(1.0) #increased the waiting time to wait for V to go to zero and V_set
   
   if i==0:
      start_time = time.time()
      chart_time[i]=0.
   else:
         chart_time[i]=time.time()-start_time

   for k in range(Nsamp):
      
      time.sleep(1.0) #increased the waiting time to wait for V to go to zero and V_set

      tmp=usb_port.x.query_ascii_values('read?',separator='A',container=np.array)
      usb_port.x.write('++addr 13')
      tmpi = usb_port.x.query_ascii_values('IOUT?',separator='A',container=np.array)
      tmpv = usb_port.x.query_ascii_values('VOUT?',separator='A',container=np.array)
      usb_port.x.write('++addr 14')
      current[i]  = float(tmp[0])
      voltage[i]  = float(tmpv) 
      vcurrent[i] = float(tmpi)

# display window
      if (display):
          live_display(voltage, current,i)
	  
      time.sleep(1.0)
#
      print(i," ",k," ","  current", current[i], "voltage",voltage[i], ' source_current', vcurrent[i])


# record raw and processed data
      record_data(data_file, str(chart_time[i]) + '\t' + str(voltage[i]) + '\t' + str(current[i]) + '\t' + str(vcurrent[i])+ '\n')
      record_data(stat_file, str(np.mean(voltage[i-Nsamp:i]))+ '\t' + str(np.mean(current[i-Nsamp:i])) + '\t' +  str(np.ptp(current[i-Nsamp:i])) + '\n')      
# make an histogram of data?
#      if histo:
          
      i = i+1 


if cycle:   # this is the ramping down loop


   
usb_port.x.write('++addr 13')
usb_port.x.write('HV OF')



