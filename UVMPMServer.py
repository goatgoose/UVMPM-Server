import socket


class UVMPMServer:
    BUFFER_SIZE = 4096

    def __init__(self, host="0.0.0.0", port=1142):
        self.host = host
        self.port = port

        self.listening_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.listening_sock.bind((self.host, self.port))
