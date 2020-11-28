import socket
import sys

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect the socket to the port where the server is listening
server_address = ('localhost', 10000)
print (sys.stderr, 'connecting to %s port %s' % server_address)
sock.connect(server_address)
aux = True

while aux:
    try:
        while aux:
            # Send data
            message = str(input('Comando> '))
            print (sys.stderr, 'sending "%s"' % message)
            if message == 'End':
                aux = False
            sock.sendall(message.encode('utf-8'))

            # Look for the response
            amount_received = 0

    finally:
        print (sys.stderr, 'closing socket')
        sock.close()