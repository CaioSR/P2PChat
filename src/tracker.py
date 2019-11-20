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

                # if data.decode() == 'get':
                #     self.sendPeers(conn)

                if data[:3].decode() == 'set':
                    peer = json.loads(data[3:].decode())
                    self.addPeer(peer)

                elif not data:
                    print('[Tracker]>> ' + str(addr[0]) + ':' + str(addr[1]) + ' disconnected')
                    self.connections.remove(conn)
                    conn.close()
                    break

        except:
            exit()

    def sendPeers(self, conn):
        data = json.dumps(self.peers)
        conn.send(data.encode())

    def addPeer(self, peer):


        if peer not in self.peers:
            
            self.peers.append(peer)

            print('[Tracker]>> Current Peers:', self.peers)

            for conn in self.connections:
                self.sendPeers(conn)
            

       
if __name__ == '__main__':
    tracker = Tracker()