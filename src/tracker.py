import socket
import threading
import sys
import time
from random import randint
import json

class Tracker:
    connections = []
    peers = []

    def __init__(self):

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(('', 5000))
        sock.listen()

        print('Tracker running ...')

        while True:
            conn, addr = sock.accept()

            tThread = threading.Thread(target=self.handler, args=(conn, addr))
            tThread.daemon = True
            tThread.start()

            self.connections.append(conn)

            print('[Tracker]>> ' + str(addr[0]) + ':' + str(addr[1]) + ' connected')

    def handler(self, conn, addr):
        try:
            while True:
                data = conn.recv(1024)
                print('[Tracker]>> Received Data', data.decode())

                if data.decode()[:5] == '-req ':
                    user = data.decode()[5:]
                    response = self.contactUser(user)

                    if response:
                        contactInfo = json.dumps(response[1])
                        msg = ('-acc ' + contactInfo).encode()
                        conn.send(contactInfo.encode())
                    else:
                        msg = '-denied'
                        conn.send(msg.encode())

                if data[:5].decode() == '-set ':
                    peer = json.loads(data[5:].decode())
                    self.addPeer(peer, conn)

                elif not data:
                    print('[Tracker]>> ' + str(addr[0]) + ':' + str(addr[1]) + ' disconnected')
                    self.removeConnection(conn)
                    conn.close()
                    break

        except:
            exit()

    def contactUser(self, user):
        peer = [p for p in self.peers if p['user'] == user]
        conn = [c for c in self.connections if peer in c][0][0]

        conn.send(('-inv ' + user).encode())

        response = conn.recv(1024).decode()
        if response[:2] == '-a':
            return True, peer
        elif response[:2] == '-b':
            return False
        else:
            return False
            
        

    def sendPeers(self, conn):
        # data = json.dumps(self.peers)
        data = []

        for user in self.peers:
            data.append(user['username'])

        conn.send(('-set ' + data).encode())

    def addPeer(self, peer, conn):

        if peer not in self.peers:
            index = self.connections.index(conn)
            self.connections[index] = (conn, peer)
            self.peers.append(peer)

            print('[Tracker]>> Current Peers:', self.peers)

            for conn in self.connections:
                self.sendPeers(conn)

    def removeConnection(self, conn):
        element = [el for el in self.connections if conn in el]
        self.peers.remove(element[1])
        self.connections.remove(element)
            

       
if __name__ == '__main__':
    tracker = Tracker()