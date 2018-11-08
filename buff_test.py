from __future__ import print_function #Python 2.7 compatibility
import gpib
import time
import numpy as np
import string as str

#import matplotlib.pyplot as plt 

usb_port=gpib.Control()

usb_port.x.write('FORM:ELEM READ')
usb_port.x.write('++addr 14')
usb_port.x.write("*RST")                       # Return 6485 to RST default
print(usb_port.x.query("SYS:ERR:ALL?"))        # Return error message 
usb_port.x.write("TRIG:DEL 0")                 # Set trigger delay to zero seconds
usb_port.x.write("TRIG:COUNT 100")            # Set trigger count to 2500
usb_port.x.write("TRAC:POIN 100")             # Set buffer size to 2500
usb_port.x.write("TRAC:CLE")                   # Clear buffer
usb_port.x.write("TRAC:FEED:CONT NEXT")        # Set storage control to start on next reading
#usb_port.x.write("STAT:MEAS:ENAB 512")         # Enable buffer full measurement event
usb_port.x.write("*SRE 1")                     # Enable SRQ on buffer full measurement event
print ('*******OPC*******')
print(usb_port.x.query("*OPC?"))     # operation complete query (synchronize completion of commands)    
usb_port.x.write("INIT")                       # start taking and storing readings wait for GPIB SRQ line to go true

res= usb_port.x.query("TRAC:DATA?")


print(res)
print(len(res))
#usb_port.read_pAmp_buffer()

#tmp = usb_port.x.query_ascii_values('read?',separator='A',container=np.array)
#print tmp

