"""
Control the servo loop for Veloce temperature control. This runs as a server that
accepts text or ZMQ-based input, and runs the servo loop as a background task.

Version history
---------------
0.1     19 Jan 2017     MJI     Skeleton only
0.2     July 2017       MR/MJI  Functioning with test plate
0.3     29 Aug 2017     MJI     Tidy-up, especially logging
"""
from __future__ import print_function, division
import numpy as np
from labjack import ljm
import time
import numpy as np
import logging

#FIXME: we should of course import lqg_math and then refer to the variables as 
#e.g.
#lqg_math.lqg_dt
#lqg_math.A_mat
#...etc.
import lqg_math_2_cap as lqg_math

LABJACK_IP = "192.168.1.7"
#Long sides, short sides, lid and base for FIO 0,2,3,4 respectively.
#NB: Heaters checked at 30, 30, 20 and 20 ohms.
HEATER_LABELS = ["Long", "Short", "Lid", "Base", "Cryostat"]
HEATER_DIOS = ["0","2","3","4","5"]         #Input/output indices of the heaters
PWM_MAX =1000000
#Table, lower then upper.
AIN_LABELS = ["Table", "Lower", "Upper", "Cryostat", "Aux 1", "Aux 2", "Aux 3"]
AIN_NAMES = ["AIN0", "AIN2", "AIN4", "AIN6", "AIN8", "AIN10", "AIN12"] #Temperature analog input names

#Calibrated using calibrate.py @25.3C - see M-Robertson for details
T_OFFSETS = [-0., 0.01531123, 0.06008029, 0.01812604, 0.06101344, 0.02001082, 0.06289097] 
HEATER_MAX = [67.2,28.8,13.09]
LJ_REST_TIME = 0.01

#Derivative of the temperature in K/s with the heater on full.
TEMP_DERIV = 0.00035 
#This should be set to 1./ENCLOSURE_TIME_CONSTANT. There are multiple time
#constants - this is the shortest one, i.e. the time in between turning the
#heater on or off and having a linear temperature ramp.
PID_GAIN_HZ = 0.002

#Similarly for the cryostat servo loop. From Matthew Robertson email, 19 Oct.
CRYO_PID_GAIN_HZ = 0.004
CRYO_TEMP_DERIV = 0.0008

#In the nested servo loop, we set the outer enclosure setpoint according to
#the difference between the table and its setpoint. The 
NESTED_GAIN = 8.0
NESTED_TIME_CONST = 3600.0 #About 10 hours.
TABLE_DEADZONE = 0.05

LOG_FILENAME = 'thermal_control.log'
#Set the following to logging.INFO on or logging.DEBUG on
logging.basicConfig(filename=LOG_FILENAME, level=logging.DEBUG, \
    format='%(asctime)s, %(created)f, %(levelname)s,  %(message)s', \
    datefmt='%Y-%m-%d %H:%M:%S')

