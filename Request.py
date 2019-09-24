from abc import ABCMeta, abstractmethod
from UVMPMException import InvalidRequestSyntax


class Request:
    __metaclass__ = ABCMeta

    def __init__(self, raw_request: str):
        self.raw_request = raw_request

    @abstractmethod
    def is_of_type(self, to_match: str):
        pass


class Unknown(Request):
    def __init__(self, raw_request: str):
        super(Request).__init__(raw_request)

    def is_of_type(self, to_match: str):
        return True


class Handshake(Request):
    def __init__(self, raw_request: str):
        super(Request).__init__(raw_request)

    def is_of_type(self, to_match: str):
        return to_match == "HELLO"


class Authentication(Request):
    def __init__(self, raw_request: str):
        super(Request).__init__(raw_request)

        split = self.raw_request.split(":")
        if len(split) != 3:
            raise InvalidRequestSyntax(self.raw_request)

        self.username = split[1]
        self.password = split[2]

    def is_of_type(self, to_match: str):
        return to_match.startswith("AUTH:")


class ListUsers(Request):
    def __init__(self, raw_request: str):
        super(Request).__init__(raw_request)

    def is_of_type(self, to_match: str):
        return to_match == "LIST"


class SendMessage(Request):
    def __init__(self, raw_request: str):
        super(Request).__init__(raw_request)

        split = self.raw_request.split(":")
        if len(split) != 3:
            raise InvalidRequestSyntax(self.raw_request)

        self.receiving_username = split[1]
        self.message = split[2]

    def is_of_type(self, to_match: str):
        return to_match.startswith("To:")


class Logout(Request):
    def __init__(self, raw_request: str):
        super(Request).__init__(raw_request)

    def is_of_type(self, to_match: str):
        return to_match == "BYE"
