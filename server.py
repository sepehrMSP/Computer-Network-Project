import socket
from threading import Thread
from typing import Callable


class Server(Thread):
    def __init__(self, address: str = socket.gethostname(), port: int = None, client_handler: Callable = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.address = address
        self.port = port
        self.client_handler = client_handler

    def run(self):
        assert self.address is not None, "Provide address attribute before calling this."
        assert self.port is not None, "Provide port attribute before calling this."
        assert self.client_handler is not None, "Provide client_handler attribute before calling this."

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((self.address, self.port))
            s.listen()
            while True:
                connection, address = s.accept()
                Thread(target=self.client_handler, args=(connection, address), daemon=True).start()

    def set_address(self, address: str):
        self.address = address

    def set_port(self, port: int):
        self.port = port

    def set_client_handler(self, client_handler: Callable):
        self.client_handler = client_handler
