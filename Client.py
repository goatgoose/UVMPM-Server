from enum import Enum, auto
import socket
from typing import Dict
from Response import Response


class Client:
    def __init__(self, sock: socket.socket):
        self.sock = sock
        self.state = State.NOT_GREETED

        self.username: str = None

    def set_greeted(self):
        self.state = State.UNAUTHORIZED

    def set_authorized(self, username):
        self.username = username
        self.state = State.AUTHORIZED

    def send_response(self, response: Response):
        self.sock.send(response.message)

    def __str__(self):
        if self.username:
            return self.username + " (" + str(self.sock.fileno()) + ")"
        else:
            return str(self.sock.fileno())


class State(Enum):
    NOT_GREETED = auto()
    UNAUTHORIZED = auto()
    AUTHORIZED = auto()
