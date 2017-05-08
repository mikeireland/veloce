"""
Control the servo loop for Veloce temperature control. This runs as a server that
accepts text or ZMQ-based input, and runs the servo loop as a background task.

Version history
---------------
0.1     19 Jan 2017     MJI     Skeleton only

"""
from __future__ import print_function, division
import numpy as np
from labjack import ljm
import time
import numpy as np
import matplotlib.pyplot as plt
from lqg_math import *

LABJACK_IP = "150.203.91.171"
HEATER_DIOS = ["0"]         #Input/output indices of the heaters
PWM_MAX =1000000
AIN_NAME = "AIN0"
HEATER_MAX = 3.409

class ThermalControl:
    def __init__(self, ip=None):
        if not ip:
            self.ip = LABJACK_IP
        try:
            self.handle = ljm.openS("ANY", "ANY", self.ip)
        except:
            print("Unable to open labjack {}".format(self.ip))
            self.labjack_open=False
            return
        self.labjack_open=True
        #WARNING: This really should read from the labjack, and set the heater values
        #appropriately
        self.cmd_initialize("")
        self.voltage=99.9
        self.lqg=0
        self.datapoints=10000
        self.storedata = 0
        self.setpoint = 25.0
        self.nreads=int(0)
        self.last_print=-1
        self.index = 0
        self.temphist = np.zeros(self.datapoints)
        self.lqgverbose = 1
        self.x_est = np.array([[0.],[0.],[0.]])
        self.u = np.array([[0]])

    #Our user or socket commands
    def cmd_initialize(self, the_command):
        """Set the heaters to zero, and set the local copy of the heater values
        (in the range 0-1) to 0. 
        
        By default, we use a 10 MHz clock (divisor of 8) and count up to 1,000,000 to give
        PWM at a 10Hz rate.
        """
        if not self.labjack_open:
            raise UserWarning("Labjack not open!")
            
        #Set FIO 0,2,3 as an example. Note that FIO 1 isn't allowed to have PWM:
        #https://labjack.com/support/datasheets/t7/digital-io/extended-features
        #(and FIO4 upwards is only available via one of the DB connectors)
        self.current_heaters = np.zeros(len(HEATER_DIOS))
        aNames = ["DIO_EF_CLOCK0_DIVISOR", "DIO_EF_CLOCK0_ROLL_VALUE", "DIO_EF_CLOCK0_ENABLE"]
        #Set the first number below to 256 for testing on a multimeter.
        #Set to 8 for normal operation
        aValues = [8, PWM_MAX, 1]
        for dio in HEATER_DIOS:
            aNames.extend(["DIO"+dio+"_EF_INDEX", "DIO"+dio+"_EF_CONFIG_A", "DIO"+dio+"_EF_ENABLE"])
            aValues.extend([0,0,1])

        #See labjack example python scripts - looks pretty simple!
        numFrames = len(aNames)
        results = ljm.eWriteNames(self.handle, numFrames, aNames, aValues)
        
        #Now set up the Analog input
        #Note that the settling time is set to default (0), which isn't actually
        #zero microsecs.
        aNames = ["AIN_ALL_NEGATIVE_CH", "AIN_ALL_RANGE", "AIN_ALL_RESOLUTION_INDEX", "AIN_ALL_SETTLING_US"]
        aValues = [1, 1, 10, 0]
        numFrames = len(aNames)
        results = ljm.eWriteNames(self.handle, numFrames, aNames, aValues)
        
    def cmd_close(self, the_command):
        """Close the connection to the labjack"""
        ljm.close(self.handle)
        self.labjack_open=True
        
    def cmd_heater(self, the_command):
        """Set a single heater to a single PWM output"""
        the_command = the_command.split()
        #Error check the input (for bugshooting, do this
        #even if the labjack isn't open)
        if len(the_command) != 3:
            return "Useage: HEATER [heater_index] [fraction]"
        else:
            try:
                dio_index = int(the_command[1])
            except:
                return "ERROR: heater_index must be an integer"
            try:
                dio = HEATER_DIOS[dio_index]
            except:
                return "ERROR: heater_index out of range"
            try:
                fraction = float(the_command[2])
            except:
                return "ERROR: fraction must be between 0.0 and 1.0"
            if (fraction < 0) or (fraction > 1):
                return "ERROR: fraction must be between 0.0 and 1.0"
        #Check that the labjack is open
        if not self.labjack_open:
            raise UserWarning("Labjack not open!")
                
        #Now we've error-checked, we can turn the heater fraction to an
        #integer and write tot he labjack
        aNames = ["DIO"+dio+"_EF_CONFIG_A"]
        aValues = [int(fraction * PWM_MAX)]
        numFrames = len(aNames)
        results = ljm.eWriteNames(self.handle, numFrames, aNames, aValues)
        return "Done."
        
    def cmd_setgain(self, the_command):
        """Dummy gain setting function"""
        the_command = the_command.split()
        if len(the_command)!=2:
            return "Useage: SETGAIN [newgain]"
        else:
            return "Gain not set to {}".format(the_command[1:])
            
    def cmd_getvs(self, the_command):
        """Return the current voltages as a string.
        """
        return "{0:9.6f}".format(self.voltage)

    def gettemp(self):
        """Return the temperature as a float"""
        ##uses converts voltage temperature, resistance implemented
        R = 10000
        Vin = 5
        resistance = (2*R*self.voltage)/(Vin - self.voltage)
        resistance += R
        aVal = 0.00113259149597421
        bVal = 0.000233514798680064
        cVal = 0.00000009045521729374
        temp_inv = aVal + bVal*np.log(resistance) + cVal*((np.log(resistance))**3)
        tempKelv = 1/(temp_inv)
        tempCelc = tempKelv -273.15
        return tempCelc

    def cmd_gettemp(self, the_command):
        """Return the temperature to the client as a string"""
        return "{0:9.6f}".format(self.gettemp())

    def cmd_lqgstart(self, the_command):
        self.lqg = 1
    
    def cmd_lqgsilent(self, the_command):
        self.lqgverbose = 0
    
    def cmd_lqgverbose(self, the_command):
        self.lqgverbose = 1

    def cmd_startrec(self, the_command):
        self.storedata = 1

    def cmd_stoprec(self, the_command):
        self.storedata = 0

    def cmd_writedata(self, the_command):
        np.savetxt('data.txt',self.temphist, fmt='%9.6f', delimiter=',')          

    def cmd_lqgstop(self, the_command):
        self.lqg = 0 

    def job_doservo(self):
        """Dummy servo loop job
        
        Just read the voltage, and print once per second 
        (plus the number of reads)"""
        self.voltage = ljm.eReadName(self.handle, AIN_NAME)
        time.sleep(lqg_dt) #!!! MJI should be lqg_math.dt
        self.nreads += 1
        if time.time() > self.last_print + 1:
            self.last_print=time.time()
        #    print("Voltage: {0:9.6f}".format(self.voltage))
      
        #Get the current temperature and set it to .
        tempnow = self.gettemp()
 
        #store temperature history for data measurment
        if self.index == self.datapoints:
           np.savetxt('data.txt',self.temphist, fmt='%9.6f', delimiter=',')
           self.storedata = 0
           self.index = 0 #!!! Matthew, I think this is what you meant and not self.lqg=1?

        if self.storedata == 1:
           self.temphist[self.index] = tempnow
           self.index = self.index + 1
  
 
        if self.lqg == 1:
            #!!! MATTHEW - this next line is great for debugging !!!
            #!!! Uncomment it to look at variables, e.g. print(y)
            #!!! and y.shape
            #import pdb; pdb.set_trace()
            
            #Store the current temperature in y.
            y = np.zeros( (1,1) )
            y[0] = tempnow - self.setpoint
            
            #Based on this measurement, what is the next value of x_i+1 est?
            x_est_new = np.dot(A_mat, self.x_est)
            x_est_new += np.dot(B_mat, self.u)
            dummy = y - np.dot(C_mat, (np.dot(A_mat, self.x_est) + np.dot(B_mat, self.u)))
            x_est_new += np.dot(K_mat, dummy)
            self.x_est = x_est_new #x_i+1 has now become xi
            # Now find u
            if use_lqg:
                self.u = -np.dot(L_mat, self.x_est)
                ucalc=self.u[0,0]
                if self.u[0,0] < 0:
                    self.u[0,0] = 0
                elif self.u[0,0] > HEATER_MAX:
                    self.u[0,0] = HEATER_MAX
                #!!!Put in an offset of 0.5, i.e. the heater half
                #on is at "zero", because it can't go negative.
                fraction = self.u[0,0]/HEATER_MAX 
                
                #FIXME: This assumes we are using heater 0.
                aNames = ["DIO"+HEATER_DIOS[0]+"_EF_CONFIG_A"]
                aValues = [int(fraction * PWM_MAX)]
                numFrames = len(aNames)
                results = ljm.eWriteNames(self.handle, numFrames, aNames, aValues)

            #!!!Another error here, u was an array, so numpy prints it as a string
            if self.lqgverbose == 1:
                print("Heater Wattage: {0:9.6f}".format(self.u[0,0]))
                print("Heater Fraction: {0:9.6f}".format(fraction))
                print("Temperature: {0:9.6f}".format(self.gettemp()))
                print("Data Index: {0:9.6f}".format(self.index))
                print("Ambient Temperature {:9.4f}".format(self.x_est[0,0] + self.setpoint))
                print("Heater Temperature {:9.4f}".format(self.x_est[1,0] + self.setpoint))
                print("Plate Temperature {:9.4f}".format(self.x_est[2,0] + self.setpoint))
                tempsensor = -1*self.x_est[0,0]*G_sa/(G_sa+G_ps)+self.x_est[2,0]*G_ps/(G_ps+G_sa)
                print("Estimated sensor Temperature {:9.4f}".format(tempsensor + self.setpoint))
                print(ucalc)




            
        return 
