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
usb_port.x.write("TRIG:COUNT 50")            # Set trigger count to 2500
usb_port.x.write("SENS:CURR:RANG:AUTO OFF")    # Turn auto range off
usb_port.x.write("SENS:CURR:NPLC 1")         # Set integration rate to NPLC 0.01
usb_port.x.write("SENS:CURR:RANG 2e-6")        # Use 200 nA range 
usb_port.x.write("SYST:ZCH OFF")               # Turn zero check off
usb_port.x.write("SYST:AZER:STAT OFF")         # Turn auto zero off
usb_port.x.write("DISP:ENAB OFF")              # Turn Display off
usb_port.x.write("*CLS")                       # Clear status model
usb_port.x.write("TRAC:POIN 50")             # Set buffer size to 2500
usb_port.x.write("TRAC:CLE")                   # Clear buffer
usb_port.x.write("TRAC:FEED:CONT NEXT")        # Set storage control to start on next reading
usb_port.x.write("STAT:MEAS:ENAB 512")         # Enable buffer full measurement event
usb_port.x.write("*SRE 1")                     # Enable SRQ on buffer full measurement event
print(usb_port.x.query("*OPC?"))               # operation complete query (synchronize completion of commands)    
usb_port.x.write("INIT")                       # start taking and storing readings wait for GPIB SRQ line to go true
usb_port.x.write("DISP:ENAB ON")               # Turn display on
res=usb_port.x.query("TRAC:DATA?") # Request data from buffer
time.sleep(1.)
res=usb_port.x.query("TRAC:DATA?") # Request data from buffer

print(res)


#usb_port.read_pAmp_buffer()

#tmp = usb_port.x.query_ascii_values('read?',separator='A',container=np.array)
#print tmp

