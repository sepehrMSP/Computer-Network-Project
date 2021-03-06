import dataclasses
from firewall.net import Direction
from firewall import Action
from types import SimpleNamespace
from typing import Optional
import socket
from packet import Packet, PacketType
import json


class Node:
    PARENT_ID_POS = 2
    PARENT_PORT_POS = -1
    UNKNOWN_ID = -2
    PORT_IS_NOT_SPECIFIED = -1

    def __init__(self, server, net_firewall=None, app_firewall=None):
        from chat import Chat, ChatMessageType, ChatState
        self.port: Optional[int] = None
        self.id: Optional[int] = None
        self.app_firewall = app_firewall
        self.net_firewall = net_firewall
        self.parent_id = None
        self.parent_port = Node.PORT_IS_NOT_SPECIFIED
        self.left_children = set()
        self.right_children = set()
        self.left_child_id = None
        self.left_child_port = Node.PORT_IS_NOT_SPECIFIED
        self.right_child_id = None
        self.right_child_port = Node.PORT_IS_NOT_SPECIFIED
        self.known_clients = set()
        self.is_in_chat = False
        self.server = server
        self.ongoing_chat: Chat = None

    def is_root(self):
        return self.parent_id == -1

    def get_sending_port(self):
        return self.port + 1

    def get_receiving_port(self):
        return self.port

    def send_tcp(self, data, port: int, host=socket.gethostname(), get_response=False):
        if port == Node.PORT_IS_NOT_SPECIFIED:
            return

        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((host, port))
        data = {'data': data, 'sender_id': self.id}

        def dumper(obj):
            try:
                return obj.ToJSON()
            except:
                try:
                    obj = dataclasses.asdict(obj)
                    return json.dumps(obj)
                except:
                    return obj.__dict__

        data = json.dumps(data, default=dumper, indent=2)

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
        resp = self.send_tcp(host=MANAGER_HOST, port=MANAGER_PORT, data=message, get_response=True)
        self.parent_id, self.parent_port = int(resp.split()[Node.PARENT_ID_POS]), \
                                           int(resp.split()[Node.PARENT_PORT_POS])

        self.server.set_port(self.get_receiving_port())
        self.server.set_client_handler(self.receive_tcp)
        self.server.start()

        if self.parent_id != -1:
            self.known_clients.add(self.parent_id)
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
        else:
            self.send_tcp(data=packet, port=self.parent_port)
            self.send_tcp(data=packet, port=self.left_child_port)
            self.send_tcp(data=packet, port=self.right_child_port)

    def transmit_packet(self, packet: Packet, sender_id: int = None):
        """
        For packets whose initiator is another host
        """
        print(f"{PacketType(packet.packet_type).name} Packet from {packet.src_id} to {packet.dst_id}")
        if packet.dst_id != -1:
            self.route_packet(packet=packet)
        else:
            assert sender_id is not None
            self.route_to_all(packet=packet, sender_id=sender_id)

    def send_new_packet(self, packet: Packet):
        """
        For packets whose initiator is self
        """
        action: Action = self.net_firewall.filter(packet, Direction.OUTPUT)
        if action == Action.DROP:
            return

        sender_id = self.id
        if packet.dst_id != -1:
            if packet.dst_id in self.known_clients or packet.packet_type == PacketType.CONN_REQ:
                action: Action = self.app_firewall.filter(packet.data)
                # print(action, packet.data)
                if action == Action.ACCEPT:
                    self.route_packet(packet=packet)
            else:
                print(f'Unknown destination {packet.dst_id}')
        else:
            self.route_to_all(packet=packet, sender_id=sender_id)

    def send_new_message(self, msg, dst_id: int):
        message_packet = Packet(src_id=self.id,
                                dst_id=dst_id,
                                packet_type=PacketType.MESSAGE,
                                data=msg)
        self.send_new_packet(message_packet)

    def receive_tcp(self, conn, addr):
        resp = json.loads(conn.recv(1024).decode('utf-8'))
        packet = Packet(**json.loads(resp['data']))
        sender_id = int(resp['sender_id'])
        conn.close()
        self.receive_packet(packet=packet, sender_id=sender_id)

    def handle_advertise_parent(self, packet: Packet, sender_id: int, input_packet_action):
        """
        Advertise the new child to parent will be ignored in case of input firewall drop rule regardless of forward rule.
        """
        assert packet.packet_type == PacketType.PARENT_ADV
        new_child_id = int(packet.data)
        if input_packet_action == Action.ACCEPT:
            self.known_clients.add(new_child_id)
            if sender_id == self.left_child_id:
                self.left_children.add(new_child_id)
            elif sender_id == self.right_child_id:
                self.right_children.add(new_child_id)
            self.parent_advertise(new_node_id=new_child_id)

    def add_new_child(self, packet: Packet, input_packet_action):
        """
        Advertise the new child to parent will be ignored in case of input firewall drop rule regardless of forward rule.
        """
        assert packet.packet_type == PacketType.CONN_REQ
        child_id = packet.src_id
        child_port = int(packet.data)
        if input_packet_action == Action.ACCEPT:
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
        if packet.dst_id == self.id or packet.dst_id == -1:
            self.known_clients.add(packet.src_id)

    def dest_not_found(self, packet: Packet, input_packet_action, forward_packet_action):
        if packet.dst_id == self.id:
            if input_packet_action == Action.ACCEPT and not self.is_in_chat:
                print(f'DESTINATION {packet.dst_id} NOT FOUND')
        else:
            if forward_packet_action == Action.ACCEPT:
                self.transmit_packet(packet=packet)

    def handle_routing_req_packet(self, packet: Packet, input_packet_action, forward_packet_action):
        if packet.dst_id == self.id:
            if input_packet_action == Action.ACCEPT:
                self.route_resp(packet.src_id)
        else:
            if forward_packet_action == Action.ACCEPT:
                self.transmit_packet(packet=packet)

    def handle_routing_resp_packet(self, packet: Packet, sender_id: int, input_packet_action, forward_packet_action):
        if packet.dst_id == self.id:
            if input_packet_action == Action.ACCEPT:
                self.modify_packet(packet=packet, sender_id=sender_id)
                print(f'the path between {packet.src_id} and {packet.dst_id}:\n'
                    f'{packet.data}')
        else:
            if forward_packet_action == Action.ACCEPT:
                self.modify_packet(packet=packet, sender_id=sender_id)
                self.transmit_packet(packet=packet)

    def handle_public_adv(self, packet: Packet, sender_id: int, input_packet_action, forward_packet_action):
        if packet.dst_id == self.id:
            if input_packet_action == Action.ACCEPT:
                self.known_clients.add(packet.src_id)
        elif packet.dst_id == -1:
            self.known_clients.add(packet.src_id)
            if forward_packet_action == Action.ACCEPT:
                self.transmit_packet(packet=packet, sender_id=sender_id)
        else:
            if forward_packet_action == Action.ACCEPT:
                self.transmit_packet(packet=packet)

    def handle_application_layer(self, packet: Packet, sender_id: int, input_packet_action, forward_packet_action):
        if packet.dst_id == self.id or packet.dst_id == -1:
            if input_packet_action == Action.ACCEPT:
                action: Action = self.app_firewall.filter(packet.data)
                if action == Action.ACCEPT:
                    if packet.data.startswith("CHAT:\n"):
                        packet.data = packet.data.split("\n")[1]
                        self.chatting(packet=packet)
                    else:
                        self.greeting(packet=packet)
            if packet.dst_id == -1:
                if forward_packet_action == Action.ACCEPT:
                    self.transmit_packet(packet=packet, sender_id=sender_id)
        else:
            if forward_packet_action == Action.ACCEPT:
                self.transmit_packet(packet=packet)

    def greeting(self, packet: Packet):
        if packet.data.strip().lower() == 'salam salam sad ta salam':
            self.send_new_message(msg='Hezaro Sisad Ta Salam', dst_id=packet.src_id)
        elif packet.data.strip().lower() == 'Hezaro Sisad Ta Salam':
            pass
        print(f'FROM {packet.src_id}:\n\t{packet.data}')
        pass

    def chatting(self, packet: Packet):
        from chat import Chat, ChatMessageType, ChatState
        message = packet.data
        message_type = Chat.get_chat_msg_type(msg=message)
        if message_type == ChatMessageType.START_REQUEST:
            chat, cli_msg = Chat.onmessage_request_join(msg=message, node=self)
            self.ongoing_chat = chat
            chat.node = self
            print(cli_msg)
        if self.ongoing_chat:
            if message_type == ChatMessageType.CHOOSE_NAME:
                print(self.ongoing_chat.onmessage_accept(message))
            elif message_type == ChatMessageType.NORMAL_CHAT_MESSAGE:
                print(self.ongoing_chat.onmessage_normal(message))
            elif message_type == ChatMessageType.EXIT_CHAT:
                print(self.ongoing_chat.onmessage_exit(message))

    def receive_packet(self, packet: Packet, sender_id: int):
        input_packet_action: Action = self.net_firewall.filter(packet, Direction.INPUT)
        forward_packet_action: Action = self.net_firewall.filter(packet, Direction.FORWARD)

        self.check_for_new_host(packet=packet)
        if packet.packet_type == PacketType.CONN_REQ:
            self.add_new_child(packet=packet, input_packet_action=input_packet_action)
        elif packet.packet_type == PacketType.DEST_NOT_FOUND:
            self.dest_not_found(packet=packet, input_packet_action=input_packet_action, forward_packet_action=forward_packet_action)
        elif packet.packet_type == PacketType.ROUTING_REQ:
            self.handle_routing_req_packet(packet=packet, input_packet_action=input_packet_action, forward_packet_action=forward_packet_action)
        elif packet.packet_type == PacketType.ROUTING_RESP:
            self.handle_routing_resp_packet(packet=packet, sender_id=sender_id, input_packet_action=input_packet_action, forward_packet_action=forward_packet_action)
        elif packet.packet_type == PacketType.PARENT_ADV:
            self.handle_advertise_parent(packet=packet, sender_id=sender_id, input_packet_action=input_packet_action)
        elif packet.packet_type == PacketType.PUBLIC_ADV:
            self.handle_public_adv(packet=packet, sender_id=sender_id, input_packet_action=input_packet_action, forward_packet_action=forward_packet_action)
        elif packet.packet_type == PacketType.MESSAGE:
            self.handle_application_layer(packet=packet, sender_id=sender_id, input_packet_action=input_packet_action, forward_packet_action=forward_packet_action)

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
