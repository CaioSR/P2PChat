import socket
import threading
import sys
import time
from random import randint
import json
import rsa
import aes

class Peer:

    # recupera o ip local
    ip = socket.gethostbyname(socket.gethostname())
    peers = []
    connection = {}

    def __init__(self, port):

        self.private_key, self.public_key = rsa.generateKey()

        # inicia o servidor
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(('', port))
        sock.listen(1)

        self.user = input('Input your username: ')

        # conecta ao tracker
        tracker = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tracker.connect(('127.0.0.1', 32500))

        self.tracker_handshake(tracker)

        print('Connected to tracker ...')

        # atualiza o tracker com as informações de conexão desse servidor
        self.updatePeers(tracker, port)

        # cria uma nova thread para escutar mensagens do tracker
        pThread = threading.Thread(target=self.listenTracker, args=(tracker,))
        pThread.daemon = True # finaliza a thread caso a principal encerre
        pThread.start()

        time.sleep(1)

        # cria uma nova thread para enviar mensagens
        mThread = threading.Thread(target=self.sendMsg, args=(tracker,))
        mThread.daemon = True
        mThread.start()

        print('[Client]>> Type -con <user> to connect to a peer')

        # loop para escutar novas conexões
        while True:

            conn, addr = sock.accept()

            # caso já exista uma conexão, a existente é encerrada e substuída pela nova
            if self.connection:
                print('Someone interrupted your connection.')
                print('Your connection with ' + self.connection['user'] + ' will be terminated.')
                msg = rsa.encrypt(self.connection['pKey'], b'-q')
                self.connection['conn'].send(msg)
                self.connection['conn'].close()
                self.connection = {}

            self.getConnHandshake(conn)

            # recebe dados na nova conexão. Normalmente o nome do usuário
            cripted_data = conn.recv(1024)
            user = rsa.decrypt(self.private_key, cripted_data).decode()

            # atribui os valores da nova conexão
            self.connection['user'] = user
            self.connection['conn'] = conn
            
            print('[Client]>> ' + addr[0] + ':' + str(addr[1]) + ' connected')
            print('[Client]>> Send Hi to', self.connection['user'])

            # cria uma nova thread para escutar mensagens da conexão
            cThread = threading.Thread(target=self.handler)
            cThread.daemon = True
            cThread.start()

    def tracker_handshake(self, tracker):
        data = tracker.recv(1024)
        tracker_public_key = rsa.deserialize(data)

        self.simKey = aes.generateKey()

        cripted_simKey = rsa.encrypt(tracker_public_key, self.simKey) 
        tracker.send(cripted_simKey)

    def updatePeers(self, tracker, port):
        """
        Método para enviar uma mensagem ao tracker para atualizar a lista de peers
        """

        # o novo peer contém: usuário, ip e porta para escutar novas conexões
        peer = {
            'user' : self.user,
            'ip' : self.ip,
            'port' : str(port),
        }

        # joga o dicionário num arquivo json
        peer = json.dumps(peer)

        # envia a mensagem com o prefixo -set
        msg = ('-set ' + peer).encode()

        cripted_msg = aes.encrypt(self.simKey, msg) ###########
        tracker.send(cripted_msg)

        print('[Client]>> Requested Peers')

    def sendMsg(self, tracker):
        """
        Método para enviar mensagens, seja para o tracker, seja para outro peer
        """
        try:
            while True:
                msg = input()

                # caso a mensagem possua esse prefixo, ela será enviada ao tracker
                if msg[:5] == '-con ':
                    cripted_msg = aes.encrypt(self.simKey, msg.encode()) ######
                    tracker.send(cripted_msg)

                # caso comece com -q, enviará o código ao outro peer e encerrará a conexão
                elif msg == '-q':
                    cripted_msg = rsa.encrypt(self.connection['pKey'], msg.encode())
                    self.connection['conn'].send(cripted_msg)
                    self.connection['conn'].close()
                    self.connection = {}
                    print('You left the chat.')
                    print('[Client]>> Current peers list:', self.peers)
                    print('[Client]>> Type -con <user> to connect to a peer')

                # senão é uma mensagem normal e envia para o outro peer
                elif self.connection:
                    cripted_msg = rsa.encrypt(self.connection['pKey'], msg.encode())
                    self.connection['conn'].send(cripted_msg)
        except:
            exit()


    def listenTracker(self, tracker):
        """
        Método para escutar mensagens do tracker
        """
        while True:

            cripted_data = tracker.recv(1024)
            data = aes.decrypt(self.simKey, cripted_data).decode() 

            # caso possua prefixo -set, stá recebendo uma lista atualizada de peers
            if data[:5]== '-set ':
                peers = data[5:]

                # cria uma lista de dicionários a partir do arquivo json
                self.peers = json.loads(peers)

                print('[Client]>> Received Peers from Tracker:', self.peers)

            # se possuir prefixo -acc a solicitação de conexão com outro peer foi aceita
            elif data[:5] == '-acc ':
                contactInfo = data[5:]
                contactInfo = json.loads(contactInfo)

                if self.connection:
                    print('You already have an active conection with ' + self.connection['user'])
                    print('It will be terminated')
                    msg = rsa.encrypt(self.connection['pKey'], b'-q')
                    self.connection['conn'].send(msg)
                    self.connection['conn'].close()
                    self.connection = {}

                print('[Client]>> ' + contactInfo['user'] + ' accepted your invite.')
                print('Connecting...')

                # cria a nova conexão com o outro peer
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                sock.connect((contactInfo['ip'], int(contactInfo['port'])))

                self.createConnHandshake(sock)

                # atualiza a conexão ativa
                self.connection['user'] = contactInfo['user']
                self.connection['conn'] = sock

                # envia a essa nova conexão seu nome de usuário
                msg = rsa.encrypt(self.connection['pKey'], self.user.encode())
                sock.send(msg)

                print('[Client]>> You are now connected to', contactInfo['user'])

                # cria a thread para escutar essa conexão
                lThread = threading.Thread(target=self.handler)
                lThread.daemon = True
                lThread.start()

    def createConnHandshake(self, conn):
        conn.send(rsa.serialize(self.public_key))

        cripted_key = conn.recv(1024)
        self.connection['pKey'] = rsa.deserialize(cripted_key)

    def getConnHandshake(self, conn):
        cripted_key = conn.recv(1024)
        self.connection['pKey'] = rsa.deserialize(cripted_key)

        conn.send(rsa.serialize(self.public_key))

    def handler(self):
        """
        Método para escutar mensagens da conexão com outro peer
        """
        try:
            while True:

                cripted_data = self.connection['conn'].recv(1024)
                data = rsa.decrypt(self.private_key, cripted_data).decode()

                # se a mensagem possuir prefixo -q, o outro encerrou a conexão
                if data == '-q':
                    print('[Client]>> ' + self.connection['user'] + ' left the chat.')
                    self.connection['conn'].close()
                    self.connection = {}
                    print('[Client]>> Current peers list:', self.peers)
                    print('[Client]>> Type -con <user> to connect to a peer')
                    break
                
                # senão é uma mensagem normal e a imprime
                else:
                    print('['+self.connection['user']+']>> ' + data)

        except:
            exit()