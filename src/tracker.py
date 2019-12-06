import socket
import threading
import sys
import time
from random import randint
import json
import rsa
import aes

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

            self.connections.append(conn)
            self.handshake(conn)
            
            # cria a thread para escutar mensagens da conexão
            tThread = threading.Thread(target=self.handler, args=(conn, addr))
            tThread.daemon = True
            tThread.start()

            print('[Tracker]>> ' + str(addr[0]) + ':' + str(addr[1]) + ' connected')

    def handshake(self, conn):
        conn.send(rsa.serialize(self.public_key))

        cripted_data = conn.recv(1024)
        simKey = rsa.decrypt(self.private_key, cripted_data)

        cIndex = self.connections.index(conn)
        self.connections[cIndex] = (conn, simKey) 

        print('[Tracker]>> Estabilished Symmetric Key: ', simKey)


    def handler(self, conn, addr):
        """
        Esse método escuta mensagens dos clientes
        """
        try:

            key = [c for c in self.connections if c[0] == conn][0][1]
            
            while True:
                
                cripted_data = conn.recv(1024)
                data = aes.decrypt(key, cripted_data).decode() 

                print('[Tracker]>> Received Data', data)

                # se a mensagem possuir prefixo -set é um novo peer se conetando e deve atualizar a lista de peers
                if data[:5] == '-set ':
                    peer = json.loads(data[5:])

                    if peer not in self.peers:
                        self.peers.append(peer)
                        print('[Tracker]>> Current Peers:', self.peers)

                        # com a lista atualizada, as listas dos clientes também devem ser atualizadas
                        self.sendPeers()

                # se a mensagem possuir prefixo -con é uma solicitação de um usuário para se conectar a outro
                elif data[:5] == '-con ':
                    user = data[5:]

                    # busca esse usuário na lista de peers para recuperar os dados para conexão
                    peer = [p for p in self.peers if p['user'] == user][0]

                    contactInfo = json.dumps(peer)
                    
                    # adiciona o prefixo -acc junto dos dados e envia ao solicitante
                    msg = ('-acc ' + contactInfo).encode()
                    cripted_msg = aes.encrypt(key, msg) 
                    conn.send(cripted_msg)
                    time.sleep(1)

        except:
            exit()
    
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

        for conn in self.connections:
            cripted_msg = aes.encrypt(conn[1], msg) ########
            conn[0].send(cripted_msg)

        print('[Tracker]>> Sent peers')

       
if __name__ == '__main__':
    tracker = Tracker()