class ThermalControl:
    def __init__(self, ip=None):
        if not ip:
            self.ip = LABJACK_IP
        
        self.cmd_open("")
        
        #WARNING: This really should read from the labjack, and set the heater values
        #appropriately
        self.cmd_initialize("")
        self.voltages=99.9*np.ones(len(AIN_NAMES))
        self.lqg=False
        self.use_lqg=True
        
        #This turns logging on or off.
        self.storedata = True 
        self.setpoint = 25.0
        self.enc_setpoint = self.setpoint #Just a starting value
        self.last_print=-1
        self.ulqg = 0
        self.lqgverbose = False
        self.x_est = np.zeros((11,1))
        self.u = np.zeros((3,1))

        #PID Constants
        self.pid=False
        self.cryo_pid=True #Inside the pid code
        self.pid_gain = PID_GAIN_HZ/TEMP_DERIV
        self.pid_i = 0.5*PID_GAIN_HZ**2/TEMP_DERIV
        self.pid_ints = np.array([0.,0.])

        #Constants for the nested servo loop. See constants above.
        self.nested_gain = NESTED_GAIN
        self.nested_i = 1.0/NESTED_TIME_CONST
        self.nested_int = 0.

        #Constants on the cryo servo loop.
        self.cryo_pid_gain = CRYO_PID_GAIN_HZ/CRYO_TEMP_DERIV
        self.cryo_pid_i = 0.5*CRYO_PID_GAIN_HZ**2/CRYO_TEMP_DERIV
        self.cryo_pid_int = 0.
    
    def cmd_open(self, the_command):
        """Open the socket connection to the labjack"""
        try:
            self.handle = ljm.openS("ANY", "ANY", self.ip)
        except:
            print("Unable to open labjack {}".format(self.ip))
            self.labjack_open=False
            return
        self.labjack_open=True   
        return "Labjack Connection Opened"

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
        #Set to 16 for normal operation (5Hz)
        aValues = [16, PWM_MAX, 1]
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
        return "Labjack Initialized"
        
    def cmd_close(self, the_command):
        """Close the connection to the labjack"""
        ljm.close(self.handle)
        self.labjack_open=True
        return "Labjack connection closed."
        
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
        self.set_heater(int(the_command[1]), float(the_command[2]))
        #import pdb; pdb.set_trace()
        return "Done."
        
    def cmd_setgain(self, the_command):
        """Set the PID gain"""
        the_command = the_command.split()
        if len(the_command)!=2:
            return "Useage: SETGAIN [newgain]"
        else:
            self.pid_gain = float(the_command[1])
            return "Gain set to {:6.5f}".format(self.pid_gain)

    def cmd_seti(self, the_command):
        """Set the PID integral term"""
        the_command = the_command.split()
        if len(the_command)!=2:
            return "Useage: SETI [newi]"
        else:
            self.pid_i = float(the_command[1])
            return "PID I term set to {:6.5f}".format(self.pid_i)

    def cmd_setnestgain(self, the_command):
        """Set the PID nested gain"""
        the_command = the_command.split()
        if len(the_command)!=2:
            return "Useage: SETNESTGAIN [newgain]"
        else:
            self.pid_gain = float(the_command[1])
            return "Nested servo gain set to {:6.5f}".format(self.nested_gain)

    def cmd_setnesti(self, the_command):
        """Set the PID nested integral term"""
        the_command = the_command.split()
        if len(the_command)!=2:
            return "Useage: SETNESTI [newi]"
        else:
            self.nested_i = float(the_command[1])
            return "PID I term set to {:6.5f}".format(self.nested_i)      
          
    def cmd_getvs(self, the_command):
        """Return the current voltages as a string.
        """
        return (', {:9.6f}'*len(AIN_NAMES)).format(*self.voltages)[2:]

    def cmd_gettemp(self, the_command):
        """Return the temperature to the client as a string"""
        temps = self.gettemps()
        return (', {:9.6f}'*len(AIN_NAMES)).format(*temps)[2:]
        #return "{0:9.6f}, {0:9.6f} {0:9.6f}".format(self.gettemp(0), self.gettemp(1), self.gettemp(2))
        
    def cmd_getresistance(self, the_command):
        """Return the temperature to the client as a string"""
        resistances = self.getresistances()
        return (', {:12.9f}'*len(AIN_NAMES)).format(*resistances)[2:]
        #return "{0:9.6f}, {0:9.6f} {0:9.6f}".format(self.gettemp(0), self.gettemp(1), self.gettemp(2))

    def cmd_lqgstart(self, the_command):
        self.pid = False
        self.lqg = True
    
    def cmd_lqgsilent(self, the_command):
        self.lqgverbose = False
        return ""
    
    def cmd_lqgverbose(self, the_command):
        self.lqgverbose = True
        return ""

    def cmd_startrec(self, the_command):
        self.storedata = True
        return ""

    def cmd_stoprec(self, the_command):
        self.storedata = False
        return ""

    def cmd_lqgstop(self, the_command):
        self.lqg = False 
        return ""

    def cmd_pidstart(self, the_command):
        self.pid = True
        self.lqg = False
        return ""

    def cmd_pidstop(self, the_command):
        self.pid = False
        return ""

    def cmd_cryostart(self, the_command):
        self.cryo_pid = True
        return ""

    def cmd_cryostop(self, the_command):
        self.cryo_pid = False
        return ""

    def cmd_setpoint(self, the_command):
        """Set the temperature setpoint"""
        the_command = the_command.split()
        if len(the_command)!=2:
            return "Useage: SETPOINT [new setpoint]"
        else:
            self.setpoint = float(the_command[1])
            return "Temperature setpoing set to {:6.5f}".format(self.setpoint)

    def set_heater(self, ix, fraction):
        """Set the heater to a fraction of its full range.
        
        Parameters
        ----------
        ix: int
            The heater to set.
        
        fraction: float
            The fractional heater current (via PWM).
        """
        #self.u[ix] = fraction
        aNames = ["DIO"+HEATER_DIOS[ix]+"_EF_CONFIG_A"]
        aValues = [int(fraction * PWM_MAX)]
        numFrames = len(aNames)
        results = ljm.eWriteNames(self.handle, numFrames, aNames, aValues)
        #import pdb; pdb.set_trace()

    def gettemp(self, ix, invert_voltage=True):
        """Return one temperature as a float. See Roberton's the
        
        v_out = v_in * [ R_t/(R_T + R) - R/(R_T + R) ]
        R_T - R = (R_T + R) * (v_out/v_in)
        R_T*(1 - (v_out/v_in)) = R * (1 + (v_out/v_in))
        R_T = R * (v_in + v_out) / (v_in - v_out)
        
        Parameters
        ----------
        ix: int
            Index of the sensor to be provided.
            
        Returns
        -------
        temp: float
            Temperature in Celcius
        """
        ##uses converts voltage temperature, resistance implemented
        R = 10000
        Vin = 5
        if invert_voltage:
            voltage = -self.voltages[ix]
        else:
            voltage = self.voltages[ix]
        resistance = R * (Vin + voltage)/(Vin - voltage)
        #resistance = (2*R*self.voltage)/(Vin - self.voltage)
        #resistance += R
        aVal = 0.00113259149597421
        bVal = 0.000233514798680064
        cVal = 0.00000009045521729374
        temp_inv = aVal + bVal*np.log(resistance) + cVal*((np.log(resistance))**3)
        tempKelv = 1/(temp_inv)
        tempCelc = tempKelv -273.15
        return tempCelc - T_OFFSETS[ix]
        
    def getresistance(self, ix, invert_voltage=True):
        """Return one resistance as a float. See Roberton's the
        
        v_out = v_in * [ R_t/(R_T + R) - R/(R_T + R) ]
        R_T - R = (R_T + R) * (v_out/v_in)
        R_T*(1 - (v_out/v_in)) = R * (1 + (v_out/v_in))
        R_T = R * (v_in + v_out) / (v_in - v_out)
        
        Parameters
        ----------
        ix: int
            Index of the sensor to be provided.
            
        Returns
        -------
        temp: float
            Temperature in Celcius
        """
        ##uses converts voltage temperature, resistance implemented
        R = 10000
        Vin = 5
        if invert_voltage:
            voltage = -self.voltages[ix]
        else:
            voltage = self.voltages[ix]
        resistance = R * (Vin + voltage)/(Vin - voltage)
        return resistance

    def gettemps(self):
        """Get all temperatures.
        
        Returns
        -------
        temps: list
            A list of temperatures for all sensors.
        """
        temps = ()
        for ix in range(0, (len(AIN_NAMES))):
            temps += (self.gettemp(ix),)
        return temps

    def getresistances(self):
        """Get all temperatures.
        
        Returns
        -------
        temps: list
            A list of temperatures for all sensors.
        """
        resistances = ()
        for ix in range(0, (len(AIN_NAMES))):
            resistances += (self.getresistance(ix),)
        return resistances

    def lqg_servo(self):
        #Store the current temperature in y.
        y = np.array([ [self.gettemp(2) - self.setpoint] ,[self.gettemp(0) - self.setpoint],[self.gettemp(1)- self.setpoint],[self.gettemp(3)- self.setpoint]])   
        #Based on this measurement, what is the next value of x_i+1 est?
        x_est_new = np.dot(lqg_math.A_mat, self.x_est)
        #import pdb; pdb.set_trace()
        x_est_new += np.dot(lqg_math.B_mat, self.u)
        dummy = y - np.dot(lqg_math.C_mat, (np.dot(lqg_math.A_mat, self.x_est) + np.dot(lqg_math.B_mat, self.u)))
        x_est_new += np.dot(lqg_math.K_mat, dummy)
        self.x_est = x_est_new #x_i+1 has now become xi
        # Now find u
        self.u = -np.dot(lqg_math.L_mat, self.x_est)
        self.ulqg = self.u
        #offset because heater can't be negative
        fraction = [0]*len(HEATER_MAX)
        for i in range(0, len(HEATER_MAX)):
	    fraction[i] = self.u[i]/HEATER_MAX[i]
	    
        #Setting the Heaters
        for i, frac in enumerate(fraction):
    	    if frac < 0:
	        self.u[i,0] = 0
	        fraction[i] = 0
	    elif fraction > 1:
	        self.u[i,0] = HEATER_MAX[i]
	        fraction[i] = 1
    
        for i, frac in enumerate(fraction):
	    if i == 0:
	        self.set_heater(0,frac)
	        self.set_heater(1,frac)
	        self.set_heater(2,frac)
	    if i == 1:
	        self.set_heater(3,frac)
	    if i == 2:
	        self.set_heater(4, frac) 

    def pid_servo(self):
        #Set the Enclosure set point according to the table temperature
        t_tab = self.gettemp(0)
        #Ignore table temperatures more than TABLE_DEADZONE from the setpoint.
        #This is a hack for limiting the affect of a limited heater current.
        if t_tab > self.setpoint + TABLE_DEADZONE:
           t_tab = self.setpoint + TABLE_DEADZONE
           self.nested_int=0
        if t_tab < self.setpoint - TABLE_DEADZONE:
            t_tab = self.setpoint - TABLE_DEADZONE
            self.nested_int=0
        self.nested_int += lqg_math.lqg_dt*(self.setpoint - t_tab)
        self.enc_setpoint = self.setpoint + self.nested_gain*(self.setpoint - t_tab) \
            + self.nested_i*self.nested_int
            
        if self.storedata:
            logging.debug('ENCPID, {0:5.3f}, {1:5.3f}'.format(self.enc_setpoint, self.nested_int))

        #Start the Enclosue PID loop. For the integral component, reset 
        #all integral terms whenever the heater hits the rail.
        t0 = self.gettemp(1)
        self.pid_ints[0] += lqg_math.lqg_dt*(self.enc_setpoint - t0)
        h0 = 0.5 + self.pid_gain*(self.enc_setpoint - t0) + self.pid_i*self.pid_ints[0]
        if (h0<0):
            h0=0
            self.pid_ints[0]=0
            self.nested_int=0
        if (h0>1):
            h0=1
            self.pid_ints[0]=0
            self.nested_int=0
        t1 = self.gettemp(2)
        self.pid_ints[1] += lqg_math.lqg_dt*(self.enc_setpoint - t1)
        h1 = 0.5 + self.pid_gain*(self.enc_setpoint - t1) + self.pid_i*self.pid_ints[1]
        if (h1<0):
            h1=0
            self.pid_ints[1]=0
            self.nested_int=0
        if (h1>1):
            h1=1
            self.pid_ints[1]=0
            self.nested_int=0
                        
        #Now control the heaters...
        #As the lid has significantly less loss to ambient, use less power.
        self.set_heater(0, h1)
        self.set_heater(1, h1)
        self.set_heater(2, 0.7*h1)
        self.set_heater(3, h0)
        return h0, h1


    def cryo_servo(self):
        t2 = self.gettemp(3)
        self.cryo_pid_int += lqg_math.lqg_dt*(self.setpoint - t2)
        h2 = 0.5 + self.cryo_pid_gain*(self.setpoint - t2) + self.cryo_pid_i*self.cryo_pid_int
        if (h2<0):
            h2=0
            self.cryo_pid_int=0
        if (h2>1):
            h2=1
            self.cryo_pid_int=0
        #Now control the heaters
        self.set_heater(4, h2)
        return h2

    def job_doservo(self):
        """Servo loop job
        
        Every lqg_math.lgq_dt, we read the voltages into our local variables, then
        compute the temperatures. Note that gettemp therefore doesn't actually get
        the temperatures, it just computs them from the last time voltages were read
        in.
        
        """
        time.sleep(lqg_math.lqg_dt) 
        for ix, ain_name in enumerate(AIN_NAMES):
            try:
                self.voltages[ix] = ljm.eReadName(self.handle, ain_name)
            except:
                print("Could not read temperature {:d} one time".format(ix))
                logging.warning("Could not read temperature {:d} one time".format(ix))
                #Now try again
                try:
                    self.voltages[ix] = ljm.eReadName(self.handle, ain_name)
                except:
                    print("Trying to re-open labjack connection...")
                    print(self.cmd_close(""))
                    print(self.cmd_open(""))
                    print(self.cmd_initialize(""))
                    try:
                        self.voltages[ix] = ljm.eReadName(self.handle, ain_name)
                    except:
                        print("Giving up reading temperature {:d}".format(ix))
                        logging.error("Giving up reading temperature {:d}".format(ix))
                    
        if time.time() > self.last_print + 1:
            self.last_print=time.time()

        #The servo can be LQG or PID. When either is set to true, the other is set to 
        #false.
        if self.lqg:
            self.lqg_servo()

        #Special real-time debugging mode for printing to screen
        if self.lqgverbose == 1:
            for i in range(0,len(self.ulqg)):
                print("Heater " + str(i) + " Wattage:" + str(self.ulqg[i]))

            print("Calculated Ambient Temperature {:9.4f}".format(self.x_est[0,0] + self.setpoint))
            print("Calculated Cryostat Inside Temperature {:9.4f}".format(self.x_est[1,0] + self.setpoint))
            print("Calculated Floor Temperature {:9.4f}".format(self.x_est[2,0] + self.setpoint))
            logging.debug('HEATERS, ' + (len(self.u)*", {:9.6f}").format(*self.u.flatten())[2:])
            print("---")
            print("Table Temperature: {0:9.6f}".format(self.gettemp(0)))
            print("Lower Temperature: {0:9.6f}".format(self.gettemp(1)))
            print("Upper Temperature: {0:9.6f}".format(self.gettemp(2)))
            print("Cryostat Temperature: {0:9.6f}".format(self.gettemp(3)))
            print("Estimated ti1:")
            print(int(self.x_est[4,0]) + self.setpoint)
                
        if self.pid:
            h0, h1 = self.pid_servo()
        else:
	    h0 = 0
            h1 = 0    
 
        if self.cryo_pid:
            h2 = self.cryo_servo()
        else:
            h2 = 0    
         
        if (self.cryo_pid or self.pid) and self.storedata: 
            logging.debug('HEATPID, {0:5.3f}, {1:5.3f}, {2:5.3f}, {3:5.3f}, {4:5.3f}, {5:5.3f}'.format(h0,h1,h2,self.pid_ints[0],self.pid_ints[1],self.cryo_pid_int))
            
        if self.storedata:
            logging.info('TEMPS, ' + self.cmd_gettemp(""))

        return
