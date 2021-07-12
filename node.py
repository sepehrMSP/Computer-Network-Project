from typing import Optional
import socket
from packet import Packet, PacketType
import json


class Node:
    PARENT_ID_POS = 2
    PARENT_PORT_POS = -1
    UNKNOWN_ID = -2

    def __init__(self, net_firewall=None, app_firewall=None):
        self.port: Optional[int] = None
        self.id: Optional[int] = None
        self.app_firewall = app_firewall
        self.net_firewall = net_firewall
        self.parent_id = None
        self.parent_port = None
        self.left_children = set()
        self.right_children = set()
        self.left_child_id = None
        self.left_child_port = None
        self.right_child_id = None
        self.right_child_port = None
        self.known_clients = set()
        self.is_in_chat = False

    def is_root(self):
        return self.parent_id == -1

    def get_sending_port(self):
        return self.port + 1

    def get_receiving(self):
        return self.port

    @staticmethod
    def send_tcp(data, port: int, host=socket.gethostname(), get_response=False):
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
        self.parent_id, self.parent_port = int(data.split()[Node.PARENT_ID_POS]), \
                                           int(data.split()[Node.PARENT_PORT_POS])
        print(self.parent_id, self.port)
        if self.parent_id != -1:
            packet = Packet(src_id=self.id,
                            dst_id=self.parent_id,
                            packet_type=PacketType.CONN_REQ,
                            data=str(self.port))
            self.send_new_packet(packet=packet)

    def route_packet(self, packet: Packet):
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
            self.route_packet(packet=packet)

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

    """
    For packets whose initiator is another host 
    """

    def transmit_packet(self, packet: Packet, sender_id: int = None):
        if packet.dst_id != -1:
            self.route_packet(packet=packet)
        else:
            assert sender_id is not None
            self.route_to_all(packet=packet, sender_id=sender_id)

    """
    For packets whose initiator is self
    """

    def send_new_packet(self, packet: Packet):
        sender_id = self.id
        if packet.dst_id != -1:
            if packet.dst_id in self.known_clients or packet.packet_type == PacketType.CONN_REQ:
                self.route_packet(packet=packet)
            else:
                print(f'Unknown destination {packet.dst_id}')
        else:
            self.route_to_all(packet=packet, sender_id=sender_id)

    def send_new_message(self, msg, dst):
        message_packet = Packet(src_id=self.id,
                                dst_id=dst,
                                packet_type=PacketType.MESSAGE,
                                data=msg)
        self.send_new_packet(message_packet)

    def get_sender_id(self, port: int) -> int:
        if port == self.parent_port:
            return self.parent_id
        elif port == self.left_child_port:
            return self.left_child_id
        elif port == self.right_child_port:
            return self.right_child_id
        else:
            return Node.UNKNOWN_ID

    def receive_tcp(self, conn, addr):
        sender_port = addr[1]
        sender_id = self.get_sender_id(port=sender_port)
        resp = json.loads(conn.recv(1024).decode('utf-8'))
        conn.close()
        self.receive_packet(packet=resp, sender_id=sender_id)

    def add_new_child(self, packet: Packet):
        assert (packet.packet_type == PacketType.CONN_REQ) or (packet.packet_type == PacketType.PARENT_ADV)
        child_id = packet.src_id
        child_port = int(packet.data)
        if packet.packet_type == PacketType.CONN_REQ:
            if self.left_child_id is None:
                self.left_child_id = child_id
                self.left_child_port = child_port
                self.left_children.add(child_id)
            elif self.right_child_id is None:
                self.right_child_id = child_id
                self.right_child_port = child_port
                self.right_children.add(child_id)
            else:
                print(f'ERROR: node {self.id} has already 2 children. connection request of node {child_id} rejected')
                return
        self.known_clients.add(child_id)
        self.parent_advertise(new_node_id=child_id)

    def check_for_new_host(self, packet: Packet):
        if packet.dst_id == self.id:
            self.known_clients.add(packet.src_id)

    def dest_not_found(self, packet: Packet):
        if packet.dst_id == self.id:
            if not self.is_in_chat:
                print(f'DESTINATION {packet.dst_id} NOT FOUND')
        else:
            self.transmit_packet(packet=packet)

    def handle_routing_req_packet(self, packet: Packet):
        if packet.dst_id == self.id:
            self.route_resp(packet.src_id)
        else:
            self.transmit_packet(packet=packet)

    def handle_routing_resp_packet(self, packet: Packet, sender_id: int):
        if packet.dst_id == self.id:
            print(f'the path between {packet.src_id} and {packet.dst_id}:\n'
                  f'{packet.data}')
        else:
            self.modify_packet(packet=packet, sender_id=sender_id)
            self.transmit_packet(packet=packet)

    def handle_public_adv(self, packet: Packet, sender_id: int):
        if packet.dst_id == self.id:
            self.known_clients.add(packet.src_id)
        elif packet.dst_id == -1:
            self.known_clients.add(packet.src_id)
            self.transmit_packet(packet=packet, sender_id=sender_id)
        else:
            self.transmit_packet(packet=packet)

    def handle_application_layer(self, packet: Packet):
        if packet.data.strip().lower() == 'salam salam sad ta salam':
            self.send_new_message(msg='Hezaro Sisad Ta Salam', dst=packet.src_id)
        elif packet.data.strip().lower() == 'Hezaro Sisad Ta Salam':
            pass
        print(f'FROM {packet.src_id}:\n\t{packet.data}')
        pass

    def receive_packet(self, packet: Packet, sender_id: int):
        self.check_for_new_host(packet=packet)
        if packet.packet_type == PacketType.CONN_REQ:
            self.add_new_child(packet=packet)
        elif packet.packet_type == PacketType.DEST_NOT_FOUND:
            self.dest_not_found(packet=packet)
        elif packet.packet_type == PacketType.ROUTING_REQ:
            self.handle_routing_req_packet(packet=packet)
        elif packet.packet_type == PacketType.ROUTING_RESP:
            self.handle_routing_resp_packet(packet=packet, sender_id=sender_id)
        elif packet.packet_type == PacketType.PARENT_ADV:
            self.add_new_child(packet=packet)
        elif packet.packet_type == PacketType.PUBLIC_ADV:
            self.handle_public_adv(packet=packet, sender_id=sender_id)
        elif packet.packet_type == PacketType.MESSAGE:
            self.handle_application_layer(packet=packet)

    def show_known_clients(self):
        print('Known clients:' + str(self.known_clients))

    def route_req(self, dst_id: int):
        assert dst_id != -1
        packet = Packet(src_id=self.id,
                        dst_id=dst_id,
                        packet_type=PacketType.ROUTING_REQ,
                        data='')
        self.send_new_packet(packet=packet)

    def route_resp(self, requester_id: int):
        packet = Packet(src_id=self.id,
                        dst_id=requester_id,
                        packet_type=PacketType.ROUTING_RESP,
                        data=str(self.id))
        self.send_new_packet(packet=packet)

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
        self.send_new_packet(packet)

    def parent_advertise(self, new_node_id: int):
        if not self.is_root():
            packet = Packet(src_id=self.id,
                            dst_id=self.parent_id,
                            packet_type=PacketType.PARENT_ADV,
                            data=str(new_node_id))
            self.send_new_packet(packet=packet)
