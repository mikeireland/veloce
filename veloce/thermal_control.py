"""
Control the servo loop for Veloce temperature control. This runs as a server that
accepts text or ZMQ-based input, and runs the servo loop as a background task.

Version history
---------------
0.1     19 Jan 2017     MJI     Skeleton only
"""

from labjack import ljm
LABJACK_IP = "192.168.1.3"
HEATER_DIOS = ["0"]         #Input/output indices of the heaters
PWM_MAX =1000000

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
        self.cmd_initialize()

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
        aValues = [8, PWM_MAX, 1]
        for dio in HEATER_DIOS:
            aNames.extend(["DIO"+dio+"_EF_INDEX", "DIO"+dio+"_EF_CONFIG_A", "DIO"+dio+"_EF_ENABLE"])
            aValues.extend([0,0,1])

        #See labjack example python scripts - looks pretty simple!
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
        
    def cmd_setgain(self, the_command):
        """Dummy gain setting function"""
        the_command = the_command.split()
        if len(the_command)!=2:
            return "Useage: SETGAIN [newgain]"
        else:
            return "Gain not set to {}".format(the_command[1:])
        
    def job_doservo(self):
        """Dummy servo loop job"""
        return