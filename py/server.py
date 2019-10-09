import socket
import sys

BUFFER_SIZE = 1024
s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s.bind(('',10000))
s.listen(1)

conn, addr = s.accept()
print 'Connection address:', addr
while 1:
	data = conn.recv(BUFFER_SIZE)
	if not data: break
	print 'received data: ', data
	conn.send(data)
conn.close

