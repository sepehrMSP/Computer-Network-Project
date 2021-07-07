class Node:
    def __init__(self, port: int, id: int, firewall):
        self.port = port
        self.id = id
        self.children = set()
        self.firewall = firewall
        self.parent = None
        self.left_child = None
        self.right_child = None

    def join_network(self):
        pass

    def send_packet(self):
        pass

    def receive_packet(self):
        pass

    def advertise(self):
        pass

    def public_advertise(self):
        pass

    def parent_advertise(self):
        pass
