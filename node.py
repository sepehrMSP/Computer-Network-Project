import socket
from packet import Packet, PacketType
import json


class Node:
    PARENT_ID_POS = 2
    PARENT_PORT_POS = -1

    def __init__(self, net_firewall, app_firewall):
        self.port: int = None
        self.id: int = None
        self.left_children = set()
        self.right_children = set()
        self.app_firewall = app_firewall
        self.net_firewall = net_firewall
        self.parent_id = None
        self.parent_port = None
        self.left_child_id = None
        self.left_child_port = None
        self.right_child_id = None
        self.right_child_port = None
        self.known_clients = set()
        self.is_in_chat = False

    def is_root(self):
        return self.parent_id == -1

    def send_tcp(self, data, port: int, host=socket.gethostname(), get_response=False) -> dict:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((host, port))
        data = json.dumps(data)
        client.send(data.encode('utf-8'))
        resp = None
        if get_response:
            resp = json.loads(client.recv(1024).decode('utf-8'))
        client.close()
        return resp

    def join_network(self, port: int, id: int):
        self.id = id
        self.port = port
        from manager import MANAGER_PORT, MANAGER_HOST
        message = f'{self.id} REQUESTS FOR CONNECTING TO NETWORK ON PORT {self.port}'
        data = self.send_tcp(host=MANAGER_HOST, port=MANAGER_PORT, data=message, get_response=True)
        self.parent_id, self.parent_port = int(data['content'].split()[Node.PARENT_ID_POS]), \
                                           int(data['content'].split()[Node.PARENT_PORT_POS])
        if self.parent_id != -1:
            packet = Packet(src_id=self.id,
                            dst_id=self.parent_id,
                            packet_type=PacketType.CONN_REQ,
                            data=str(self.port))
            self.send_packet(packet=packet)

    def route_packet(self, packet: Packet, sender_id: int):
        assert packet.dst_id != -1

        if packet.dst_id in self.left_children:
            self.send_tcp(data=packet, port=self.left_child_port)
        elif packet.dst_id in self.right_children:
            self.send_tcp(data=packet, port=self.right_child_port)
        elif not self.is_root():
            self.send_tcp(data=packet, port=self.parent_port)
        else:
            data = f'DESTINATION {packet.dst_id} NOT FOUND'
            packet = Packet(src_id=self.id,
                            dst_id=packet.src_id,
                            packet_type=PacketType.DEST_NOT_FOUND,
                            data=data)
            self.route_packet(packet=packet, sender_id=sender_id)

    def route_to_all(self, packet: Packet, sender_id: int):
        assert packet.dst_id == -1
        if sender_id == self.parent_id:
            self.send_tcp(data=packet, port=self.left_child_port)
            self.send_tcp(data=packet, port=self.right_child_port)
        elif sender_id == self.left_child_id:
            self.send_tcp(data=packet, port=self.parent_port)
            self.send_tcp(data=packet, port=self.right_child_port)
        elif sender_id == self.right_child_id:
            self.send_tcp(data=packet, port=self.parent_port)
            self.send_tcp(data=packet, port=self.left_child_port)

    def send_packet(self, packet: Packet, sender_id=None):
        if sender_id is None:
            sender_id = self.id

        if packet.dst_id != -1:
            if packet.dst_id in self.known_clients:
                self.route_packet(packet=packet, sender_id=sender_id)
            else:
                print(f'Unknown destination {packet.dst_id}')
        else:
            self.route_to_all(packet=packet, sender_id=sender_id)

    def get_sender_id(self, port: int) -> int:
        if port == self.parent_port:
            return self.parent_id
        elif port == self.left_child_port:
            return self.left_child_id
        else:
            return self.right_child_id

    def receive_packet(self):
        # todo
        pass

    def show_known_clients(self):
        print('Known clients:' + str(self.known_clients))

    def route_req(self, dst_id: int):
        packet = Packet(src_id=self.id,
                        dst_id=dst_id,
                        packet_type=PacketType.ROUTING_REQ,
                        data='')
        self.send_packet(packet=packet)

    def route_resp(self, requester_id: int):
        packet = Packet(src_id=self.id,
                        dst_id=requester_id,
                        packet_type=PacketType.ROUTING_RESP,
                        data=str(self.id))
        self.send_packet(packet=packet)

    def modify_routing_resp(self, packet: Packet, sender_id: int):
        if sender_id == self.parent_id:
            packet.data = str(self.id) + '<-' + packet.data
        else:
            packet.data = str(self.id) + '->' + packet.data

    def modify_packet(self, packet: Packet, sender_id: int):
        if packet.packet_type == PacketType.ROUTING_RESP:
            self.modify_routing_resp(packet=packet, sender_id=sender_id)

    def public_advertise(self, destination_id: int):
        packet = Packet(src_id=self.id,
                        dst_id=destination_id,
                        packet_type=PacketType.PUBLIC_ADV,
                        data='')
        self.send_packet(packet)

    def parent_advertise(self, new_node_id: int):
        if not self.is_root():
            packet = Packet(src_id=self.id,
                            dst_id=self.parent_id,
                            packet_type=PacketType.PARENT_ADV,
                            data=str(new_node_id))
            self.send_packet(packet=packet)
