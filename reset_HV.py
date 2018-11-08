# Added a command to read the real voltage (line 78-80) : 16-07-2018 by Osama Mohsen
# Added a new path to sort measurments by date in the Documents 
from __future__ import print_function #Python 2.7 compatibility
import gpib
import time
import numpy as np
import os
###############################################
usb_port=gpib.Control()


usb_port.x.write('++addr 13')
command = str('VSET') + str(1000)
usb_port.x.write(command)
usb_port.x.write('HVON')

IN=input("TYPE something and enter")

print ("test clear")
#command = str('TCLR') 
command = str('TMOD') + str(1)
usb_port.x.write(command)

command = str('VSET') + str(100)
usb_port.x.write(command)

m = usb_port.x.query_ascii_values('VOUT?')

print(m)
