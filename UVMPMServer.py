from ConnectionManager import ConnectionManager
import socket
import select


class UVMPMServer:
    BUFFER_SIZE = 4096

    def __init__(self, host="0.0.0.0", port=1143):
        self.host = host
        self.port = port

        self.connection_manager = ConnectionManager()

        self.listening_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.listening_socket.bind((self.host, self.port))

        self.poller = select.poll()
        self.poller.register(self.listening_socket, select.POLLIN)

        self.sockets = {}  # fileno : socket

    def run(self):
        self.listening_socket.listen()
        print("Listening on port", self.port)

        self.sockets[self.listening_socket.fileno()] = self.listening_socket

        while True:
            for fd, event in self.poller.poll():
                sock = self.sockets[fd]
                if sock is self.listening_socket:
                    sock, address = self.listening_socket.accept()
                    sock.setblocking(False)
                    self.sockets[sock.fileno()] = sock
                    self.poller.register(sock, select.POLLIN)

                elif event & select.POLLIN:
                    incoming_data = sock.recv(self.BUFFER_SIZE)
                    if len(incoming_data) == 0:
                        self.poller.modify(sock, select.POLLHUP)
                        continue

                    try:
                        self.handle_data(sock, incoming_data.decode("ascii").strip())
                    except Exception:
                        pass

                elif event & (select.POLLHUP | select.POLLERR | select.POLLNVAL):
                    self.disconnect(sock)
