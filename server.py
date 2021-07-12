import socket
import threading
from node import Node


class Server(threading.Thread):
    def __init__(self):
        super().__init__()
        self.node = None

    def run(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((socket.gethostname(), self.node.get_receiving_port()))
            s.listen()
            while True:
                conn, addr = s.accept()
                threading.Thread(target=self.node.receive_tcp, args=(conn, addr), daemon=True).start()

    def set_node(self, node: Node):
        self.node = node
