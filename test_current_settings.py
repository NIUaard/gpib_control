import gpib
import time
import numpy as np
import string as str

#import matplotlib.pyplot as plt 

usb_port=gpib.Control()

usb_port.x.write("*RST")                   
time.sleep(0.50)
usb_port.x.write("SYST:ZCH OFF")
time.sleep(0.50)
usb_port.x.write("SENS:CURR:RANG 2e-7")
time.sleep(0.50)
usb_port.x.write("SYST:AZER:STAT OFF") 
time.sleep(0.50)


usb_port.x.write('FORM:ELEM READ')
usb_port.x.write('++addr 14')
tmp=usb_port.x.query_ascii_values('read?',separator='A',container=np.array)
print tmp

