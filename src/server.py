import socket
import threading
import sys
import time
from random import randint
import json

class Server:
    connections = []
    peers = []
    clients = []
    def __init__(self, port):

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(('', port))
        sock.listen()

        print('Server running ...')

        tracker = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tracker.connect(('127.0.0.1', 5000))

        print('Connected to tracker ...')

        self.retrievePeers(tracker)

        pThread = threading.Thread(target=self.listenTracker, args=(tracker,))
        pThread.daemon = True
        pThread.start()

        time.sleep(1)

        while True:

            conn, addr = sock.accept()

            data = conn.recv(1024)
            user = data.decode()

            self.clients.append({
                'username' : user,
                'ip' : addr[0],
                'port' : addr[1]
            })

            msg = '[Server]>> Welcome, ' + user
            conn.send(msg.encode())

            cThread = threading.Thread(target=self.receiver, args=(conn, addr))
            cThread.daemon = True
            cThread.start()

            self.connections.append(conn)
            self.updatePeers(tracker, conn.getsockname())
            print('[Server]>> ' + str(addr[0]) + ':' + str(addr[1]) + ' connected')

    def retrievePeers(self, tracker):
        tracker.send(b'get')

        data = tracker.recv(1024)
        jsonData = data.decode()
        self.peers = json.loads(jsonData)

        print('[Server]>> Received Peers from Tracker:', self.peers)

    def sendPeers(self):
        peers = json.dumps(self.peers)
        msg = ('\x11' + peers).encode()

        for connections in self.connections:
            connections.send(msg)

    def updatePeers(self, tracker, addr):
        peer = {
            'ip' : addr[0],
            'port' : str(addr[1])
        }
        peer = json.dumps(peer)
        msg = ('set' + peer).encode()
        tracker.send(msg)

    def listenTracker(self, tracker):

        while True:

            data = tracker.recv(1024)
            jsonData = data.decode()
            self.peers = json.loads(jsonData)

            print('[Server]>> Received Peers from Tracker:', self.peers)

            self.sendPeers()

    def removeClient(self, addr):
        for client in self.clients:
            if client['ip'] == addr[0] and client['port'] == addr[1]:
                self.clients.remove(client)
                return client['username']

    def receiver(self, conn, addr):
        try:
            while True:

                data = conn.recv(1024)

                if data.decode() == 'q':
                    print('[Server]>> ' + str(addr[0]) + ':' + str(addr[1]) + ' disconnected')
                    self.connections.remove(conn)
                    user = self.removeClient(addr)
                    msg = '[Server]>> ' + user + ' left.'
                    conn.close()
                    break

                else:
                    for connection in self.connections:
                        if connection != conn:

                            for client in self.clients:
                                if client['ip'] == addr[0] and client['port'] == addr[1]:
                                    user = client['username']
                                    break

                            msg = '['+user+']>> ' + data.decode()
                            connection.send(msg.encode())

        except:
            exit()


    