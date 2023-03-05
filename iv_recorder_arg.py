'''
I-V recorder, with an option for stability measurment
PP 11-JUL-2018, rev. 04-MAR-2023
'''
# 14-OCT--2018 
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


############################################### parser only Vmin and Vmax are required

parser = argparse.ArgumentParser(description='records I-V curve V. 11-09-2018')

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
parser.add_argument('--PaScale', type=str, nargs='?', default='2e-5', 
                    help='range for pAmmeter: 2e-7 2e-6 2e-5 2e-4 2e-3')
parser.add_argument('--ProjectDir', type=str, nargs='?',default='None', 
                    help='create a project dir in which the files are to be stored at, should be between single quote, if not added, data are sorted based on the date and time in the Documents Directory')
parser.add_argument('--Comment', type=str, nargs='?',default='no comment', 
                    help='a text comment that will be added to log file header should be between single quote ')
		    
# Switch
parser.add_argument('--cycle', action='store_true',
                    help='do the cycle Vmin->Vmax->Vmin')
parser.add_argument('--display', action='store_true',
                    help='display data during the scan')

args = parser.parse_args()

print(args)

############################################### initialize file and directory
display = False


Vmin    = args.Vmin
Vmax    = args.Vmax
Nsamp   = args.Nsamp     # number of point to record per voltage step
Nstep   = args.Nstep     # number of point to record
PaScale = args.PaScale   # picoAmmeter scale 
display = args.display   # live plot flag
cycle   = args.cycle     # ramp down FLAG (then 2*Nstep are taken)

projectdir = args.ProjectDir
if projectdir == 'None':
   pass
else:
    dir_path = '/usr/local/home/labuser/Documents/'+str(projectdir)
    

usb_port=gpib.Control()

if (display):
    import matplotlib.pyplot as plt 

int_range = 'SENS:CURR:RANG '+PaScale
print ("Pammeter range=", int_range)

# directory & rootname:

#dir_path = '/usr/local/home/labuser/Documents/'
rootname = 'ivScan_Vmin_'+str(Vmin)+'Vmax_'+str(Vmax)+'_Nstep_'+str(Nstep)+'_Nsamp_'+str(Nsamp)+'_PaScale_'+str(PaScale) 

timestamp = time.strftime("%Y%m%d-%H%M%S")

path = dir_path+str('/')

if not os.path.isdir(path):
   os.makedirs(path)
dir_path = path
filename  = dir_path+str('/')+rootname+'_'+timestamp
print(filename)

data_file = filename+'.data'       # data file
stat_file = filename+'.stat'       # processed file (mean RMS)
log_file  = filename+'.log'        # log file (input parameters and other info)


############################################### initialize all the variables
Npts=Nsamp*Nstep
if (cycle):
   Npts=Npts*2
   
chart_time  = np.zeros((Npts))
current     = np.zeros((Npts))
voltage     = np.zeros((Npts))
vcurrent    = np.zeros((Npts)) 
voltage_set = np.linspace(Vmin, Vmax, Nstep)

record_status(log_file, args)
############################################### initialize usb Port connection

# usb_port=gpib.Control
time.sleep(1.0)
usb_port.x.write('++addr 14')          # connect to Picoammeter
usb_port.x.write("*RST")               # return Picoammeter to default values          
time.sleep(0.50)
usb_port.x.write("SYST:ZCH OFF")       # turn zero check off 
time.sleep(0.50)
# set current sensitivity range
range_comm = str('\'SENS:CURR:RANG')+str(' ')+int_range[0]+str('\'')
usb_port.x.write(int_range)
time.sleep(0.50)
usb_port.x.write("SYST:AZER:STAT OFF") # turn auto-zero off 
time.sleep(0.50)
usb_port.x.write("*CLS")               # clear status                

# wait for the picoammeter to be ready
time.sleep(5.0)


usb_port.x.write('++addr 13')          # connect to HVPS
usb_port.x.write("*CLS")               # clear status 
command = str('VSET') + str(Vmin)      
# set voltage 
usb_port.x.write(command) 
usb_port.x.write('HVON')               # turn on HVPS


if (display):
   plt.ion()

###################################################### loop on measurement 

i=0

record_status(log_file, 'ramp up')

