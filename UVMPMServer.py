import socket
import select


class UVMPMServer:
    BUFFER_SIZE = 4096

    def __init__(self, host="0.0.0.0", port=1142):
        self.host = host
        self.port = port

        self.listening_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.listening_sock.bind((self.host, self.port))

        self.sockets = {}  # fileno : socket
        self.unauthorized_sockets = {}  # fileno : sock
        self.authorized_sockets = {}  # fileno : sock

        self.authorized_clients = {}  # username : sock

        self.data_to_send = {}  # socket : data

        self.poller = select.poll()
        self.poller.register(self.listening_sock, select.POLLIN)

    def run(self):
        self.listening_sock.listen()
        print("Listening on port", self.port)

        self.sockets[self.listening_sock.fileno()] = self.listening_sock

        while True:
            for fd, event in self.poller.poll():
                sock = self.sockets[fd]
                if sock is self.listening_sock:
                    sock, address = self.listening_sock.accept()
                    sock.setblocking(False)
                    self.sockets[sock.fileno()] = sock
                    self.poller.register(sock, select.POLLIN)

                elif event & select.POLLIN:
                    incoming_data = sock.recv(self.BUFFER_SIZE)
                    if len(incoming_data) == 0:
                        self.poller.modify(sock, select.POLLHUP)
                        continue

                    self.handle_data(sock, incoming_data.decode("UTF-8"))

                elif event & select.POLLOUT:
                    data = self.data_to_send[sock]
                    bytes_sent = sock.send(data)
                    if bytes_sent < len(data):
                        self.data_to_send[sock] = data[bytes_sent:]
                    else:
                        self.data_to_send[sock] = b''
                        self.poller.modify(sock, select.POLLIN)

    def handle_data(self, sock, data):
        if data == "HELLO":
            self.send_message(sock, "HELLO")
        else:
            self.send_message(sock, "Unrecognized message.")

    def send_message(self, sock, message):
        self.data_to_send[sock] = self.data_to_send.pop(sock, b'') + message.encode()
        self.poller.modify(sock, select.POLLOUT)
        print(sock.fileno, "<-", message)

    def broadcast(self, message):
        for user in self.authorized_clients:
            sock = self.authorized_clients[user]
            self.send_message(sock, message)


if __name__ == '__main__':
    server = UVMPMServer()
    server.run()
