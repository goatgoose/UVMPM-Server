from typing import Dict
import socket


class ConnectionManager:
    def __init__(self):
        self.sockets: Dict[int, socket.socket] = {}
