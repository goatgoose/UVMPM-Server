from abc import ABCMeta, abstractmethod


class Response:
    __metaclass__ = ABCMeta

    @abstractmethod
    @property
    def _message(self):
        pass

    @property
    def message(self):
        return self._message.encode("ascii")


class Ack(Response):
    def _message(self):
        return "HELLO"
