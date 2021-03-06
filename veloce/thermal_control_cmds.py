""" Given a list of functions and a list of strings, this program 
 is designed to find the function matching a given string.
 As this has to be done in principle when "compiling", the C way
 to do this is to have a list of functions and a list of strings.

 Function lists may have to be imported from many places, but
 within the same global scope. With the "simple server" mentality, 
 this can be passed a single object that contains the function 
 definitions, as a single object should be enough to contain all
 pieces of hardware (which should be 1).

 The idea is that a single call to:
 execute_command(command)
 ... returns a string for successful execution, or a useful string

 Try: 
 ./make_command_list dummy_functions.py 
 import dummy_functions as d
 from command_list import CommandList
 cl = CommandList(d)
 print(cl.execute_command("help")) """

import pydoc

class CommandList():
    def __init__(self, module_with_functions):
        '''Initialise the command list with the module containing all function names'''
        self.module_with_functions=module_with_functions

    def execute_command(self, the_command):
        '''Find the_command amongst the list of commands like cmd_one in module m
    
        This returns a string containing the response, or a -1 if a quit is commanded.'''
        m = self.module_with_functions
        the_functions = dict(open=m.cmd_open,initialize=m.cmd_initialize,close=m.cmd_close,heater=m.cmd_heater,setgain=m.cmd_setgain,seti=m.cmd_seti,setnestgain=m.cmd_setnestgain,setnesti=m.cmd_setnesti,getvs=m.cmd_getvs,gettemp=m.cmd_gettemp,getresistance=m.cmd_getresistance,lqgstart=m.cmd_lqgstart,lqgsilent=m.cmd_lqgsilent,lqgverbose=m.cmd_lqgverbose,startrec=m.cmd_startrec,stoprec=m.cmd_stoprec,lqgstop=m.cmd_lqgstop,pidstart=m.cmd_pidstart,pidstop=m.cmd_pidstop,cryostart=m.cmd_cryostart,cryostop=m.cmd_cryostop,setpoint=m.cmd_setpoint)
        commands = the_command.split()
        #Make sure we ignore case.
        commands[0] = commands[0].lower()
        if len(commands) == 0:
            return ""
        if commands[0] == "help":
            if (len(commands) == 1):
                return '** Available Commands **\nexit\nopen\ninitialize\nclose\nheater\nsetgain\nseti\nsetnestgain\nsetnesti\ngetvs\ngettemp\ngetresistance\nlqgstart\nlqgsilent\nlqgverbose\nstartrec\nstoprec\nlqgstop\npidstart\npidstop\ncryostart\ncryostop\nsetpoint\n'
            elif commands[1] in the_functions:
                td=pydoc.TextDoc()
                return td.docroutine(the_functions[commands[1]])
            else:
                return "ERROR: "+commands[1]+" is not a valid command."
        elif commands[0] == 'exit' or commands[0] == 'bye' or commands[0] == 'quit':
            return -1
        elif commands[0] in the_functions:
            return the_functions[commands[0]](the_command)
        else:
            return "ERROR: Command not found - {0:s} ".format(commands[0])

