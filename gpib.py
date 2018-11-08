# new class for GPIB control
# Osama Mohsen

from __future__ import print_function #Python 2.7 compatibility

import numpy as np
import visa  # visa library to import the backend
import csv   # data manipulation
import datetime
import schedule
import time

# visa.log_to_screen()
# rm = visa.ResourceManager('@py')
# x = rm.open_resource( u'ASRL/dev/ttyUSB0::INSTR', timeout=2000)

global DEBUGG

DEBUGG=0

class Control(object):


    def __init__(self):
        ''' 
        this function open the USB port 
        '''        
        if DEBUGG>0:
	   visa.log_to_screen()
        self.rm = visa.ResourceManager('@py')
        self.x = self.rm.open_resource(u'ASRL/dev/ttyUSB0::INSTR', timeout=2000)
	print ('usb port connected')

    def close(self):
        ''' 
        this function closes the USB port 
        '''        
        self.x.close()
	 

    def check_instrument(self):
        address = self.x.query_ascii_values('++addr')
        if address == [14.0]:
            print("PicoAmmeter")
        elif address == [13.0]:
            print("20-kV Voltage Source 1")
        elif address == [12.0]:
            print("5-kV Voltage Source 2")
        elif address == [11.0]:
            print("5-kV Voltage Source")


    def set_voltage(self, Vset, psid=13):
        '''
	set voltage "value" in the power supply psid 
	(psid is defaulted to 13 if not given)
	returns the output voltage from the supply
	'''
        command = 'VSET'   + str(Vset)
	instrum = '++addr '+ str(psid)
        self.x.write(instrum)
        self.x.write(command)
        self.x.write('HVON')
        Vout = x.query_ascii_values('VOUT?')
        return (Vout)


    def reset_pAmp(self, scale=0.002, int_plc='0.01'):
        '''
	reads current from pAmmeter 
	the scale parameter sets the range: 0.002 (2 mA) 
	allowed values are:
             2E-2 or 0.02
             2E-3 or 0.002
             2E-4 or 0.0002
             2E-5 or 0.00002
             2E-6 or 0.000002
             2E-7 or 0.0000002
             2E-8 or 0.00000002
             2E-9 or 0.000000002
	int_plc is the integration rate needs to be set to 
        small alue 0.01 for buffer acquisition     
	returns current Iout 
	'''
        self.x.write('FORM:ELEM READ')
        self.x.write('++addr 14')
        self.x.write('*RST')
        time.sleep(1)
        self.x.write('SENS:CURR:RANG:AUTO OFF')
        time.sleep(1)
	set_scale='SENS:CURR:RANG '+str(scale)
        self.x.write(set_scale)
        time.sleep(1)
	set_integ='SENS:CURR:NPLC '+str(int_plc)
        self.x.write(set_integ)
        time.sleep(1)
        self.x.write('SYST:ZCH OFF ')
        time.sleep(1)
        self.x.write('SYST:AZER:STAT OFF')


    def read_pAmp(self):
        self.x.write('FORM:ELEM READ')
        self.x.write('++addr 14')
        tmp = self.x.query_ascii_values('read?',separator='A',container=np.array)
#       query('read?') 
        if DEBUGG>0:
	   print ("tmp ----",tmp)
	try: 
	   Iout=float(tmp[0])
        except ValueError,e:
           print ("error",e)
	   Iout=666
        return (Iout)

     
    def read_pAmp_buffer(self, num_buffer=100):
        '''
	reads current from pAmmeter 
	num_buffer number of value to save in the buffer
	returns current Iout 
	'''
        self.x.write('FORM:ELEM READ')
        self.x.write('++addr 14')
        self.x.write("*RST")                       # Return 6485 to RST default
        print(self.x.query("SYS:ERR:ALL?"))        # Return error message 
        self.x.write("TRIG:DEL 0")                 # Set trigger delay to zero seconds
        self.x.write("TRIG:COUNT 2500")            # Set trigger count to 2500
        self.x.write("SENS:CURR:RANG:AUTO OFF")    # Turn auto range off
        self.x.write("SENS:CURR:NPLC .01")         # Set integration rate to NPLC 0.01
        self.x.write("SENS:CURR:RANG 2e-7")        # Use 200 nA range 
        self.x.write("SYST:ZCH OFF")               # Turn zero check off
        self.x.write("SYST:AZER:STAT OFF")         # Turn auto zero off
        self.x.write("DISP:ENAB OFF")              # Turn Display off
        self.x.write("*CLS")                       # Clear status model
        self.x.write("TRAC:POIN 2500")             # Set buffer size to 2500
        self.x.write("TRAC:CLE")                   # Clear buffer
        self.x.write("TRAC:FEED:CONT NEXT")        # Set storage control to start on next reading
        self.x.write("STAT:MEAS:ENAB 512")         # Enable buffer full measurement event
        self.x.write("*SRE 1")                     # Enable SRQ on buffer full measurement event
        print(self.x.query("*OPC?"))     # operation complete query (synchronize completion of commands)    
        self.x.write("INIT")                       # start taking and storing readings wait for GPIB SRQ line to go true
        self.x.write("DISP:ENAB ON")               # Turn display on
        print(self.x.query("TRAC:DATA?")) # Request data from buffer

     
    def Zero_check(self):
        self.x.write('++addr 14')  # change to picoammeter
        self.x.write('*RST')  # reset the device
        self.x.write('FORM:ELEM READ')  # read only the value of the current
        self.x.write('SYST:ZCH ON')  # zero check is on
        self.x.write('INIT')  # init reading
        self.x.write('SYST:ZCOR:ACQ')  # take the last value is zero correction
        self.x.write('CURR:RANG:AUTO ON')  # auto range current is on
        self.x.write('SYST:ZCH OFF')  # zero check is off (now you can connect the measurment)


"""
if __name__ == '__main__':
    cont = Control()
    cont.read_one_value()
"""
