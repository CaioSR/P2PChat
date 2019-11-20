import socket
import threading
import sys
import time
from random import randint
import json

class Client:
    peers = []
    connections = []

    def __init__(self, address):

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.connect(address)
        
        self.connections.append(sock)

        time.sleep(1)

        if len(self.connections) == 1:
            self.user = input('Input your username: ')
            sock.send(self.user.encode())
            response = sock.recv(1024)
            print(response.decode())

        
        iThread = threading.Thread(target=self.listenMsg, args=(sock,))
        iThread.daemon = True
        iThread.start()

        time.sleep(2)
        print('[Help]>> Type -con <IP>:<PORT> to connect to a peer')

        try:
            while True:
                msg = input()

                if msg[:5] == '-con ':
                    self.connectToPeer(msg[5:])

                else:
                    for conn in self.connections:
                        conn.send(msg.encode())
        except:
            exit()

    def listenMsg(self, sock):

        while True:
            
            data = sock.recv(1024)

            if not data:
                break

            elif data[:1].decode() == '\x11':
                self.receivePeers(data[1:].decode())

            else:
                print(data.decode())
        
    def receivePeers(self, peers):
        self.peers = json.loads(peers)
        print('[Client]>> Received Peers from Server:', self.peers)

    def connectToPeer(self, addr):

        addr = addr.split(':')

        peer = {
            'ip' : addr[0],
            'port' : addr[1]
        }

        if peer in self.peers:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.connect((peer['ip'], int(peer['port'])))
            time.sleep(1)
            sock.send(self.user.encode())
            self.connections.append(sock)
            print('Added Connection to', peer)

            lThread = threading.Thread(target=self.listenMsg, args=(sock,))
            lThread.daemon = True
            lThread.start()
        else:
            print('Couldn\'t find typed peer')





if __name__== '__main__':
    client = Client('127.0.0.1')
