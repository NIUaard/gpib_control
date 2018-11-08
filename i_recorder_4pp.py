'''
I-V recorder
PP 07-11-2018
usage iv_recorder 

updated:
-PP, 9/12/2018: now records HVPS current + implements autoscale feature for the pAmp 
'''
from __future__ import print_function #Python 2.7 compatibility
import gpib
import time
import numpy as np
import os 

###############################################


Npts=45000
Vmin=3500
dir_path = '/usr/local/home/labuser/Documents/'
rootname = 'i_monitoring'


###############################################

newdir = time.strftime("%y-%B-%d")
path = dir_path+str('/')+str(newdir)

if not os.path.isdir(path):
   os.makedirs(path)

dir_path = path

timestamp = time.strftime("D%Y%m%dT%H%M%S")

filename  = dir_path+str('/')+rootname+'_'+timestamp

usb_port=gpib.Control()

usb_port.x.write('++addr 14')

usb_port.x.write("*RST")                   
time.sleep(0.50)
usb_port.x.write("SYST:ZCH OFF")
time.sleep(0.50)
usb_port.x.write("SENS:CURR:RANG 2e-6")
time.sleep(0.50)
usb_port.x.write("SYST:AZER:STAT OFF") 
time.sleep(0.50)

int_range = ['SENS:CURR:RANG 2e-7','SENS:CURR:RANG 2e-6','SENS:CURR:RANG 2e-5','SENS:CURR:RANG 2e-4','SENS:CURR:RANG 2e-3','SENS:CURR:RANG 2e-2']


fh = open(filename, 'w')

command = str('VSET') + str(Vmin)
usb_port.x.write('++addr 13')
usb_port.x.write(command)
usb_port.x.write('HVON')
m = usb_port.x.query_ascii_values('VOUT?')

usb_port.x.write('FORM:ELEM READ')
usb_port.x.write('++addr 14')

i=0
l=0
for i in range(Npts):
   
   if i==0:
      start_time = time.time()
      chart_time=0.
   else:
      chart_time=time.time()-start_time
   usb_port.x.write('++addr 14')
   time.sleep(0.5)   
   tmp=usb_port.x.query_ascii_values('read?',separator='A',container=np.array)
   current=float(tmp[0])
   print(i,"  current", current, "voltage",Vmin)
   usb_port.x.write('++addr 13')
   time.sleep(0.5)
   tmpv    = usb_port.x.query_ascii_values('VOUT?',separator='A',container=np.array)
   tmpi    = usb_port.x.query_ascii_values('IOUT?',separator='A',container=np.array)
   current = float(tmp[0])
   voltage = float(tmpv) 
   vcurrent= float(tmpi) 
   if current <-666:
      print(current,l) 
      current = 0.0
#      fl.write('Range increased at ' + str(voltage) + '\t'+ str(i)+ 'from '+ str(int_range[l-1]) + 'to ' + str(int_range[l])+ '\n')
      print('increasing the range')
      usb_port.x.write(int_range[l])
      l = l +1
      time.sleep(5.0)
      m = usb_port.x.query('SENS:CURR:RANG?')
      print(m)
   else:
      pass
      
   print(chart_time,"voltage",voltage, "  current:", current, "current PS:", vcurrent)
   fh.write(str(chart_time) + '\t' + str(current) + '\t' + str(voltage) + '\t' + str(vcurrent) + '\n')

fh.close()
 
command = str('VSET') + str(0.0)
usb_port.x.write('++addr 13')
usb_port.x.write(command)
usb_port.x.write('HVOF')

