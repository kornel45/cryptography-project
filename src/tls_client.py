import socket
import ssl
import threading
from src.port import port
import os

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
port = port

local = os.getcwd()
CLIENT_CERT = os.path.join(local, 'client_data/client2/client.pem')
CLIENT_KEY = os.path.join(local, 'client_data/client2/client.key')
SERVER_CERT = os.path.join(local, 'server_data/server.pem')

uname = input("Enter user name::")

ip = '127.0.1.1'
s.setblocking(1)


context = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
context.verify_mode = ssl.CERT_REQUIRED
context.load_verify_locations(SERVER_CERT)
context.load_cert_chain(certfile=CLIENT_CERT, keyfile=CLIENT_KEY)

if ssl.HAS_SNI:
    secure_sock = context.wrap_socket(s, server_side=False, server_hostname=ip)
else:
    secure_sock = context.wrap_socket(s, server_side=False)

secure_sock.connect((ip, port))
secure_sock.send(uname.encode('ascii'))

clientRunning = True


def receiveMsg(sock):
    server_down = False
    while clientRunning and (not server_down):
        try:
            msg = sock.read(1024).decode('ascii')
            print(msg)
        except:
            print('Server is Down. You are now Disconnected. Press enter to exit...')
            server_down = True


threading.Thread(target=receiveMsg, args=(secure_sock,)).start()
while clientRunning:
    tempMsg = input()
    msg = uname + '>>' + tempMsg
    if '\quit' in msg:
        clientRunning = False
        secure_sock.write(r'\quit'.encode('ascii'))
    else:
        secure_sock.write(msg.encode('ascii'))
