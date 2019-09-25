from Request import *
from Client import Client


class RequestManager:
    def __init__(self):
        self.requests = [
            Handshake,
            Authentication,
            ListUsers,
            SendMessage,
            Logout,
            Unknown
        ]

    def get_request(self, client: Client, request_bytes: bytes):
        try:
            raw_request = request_bytes.decode("ascii").strip()
        except Exception:
            # Unable to convert to ascii
            return Unknown(client, None)

        for request_class in self.requests:
            if request_class.is_of_type(raw_request):
                return request_class(client, raw_request)

        return Unknown(client, None)
