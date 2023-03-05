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
import time
import numpy as np
import os
import sys

def record_status (filename, variable):
   timestamp = time.strftime("D%Y%m%dT%H%M%S")
   logFile = open(filename, 'a+')
   logFile.write(str(timestamp)+'\n')
   logFile.write(str(variable)+'\n')
   logFile.close()
   
def record_data (filename, variable):
   datFile = open(filename, 'a+')
   datFile.write(str(variable)+'\n')
   datFile.close()
   
def live_display (voltage, current,i):
   import matplotlib.pyplot as plt 
   if (i==0):
      n=0
   else:
      n=np.arange(i)
   plt.scatter (voltage[i], current[i])
   plt.ylim(np.min(current[n])*0.95,np.max(current[n])*1.05)
   plt.xlim(np.min(voltage[n])*0.95,np.max(voltage[n])*1.05)
   plt.show()
   plt.pause(0.0001)
   

