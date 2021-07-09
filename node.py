import socket
from manager import MANAGER_PORT, MANAGER_HOST
from packet import Packet, PacketType


class Node:
    PARENT_ID_POS = 2
    PARENT_PORT_POS = -1

    def __init__(self, port: int, id: int, firewall):
        self.port = port
        self.id = id
        self.left_children = set()
        self.right_children = set()
        self.firewall = firewall
        self.parent_id = None
        self.parent_port = None
        self.left_child_id = None
        self.left_child_port = None
        self.right_child_id = None
        self.right_child_port = None
        self.known_clients = set()
        self.is_in_chat = False

    @staticmethod
    def send_tcp(host, port: int, message, get_response=False):
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((host, port))
        client.send(message.encode('ascii'))
        data = None
        if get_response:
            data = client.recv(1024).decode('ascii')
        client.close()
        return data

    def join_network(self):
        message = f'{self.id} REQUESTS FOR CONNECTING TO NETWORK ON PORT {self.port}'
        data = self.send_tcp(host=MANAGER_HOST, port=MANAGER_PORT, message=message, get_response=True)
        self.parent_id, self.parent_port = int(data.split()[Node.PARENT_ID_POS]), \
                                           int(data.split()[Node.PARENT_PORT_POS])
        if self.parent_id != -1:
            data = str(self.port)
            packet = Packet(src_id=self.id,
                            dst_id=self.parent_id,
                            packet_type=PacketType.CONN_REQ,
                            data=data)
            self.send_packet(packet=packet)

    def self_route(self, packet: Packet):
        if packet.packet_type == PacketType.ROUTING_REQ:
            packet = Packet(src_id=self.id,
                            dst_id=packet.src_id,
                            packet_type=PacketType.ROUTING_RESP,
                            data='')
            self.route_resp(packet=packet, sender_id=self.id)

    def route_packet(self, packet: Packet):
        # todo
        if packet.dst_id == self.id:
            self.self_route(packet=packet)
        if packet.dst_id in self.left_children:
            pass
        elif packet.dst_id in self.right_children:
            pass
        elif self.parent_id != -1:
            pass
        else:
            data = f'DESTINATION {packet.dst_id} NOT FOUND'
            packet = Packet(src_id=self.id,
                            dst_id=packet.src_id,
                            packet_type=PacketType.DEST_NOT_FOUND,
                            data=data)
            self.route_packet(packet)

    def send_packet(self, packet: Packet):
        # todo why this function exist?
        if packet.dst_id != -1:
            if packet.dst_id in self.known_clients:
                self.route_packet(packet=packet)
            else:
                print(f'Unknown destination {packet.dst_id}')
        else:
            # todo
            pass

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
        self.route_packet(packet=packet)

    def route_resp(self, packet: Packet, sender_id: int):
        if packet.src_id == self.id:
            packet.data = str(self.id) + packet.data
        else:
            if sender_id == self.parent_id:
                packet.data = str(self.id) + '<-' + packet.data
            else:
                packet.data = str(self.id) + '->' + packet.data
        self.route_packet(packet=packet)

    def public_advertise(self, destination_id: int):
        if destination_id != -1:
            packet = Packet(src_id=self.id,
                            dst_id=destination_id,
                            packet_type=PacketType.PUBLIC_ADV,
                            data='')
            self.route_packet(packet)
        else:
            # todo
            pass

    def parent_advertise(self, new_node_id: int):
        if self.parent_id != -1:
            packet = Packet(src_id=self.id,
                            dst_id=self.parent_id,
                            packet_type=PacketType.PARENT_ADV,
                            data=str(new_node_id))
            self.route_packet(packet=packet)
