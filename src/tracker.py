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

        # inicia o servidor
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(('', 32500))
        sock.listen(1)

        print('Tracker running ...')

        while True:
            conn, addr = sock.accept()

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
                print('[Tracker]>> Received Data', data.decode())

                # se a mensagem possuir prefixo -con é uma solicitação de um usuário para se conectar a outro
                if data.decode()[:5] == '-con ':
                    user = data.decode()[5:]

                    # busca esse usuário na lista de peers para recuperar os dados para conexão
                    peer = [p for p in self.peers if p['user'] == user][0]

                    contactInfo = json.dumps(peer)

                    # adiciona o prefixo -acc junto dos dados e envia ao solicitante
                    conn.send(('-acc ' + contactInfo).encode())

                # se a mensagem possuir prefixo -set é um novo peer se conetando e deve atualizar a lista de peers
                elif data[:5].decode() == '-set ':
                    peer = json.loads(data[5:].decode())
                    self.addPeer(peer)

                # se não foi nada é uma desconexão (não funciona)
                elif not data:
                    print('[Tracker]>> ' + str(addr[0]) + ':' + str(addr[1]) + ' disconnected')
                    self.connections.remove(conn)
                    conn.close()
                    break

        except:
            exit()

    def addPeer(self, peer):
        """
        Esse método adiciona um peer a lista de peers
        """

        if peer not in self.peers:
            self.peers.append(peer)

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
        print('[Tracker]>> Sending peers')

        for conn in self.connections:
            conn.send(('-set ' + data).encode())



       
if __name__ == '__main__':
    tracker = Tracker()