import socket
import sys
import time
import queue
import threading

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to the port
server_address = ('localhost', 10000)
print (sys.stderr, 'starting up on %s port %s' % server_address)
sock.bind(server_address)

# Listen for incoming connections
sock.listen(1)
q = queue.Queue()
connection, client_address = sock.accept()
print('Connection accepted')

def hearqueue():
    inLoop = True
    while inLoop:
        print('in queue loop')
        data = connection.recv(100)
        command = data.decode('utf-8')
        # If server reads end then close the connection
        if(command == 'end'):
            time.sleep(1)
            inLoop=False
        q.put(command)
        #break

listenT = threading.Thread(target=hearqueue, daemon=True)

listenT.start()

listenT.join()
print('Thread termina')

print(q.qsize())
while (not q.empty()):
    comando = q.get()
    print(comando)
    

#finally:
        # Clean up the connection
connection.close()