for j in range(Nstep):
   usb_port.x.write('++addr 13')       # connect to HVPS
   # set voltage 
   command = str('VSET') + str(voltage_set[j])
   usb_port.x.write(command)
   usb_port.x.write('HVON')
   usb_port.x.write('++addr 14')       # connect to Picoammeter
   time.sleep(1.0)                   
   tmp=usb_port.x.query_ascii_values('read?',separator='A',container=np.array)
   
   m = usb_port.x.query('SENS:CURR:RANG?')    # query current current sensitivity
   record_status(log_file, 'pA range = '+str(m))
   
   for k in range(Nsamp):
      
      if i==0:
         start_time = time.time()
         chart_time[i]=0.
      else:
         chart_time[i]=time.time()-start_time

      time.sleep(0.5) 
      # query current value from picoAmmeter
      tmp=usb_port.x.query_ascii_values('read?',separator='A',container=np.array)
      usb_port.x.write('++addr 13')       # connect to HVPS
      tmpi = usb_port.x.query_ascii_values('IOUT?',separator='A',container=np.array)
      tmpv = usb_port.x.query_ascii_values('VOUT?',separator='A',container=np.array)
      usb_port.x.write('++addr 14')

      current[i]  = float(tmp[0])
      voltage[i]  = float(tmpv) 
      vcurrent[i] = float(tmpi)

# display window
      if (display):
          live_display(voltage, current,i,'b')
	  
      time.sleep(0.3)
#
      print(i,"\t",k,"\t voltage=",voltage[i],"\t current=", current[i], "\t source_current=", vcurrent[i])


# record raw and processed data
      record_data(data_file, str(chart_time[i]) + '\t' + str(voltage[i]) + '\t' \
             + str(current[i]) + '\t' + str(vcurrent[i])+'\n')
# make an histogram of data?
#      if histo:
          
      i = i+1 

   record_data(stat_file, str(np.mean(voltage[i-Nsamp:i]))+ '\t' + str(np.mean(current[i-Nsamp:i])) \
            + '\t' +  str(np.std(current[i-Nsamp:i])) + '\t' +  str(np.ptp(current[i-Nsamp:i])) + '\n')      

if (cycle):   # this is the ramping down loop
   record_status(log_file, 'ramp down')

   for j in range(Nstep):
      usb_port.x.write('++addr 13')
      command = str('VSET') + str(voltage_set[Nstep-j-1])
      usb_port.x.write(command)
      usb_port.x.write('HVON')
      usb_port.x.write('++addr 14')
      time.sleep(1.0) #increased the waiting time to wait for V to go to zero and V_set
      tmp=usb_port.x.query_ascii_values('read?',separator='A',container=np.array)
   
      m = usb_port.x.query('SENS:CURR:RANG?')
      record_status(log_file, 'pA range = '+str(m))
   
      for k in range(Nsamp):
      
         chart_time[i]=time.time()-start_time

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
             live_display(voltage, current,i,'r')
	  
         time.sleep(1.0)
#
         print(i,"\t",k,"\t voltage=",voltage[i],"\t current=", current[i], "\t source_current=", vcurrent[i])


# record raw and processed data
         record_data(data_file, str(chart_time[i]) + '\t' + str(voltage[i]) + '\t' \
	        + str(current[i]) + '\t' + str(vcurrent[i])+ '\n')
# make    an histogram of data?
#      if histo:
          
         i = i+1 

      record_data(stat_file, str(np.mean(voltage[i-Nsamp:i]))+ '\t' + str(np.mean(current[i-Nsamp:i])) \
                + '\t' +  str(np.std(current[i-Nsamp:i])) + '\t' +  str(np.ptp(current[i-Nsamp:i])) + '\n')      


if (display):
   plt.text(0.9, 0.9,timestamp, ha='center', va='center', transform=ax.transAxes, fontsize=12)
   plt.xlabel(r'applied voltage (V)')
   plt.ylabel(r'current (A)')
   plt.tight_layout()
   
   
record_status(log_file, 'total number of points = '+str(i))
record_status(log_file, 'done with scan')
   
usb_port.x.write('++addr 13')
usb_port.x.write('HV OF')
record_status(log_file, 'HVPS turned off')



