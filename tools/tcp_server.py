import math
import time
import json

import socket
import _thread
import traceback



class TCPSocketServer(socket.socket):
    clients = []
    port = 9000
    host = '127.0.0.1'
    #Broadcasting to <LocalHost> over LAN reduced errors in payload

    def __init__(self, port):
        socket.socket.__init__(self)
        self.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.port = port
        self.host = TCPSocketServer.host
        self.bind((self.host,port))
        self.listen(5)

    def run(self):
        print('*** Server started at host:', self.host, ' port:', self.port)
        try:
            self.accept_clients()
        except Exception as ex:
            print(ex)
            traceback.print_exc()
        finally:
            print("*** Server closing")
            for client in self.clients:
                client.close()
            self.close()

    def run_thread(self):
        _thread.start_new_thread(self.run, ())

    def accept_clients(self):
        while True:
            (clientsocket, address) = self.accept()
            self.clients.append(clientsocket)
            self.onopen(clientsocket)
            _thread.start_new_thread(self.recieve, (clientsocket,))
            print('*** active clients:', self.clients)

    def recieve(self, client):
        while 1:
            data = client.recv(1024)
            if len(data) == 0:
                print('*** client dropped off')
                break
            self.onmessage(client, data)
        self.clients.remove(client)
        self.onclose(client)
        client.close()
        _thread.exit()
        print('*** active clients:', self.clients)

    def broadcast(self, message):
        message = message.encode()
        for client in self.clients:
            client.send(message)

    def onopen(self, client):
        pass

    def onmessage(self, client, message):
        pass

    def onclose(self, client):
        pass
