import socket
import threading
import sys
import time
from random import randint
import json
import rsa

class Tracker:
    connections = []
    peers = []

    def __init__(self):

        # inicia o servidor
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(('', 32500))
        sock.listen(1)

        print('Tracker running ...')

        self.private_key, self.public_key = rsa.generateKey()

        while True:
            conn, addr = sock.accept()

            conn.send(rsa.serialize(self.public_key))

            # cria a thread para escutar mensagens da conexão
            tThread = threading.Thread(target=self.handler, args=(conn, addr))
            tThread.daemon = True
            tThread.start()

            self.connections.append(conn)

            print('[Tracker]>> ' + str(addr[0]) + ':' + str(addr[1]) + ' connected')

    def handler(self, conn, addr):
        """
        Esse método escuta mensagens dos clientes
        """
        try:
            
            while True:
                
                data = conn.recv(1024)
                plain_data = rsa.decrypt(self.private_key, data)
                data = plain_data.decode()

                print('[Tracker]>> Received Data', data)

                # se a mensagem possuir prefixo -con é uma solicitação de um usuário para se conectar a outro
                if data[:5] == '-con ':
                    key = [c for c in self.connections if c[0] == conn][0][1]

                    user = data[5:]

                    # busca esse usuário na lista de peers para recuperar os dados para conexão
                    peer = [p for p in self.peers if p['user'] == user][0]
                    peerPubKey = peer['pKey']
                    del peer['pKey']

                    contactInfo = json.dumps(peer)

                    
                    # adiciona o prefixo -acc junto dos dados e envia ao solicitante
                    msg = ('-acc ' + contactInfo).encode()
                    cripted_msg = rsa.encrypt(key, msg)
                    conn.send(cripted_msg)
                    time.sleep(1)
                    conn.send(peerPubKey)
                    
                # se a mensagem possuir prefixo -set é um novo peer se conetando e deve atualizar a lista de peers
                elif data[:5] == '-set ':
                    peer = json.loads(data[5:])
                    pKey = conn.recv(1024)
                    self.addPeer(peer, conn, pKey)

                # se não foi nada é uma desconexão (não funciona)
                elif not data:
                    print('[Tracker]>> ' + str(addr[0]) + ':' + str(addr[1]) + ' disconnected')
                    self.connections.remove(conn)
                    conn.close()
                    break

        except:
            exit()

    def addPeer(self, peer, conn, pKey):
        """
        Esse método adiciona um peer a lista de peers
        """

        peer['pKey'] = pKey

        if peer not in self.peers:
            self.peers.append(peer)
            cIndex = self.connections.index(conn)
            self.connections[cIndex] = (conn, rsa.deserialize(pKey))

            print('[Tracker]>> Current Peers:', self.peers)

            # com a lista atualizada, as listas dos clientes também devem ser atualizadas
            self.sendPeers()
            
    
    def sendPeers(self):
        """
        Esse método envia uma lista de usuários aos peers
        """
        data = []

        # cria uma lista de nome de usuários dos peers
        for user in self.peers:
            data.append(user['user'])

        data = json.dumps(data)
        msg = ('-set ' + data).encode()

        print('[Tracker]>> Sending peers')

        for conn in self.connections:
            cripted_msg = rsa.encrypt(conn[1], msg)
            conn[0].send(cripted_msg)

       
if __name__ == '__main__':
    tracker = Tracker()