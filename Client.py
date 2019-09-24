from enum import Enum, auto
import socket
from typing import Dict


class Client:
    def __init__(self, sock: socket.socket):
        self.socket = sock

        self.state = State.NOT_GREETED

        self.username: str = None
        self.password: str = None

    def set_greeted(self):
        if self.state == State.NOT_GREETED:
            self.state = State.UNAUTHORIZED

    def authorize(self, username, password):
        self.username = username
        self.password = password

        self.state = State.AUTHORIZED

    def send_message(self, message: str):
        pass

    def send_user_list(self):
        pass

    def logout(self):
        pass


class State(Enum):
    NOT_GREETED = auto
    UNAUTHORIZED = auto
    AUTHORIZED = auto
