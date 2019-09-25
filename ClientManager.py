from Client import Client
from Authorizer import Authorizer
from typing import Dict
import socket
import select
from Response import Response


class ClientManager:
    def __init__(self):
        self.authorizer = Authorizer("auth_info.json")

        self.sockets: Dict[int, socket.socket] = {}  # fileno : sock

        self.clients: Dict[int, Client] = {}  # fileno : client
        self.authorized_clients: Dict[str, Client] = {}  # username : client

        self.poller = select.poll()

    def client_exists(self, sock: socket.socket):
        return sock.fileno() in self.clients

    def create_client(self, sock: socket.socket):
        if self.client_exists(sock):
            return

        client = Client(sock)

        self.clients[sock.fileno()] = client
        self.sockets[sock.fileno()] = sock
        self.poller.register(sock, select.POLLIN)

        print(str(client), "connected.")

    def login_client(self, client: Client, username: str):
        self.authorized_clients[username] = client
        client.set_authorized(username)

        print(str(client), "authorized.")

    def remove_client(self, client: Client):
        self.clients.pop(client.sock.fileno(), None)
        if client.username:
            self.authorized_clients.pop(client.username, None)
        self.sockets.pop(client.sock.fileno(), None)
        self.poller.unregister(client.sock.fileno())

        client.sock.send(b'')
        client.sock.close()

        print(str(client), "disconnected.")

    def broadcast(self, response: Response):
        for client in self.authorized_clients.values():
            client.send_response(response)
