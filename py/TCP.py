import math
import re
import socket
import sys
import io
import time
import GlobalSettings
from GlobalSettings import TCPServer
from GlobalSettings import TCPClient
from GlobalSettings import IP_Address

class TCP:
    def __init__(self):
	self.Address = IP_Address
	self.Port = 10000
        self.s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
	self.buffer_size = 1024
        
	if TCPServer:
	    self.s.bind((self.Address,self.Port))
	    #self.s.settimeout(1)
	    self.s.listen(1)

    def server(self):
	#self.s.bind((self.Address,self.Port))
	#self.s.settimeout(1)
	#self.s.listen(1)
	conn,addr = self.s.accept()
	data = conn.recv(self.buffer_size)
#	if not data: break
	print 'received_data: ', data
	(x1,y1) = re.findall('\d+.\d+',data)
	conn.close() 
	return (float(x1),float(y1))	
#	self.s.close()

    def client(self):
        self.s = socket.socket()
	message = str(new[0]) + ',' + str(new[1])
	self.s.connect((self.Address,self.Port))
	self.s.send(message)
	data = self.s.serv(self.buffer_size)
	self.s.close()

    def talk(self):
        if TCPServer:
            self.server()
        else:
            self.client()
        
