import socket
import ssl
import threading
import os
from src.port import port

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serverRunning = True
ip = '127.0.1.1'

local = os.getcwd()
SERVER_CERT = os.path.join(local, 'server_data/server.pem')
SERVER_KEY = os.path.join(local, 'server_data/server.key')
CLIENT_CERT = os.path.join(local, 'client_data/client1/client.pem')

clients = {}

s.bind((ip, port))
s.listen()


print('Server Ready...')
print('Ip Address of the Server::%s' % ip)


def handle_client(client, uname):
    client_connected = True
    keys = clients.keys()
    help = 'There are four commands in Messenger\n' \
           '1::\chatlist=>gives you the list of the people currently online\n' \
           '2::\quit=>To end your session\n' \
           '3::\\broadcast=>To broadcast your message to each and every person currently present online\n' \
           '4::Write \\[name] on the beggining of your message to send it to someone called [name]'

    while client_connected:
        try:
            msg = client.recv(1024).decode('ascii')
            response = ''
            found = False
            if r'\chatlist' in msg:
                clientNo = 0
                for name in keys:
                    clientNo += 1
                    response = response + str(clientNo) + '::' + name + '\n'
                client.send(response.encode('ascii'))
            elif r'\help' in msg:
                client.send(help.encode('ascii'))
            elif r'\broadcast' in msg:
                msg = msg.replace(r'\broadcast', '')
                for k, v in clients.items():
                    v.send(msg.encode('ascii'))
            elif r'\quit' in msg:
                response = 'Stopping Session and exiting...'
                client.send(response.encode('ascii'))
                clients.pop(uname)
                print(uname + ' has been logged out')
                client_connected = False
            else:
                for name in keys:
                    if ('\\' + name) in msg:
                        msg = msg.replace('\\' + name, '')
                        clients.get(name).send(msg.encode('ascii'))
                        found = True
                if not found:
                    client.write('Trying to send message to invalid person.'.encode('ascii'))
        except:
            clients.pop(uname)
            print(uname + ' has been logged out')
            client_connected = False


while serverRunning:
    client, address = s.accept()
    secure_sock = ssl.wrap_socket(client, server_side=True, certfile=SERVER_CERT, keyfile=SERVER_KEY,
                                  ca_certs=CLIENT_CERT, cert_reqs=ssl.CERT_REQUIRED, ssl_version=ssl.PROTOCOL_TLSv1)

    uname = secure_sock.read(1024).decode('ascii')
    print('%s connected to the server' % str(uname))
    secure_sock.write(r'Welcome to Messenger. Type \help to know all the commands'.encode('ascii'))

    if secure_sock not in clients:
        clients[uname] = secure_sock
        threading.Thread(target=handle_client, args=(secure_sock, uname,)).start()

