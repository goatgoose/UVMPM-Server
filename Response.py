from abc import ABCMeta, abstractmethod


class Response:
    __metaclass__ = ABCMeta

    @abstractmethod
    @property
    def _message(self):
        pass

    @property
    def message(self):
        message_ = self._message + "\n"
        return message_.encode("ascii")


class Ack(Response):
    def _message(self):
        return "HELLO"


class AuthYes(Response):
    def _message(self):
        return "AUTHYES"


class AuthNo(Response):
    def _message(self):
        return "AUTHNO"


class SignIn(Response):
    def __init__(self, user):
        self.user = user

    def _message(self):
        return "SIGNIN:" + self.user


class SignOff(Response):
    def __init__(self, user):
        self.user = user

    def _message(self):
        return "SIGNOFF:" + self.user


class UserList(Response):
    def __init__(self, clients):
        self.clients = clients

    def _message(self):
        return ", ".join([client.username for client in self.clients])


class UserMessage(Response):
    def __init__(self, from_client, message):
        self.from_client = from_client
        self.user_message = message

    def _message(self):
        return "From:" + self.from_client + ":" + self.user_message
