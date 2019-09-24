from Auth import Auth
import socket
import select


class UVMPMServer:
    BUFFER_SIZE = 4096

    def __init__(self, host="0.0.0.0", port=1143):
        self.host = host
        self.port = port

        self.auth = Auth("auth_info.json")

        self.listening_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.listening_sock.bind((self.host, self.port))

        self.sockets = {}  # fileno : socket
        self.unauthorized_sockets = set()
        self.authorized_sockets = set()  # sockets

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

                    try:
                        self.handle_data(sock, incoming_data.decode("ascii").strip())
                    except Exception:
                        pass

                elif event & (select.POLLHUP | select.POLLERR | select.POLLNVAL):
                    self.disconnect(sock)

    def handle_data(self, sock, data):
        if data == "HELLO":
            self.send_message(sock, "HELLO")
            if sock not in self.unauthorized_sockets.union(self.authorized_sockets):
                self.unauthorized_sockets.add(sock)
        elif data.startswith("AUTH:"):
            if sock not in self.unauthorized_sockets:
                self.send_message(sock, "Not yet greeted.")
                return
            elif sock in self.authorized_sockets:
                self.send_message(sock, "Already logged in.")
                return

            split = data.split(":")
            if len(split) != 3:
                self.send_message(sock, "Unrecognized message: " + data)
                return

            username = split[1]
            password = split[2]
            if self.auth.is_authorized(username, password):
                self.unauthorized_sockets.remove(sock)
                self.authorized_sockets.add(sock)
                self.authorized_clients[username] = sock

                self.send_message(sock, "AUTHYES")
                self.broadcast("SIGNIN:" + username)
            else:
                self.send_message(sock, "AUTHNO")
        elif data == "LIST":
            if sock not in self.authorized_sockets:
                self.send_message(sock, "Unauthorized.")
                return

            self.send_message(sock, ", ".join(self.authorized_clients.keys()))
        elif data.startswith("To:"):
            if sock not in self.authorized_sockets:
                self.send_message(sock, "Unauthorized.")
                return

            split = data.split(":")
            if len(split) != 3:
                self.send_message(sock, "Unrecognized message: " + data)
                return

            send_to = split[1]
            message = split[2]

            send_to_sock = self.authorized_clients.get(send_to)
            if not send_to_sock:
                self.send_message(sock, "User doesn't exist: " + send_to)
                return

            self.send_message(send_to_sock, "From:" + self.get_user(sock) + ":" + message)
        elif data == "BYE":
            if sock not in self.authorized_sockets:
                self.send_message(sock, "Unauthorized.")
                return

            user = self.get_user(sock)
            if user:
                self.broadcast("SIGNOFF:" + user)
                self.authorized_clients.pop(user)
            self.authorized_sockets.remove(sock)

            self.poller.unregister(sock.fileno())
            sock.send(b'')
            sock.close()
            del self.sockets[sock.fileno()]
        else:
            self.send_message(sock, "Unrecognized message: " + data)

    def send_message(self, sock, message):
        message += "\n"
        sock.send(message.encode("ascii"))
        self.poller.modify(sock, select.POLLIN)
        print(sock.fileno(), "<-", message)

    def broadcast(self, message):
        for user in self.authorized_clients:
            sock = self.authorized_clients[user]
            self.send_message(sock, message)

    def get_user(self, sock):
        # TODO double dictionary
        for user in self.authorized_clients:
            if sock == self.authorized_clients[user]:
                return user
        return None

    def disconnect(self, sock):
        self.poller.unregister(sock.fileno())
        sock.send(b'')
        sock.close()
        del self.sockets[sock.fileno()]
        print(sock.fileno(), "disconnected")


if __name__ == '__main__':
    server = UVMPMServer()
    server.run()
