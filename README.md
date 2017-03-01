# veloce
Python code for Veloce, designed to be compatible with Ian Price's zmq-based comms protocol.

Most importantly, you have to start by setting LABJACK_IP appropriately in thermal_control.py,
and ensuring that the correct FIO is used for output (FIO0 by default)

Test the skeleton code with:
>> python test_thermal.py
help

You will see that one of the commands in help is "heater". You can turn the 
heater on (via PWM) between 0 and 1 using (e.g):

heater 0 0.5

This turns the first heater (0) to a value of 0.5. 
