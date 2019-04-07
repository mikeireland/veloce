#!/usr/bin/env python
from __future__ import print_function, division
import sys
import string
import select
import socket
import numpy as np
import zlib
import pdb
import time
import zmq
import json
import struct
SECRET_CODE = 314159

class ClientSocket:
    """This is copied to macquarie-observatory-automation/common"""
    MAX_BUFFER = 65536
    def __init__(self,IP="127.0.0.1",Port="3000"): #!!! Set this below - not here !!!
        #NB See the prototype in macquarie-university-automation for a slightly neater start.
        ADS = (IP,Port)
        self.count=0
        try:
            self.context = zmq.Context()
            self.client = self.context.socket(zmq.REQ)
            tcpstring = "tcp://"+IP+":"+Port
            print(tcpstring)
            self.client.connect(tcpstring)
            self.client.RCVTIMEO = 5000
            self.connected=True
        except: 
            print('ERROR: Could not connect to server. Please check that the server is running and IP is correct.')
            self.connected=False

    def send_command(self, command):
        """WARNING: Currently an occasional issue where the server just doesn't respond.
        No idea why..."""
        if (self.connected==False) and (len(command)==0):
            try:
                response = self.client.recv(self.MAX_BUFFER,zmq.NOBLOCK)
            except:
                self.count += 1
                return "Could not receive buffered response - connection still lost ({0:d} times).".format(self.count)
            self.connected=True
            return "Connection re-established!"
        
        #Send a command to the client.
        try: 
            command_with_code = bytearray(struct.pack("<I", SECRET_CODE))
            command_with_code.extend(command.encode())
            self.client.send(command_with_code,zmq.NOBLOCK)
        except:
            self.connected=False 
            self.count += 1
            return 'Error sending command, connection lost ({0:d} times).'.format(self.count)
        
        #Receive the response
        try:
            response = self.client.recv(self.MAX_BUFFER,zmq.NOBLOCK)
            self.connected=True
            data_type = struct.unpack("<I", response[:4])[0]
            #From server_socket:
            #DTYPES = {str:0, int:1, float:2, "image":3}
            if data_type==0:
                return response[4:]
            elif data_type==1:
                return struct.unpack("i", response[4:])
            elif data_type==2:
                return struct.unpack("f", response[4:])
            else:
                raise UserWarning("Unsupported data type")
        except:
            self.connected=False 
            self.count += 1
            return 'Error receiving response, connection lost ({0:d} times)\nPress Enter to reconnect.'.format(self.count)