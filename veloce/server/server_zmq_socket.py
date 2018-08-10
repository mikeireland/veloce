"""This python object is designed to take as inputs a socket number, a server name
and a hardware object, and to do all communication in the same way for all servers.

It is based on Ian Price's ZMQ standards in his C++ codes.
"""

from __future__ import division, print_function

import sys, time
import string
import zmq
import select
from datetime import datetime
import struct
import pdb

DEBUG=True
SECRET_CODE = 314159
DTYPES = {str:0, int:1, float:2, "image":3}

class ServerSocket:
    #Some properties needed by multiple methods.
    clients=[]
    jobs=[]
    def __init__(self, port, hardware_name, command_list, include_stdin=False):
        """A ZMQ socket  """
        try:
            self.context = zmq.Context()
            self.server = self.context.socket(zmq.REP)
            tcpstring = "tcp://*:"+str(port)
            print(tcpstring)
            self.server.bind(tcpstring)
            self.poller = zmq.Poller()
            self.poller.register(self.server, zmq.POLLIN)
            self.connected=True
        except: 
            print('ERROR: Could not initiate server socket.')
            self.connected=False
    
        #Set up the list of commands
        self.command_list = command_list
        #Set up the object "hardware_name" 
        self.hardware_name=hardware_name
        #Still use an input array, even though this is text only now.
        if include_stdin:
            self.input = [sys.stdin]
        else:
            self.input=[]

#This method deals with the various inputs from stdin and connected clients
    def socket_funct(self, s):
        if s == self.server:
        #handle server socket
            return s.recv()
        elif s == sys.stdin:
        #handle standard input
            return sys.stdin.readline()
        else:
        #shouldn't happen
            raise UserWarning

#We will use this to log what is happening in a file with a timestamp, but for now, print to screen
#I should also add something to document which client sent which command
    def log(self, message):
        print(str(datetime.now())+" "+str(message))

#This closes the connections to the cliente neatly.
    def close(self):
        self.server.close

#This medhod adds a new job to the queue.
    def add_job(self, new_job):
        self.jobs.append(new_job)

#This method runs the jobs and waits for new input
    def run(self):
        self.log("Waiting for connection, number of clients connected: "+str(len(self.clients)))
        running=True
        while running:
            time.sleep(0.1)
            inputready,outputready,exceptready = select.select(self.input,[],[],0)
            #pdb.set_trace()
            if self.connected:
                socks = dict(self.poller.poll(10))
                if self.server in socks and socks[self.server] == zmq.POLLIN:
                    inputready.append(self.server)
            for s in inputready:  #loop through our array of sockets/inputs
                data = self.socket_funct(s)
                if data == -1:
                    running=False
                elif data != 0:
                    #Now we check the command structure and deal with it appropriately
                    if s!=sys.stdin:
                        if (struct.unpack("<I", data[:4])[0]!=SECRET_CODE):
                            print("Error - client with incorrect secret code.")
                            continue
                        data=data[4:]
                    response = self.command_list.execute_command(data)
                    if response == -1:
                        running=False
                        if s == sys.stdin:
                            self.log("Manually shut down. Goodbye.")
                        else:
                            self.log("Shut down by remote connection. Goodbye.")
                    else:
                        if s==sys.stdin:
                            if type(response)==str:
                                print(response)
                            else:
                                print("Terminal can only print string responses!")
                        else:
                            if type(response)==str:                      
                                s.send(struct.pack("I", DTYPES[str]) + response)
                            elif type(response)==int:
                                s.send(struct.pack("I", DTYPES[int]) + struct.pack("I", response))
                            elif type(response)==float: 
                                s.send(struct.pack("I", DTYPES[float]) + struct.pack("f", response))
                            elif type(response)==tuple:
                                #WARNING: Error checking needed here!
                                s.send(struct.pack("I", DTYPES[response[0]]) + response[1])
                            else:
                                print("WARNING: Unknown response type!")
                                s.send("")
            for the_job in self.jobs:
                if DEBUG:
                    message=the_job()
                else:
                    try: message=the_job()
                    except:
                        raise UserWarning('Unable to do the '+the_job.__name__+' function. Check if the hardward needed is connected.')
                if message:
                    print(message)
                    #ISSUE: No way to get these messages to clients with the client-server model.
                    #Resolve this with a status command, e.g. returning json name-value pairs.
                    #for i in self.clients:
                    #    i.send(message)

