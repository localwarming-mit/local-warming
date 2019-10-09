class TCPClient:
    def __init__(self, Address, Port):
	self.Address = Address
	self.Port = Port
        self.open_server()

    def open_server(self):
        # Create a TCP/IP socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Connect the socket to the port where the server is listening
        server_address = (self.Address, self.Port)
        print >>sys.stderr, 'connecting to %s port %s' % server_address
        self.sock.connect(server_address)

    def send(self, pts):
        try:
            i = 0
            for pt in pts:
                # the data should be sent as 3 comma separated values with a total length of 19 characters.
                # 1 for id, 8 for x, 8 for y
                # [ i,xxxxxxxx,yyyyyyyy ]
                message = '' + str(i) + ',' + ("%8f" % pt[0]) + ',' + ("%8f" % pt[1])

                # Send data
                sock.sendall(message)
                i = i + 1
                if(i == 10):
                    break
        except:
            pass


#tcpc = TCPClient('localhost', 4558)
