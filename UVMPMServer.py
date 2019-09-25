from ClientManager import ClientManager
from RequestManager import RequestManager
from RequestHandler import RequestHandler
import socket
import select


class UVMPMServer:
    BUFFER_SIZE = 4096

    def __init__(self, host="0.0.0.0", port=1145):
        self.host = host
        self.port = port

        self.client_manager = ClientManager()
        self.request_manager = RequestManager()

        self.request_handler = RequestHandler(self.client_manager)

        self.listening_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.listening_socket.bind((self.host, self.port))

        self.client_manager.poller.register(self.listening_socket, select.POLLIN)

    def run(self):
        self.listening_socket.listen()
        print("Listening on port", self.port)

        self.client_manager.sockets[self.listening_socket.fileno()] = self.listening_socket

        while True:
            for fd, event in self.client_manager.poller.poll():
                sock = self.client_manager.sockets[fd]
                if sock is self.listening_socket:
                    sock, address = self.listening_socket.accept()
                    sock.setblocking(False)
                    self.client_manager.create_client(sock)

                elif event & select.POLLIN:
                    incoming_data = sock.recv(self.BUFFER_SIZE)
                    if len(incoming_data) == 0:
                        self.client_manager.poller.modify(sock, select.POLLHUP)
                        continue

                    client = self.client_manager.clients.get(sock.fileno())
                    request = self.request_manager.get_request(client, incoming_data)
                    self.request_handler.handle(request)

                elif event & (select.POLLHUP | select.POLLERR | select.POLLNVAL):
                    client = self.client_manager.clients.get(sock.fileno())
                    self.client_manager.remove_client(client)
