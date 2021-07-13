import re
import socket
import threading
import json
from dataclasses import dataclass
from threading import Thread
from typing import Optional
from server import Server

MANAGER_PORT = 8000
MANAGER_HOST = socket.gethostname()

CONNECT_TO_NETWORK_RE = "^([0-9]+) REQUESTS FOR CONNECTING TO NETWORK ON PORT ([0-9]+)$"

nodes_tree = []
nodes_tree_lock = threading.Lock()


@dataclass
class PortId:
    port: int
    id: int


def get_new_node(node_request) -> Optional[PortId]:
    connection_request = json.loads(node_request)
    data = connection_request['data']
    search_items = re.search(CONNECT_TO_NETWORK_RE, data, flags=re.IGNORECASE)
    if search_items:
        id_new = search_items.group(1)
        port_new = search_items.group(2)
        node_new = PortId(port=int(port_new), id=int(id_new))
        return node_new
    return None


def get_new_node_father():
    index = (len(nodes_tree) - 1) // 2
    return nodes_tree[index]


def send_client_join_response(client_socket: socket.socket, id_parent: int, port_parent: int):
    response = json.dumps(f'CONNECT TO {id_parent} WITH PORT {port_parent}')
    client_socket.sendall(response.encode('utf-8'))


def add_node_to_tree(node: PortId):
    with nodes_tree_lock:
        if not nodes_tree:
            # return you are the first
            nodes_tree.append(node)
            return -1, -1
        else:
            # return who your father is
            father: PortId = get_new_node_father()
            nodes_tree.append(node)
            return father.id, father.port


def handle_client(client_socket: socket.socket, client_addr):
    msg = client_socket.recv(1024).decode('utf-8')
    print("before new_node ", msg)
    new_node = get_new_node(msg)

    if not new_node:
        print("shoot, it's not how we where supposed to talk man :/")
        return
    id_parent, port_parent = add_node_to_tree(new_node)
    send_client_join_response(client_socket, id_parent, port_parent)


if __name__ == "__main__":
    server = Server(
        address=MANAGER_HOST,
        port=MANAGER_PORT,
        client_handler=handle_client,
    )
    server.start()
