import socket
import threading
import re
from node import Node

MANAGER_PORT = 8000
MANAGER_HOST = socket.gethostname()

CONNECT_TO_NETWORK_RE = "^([0-9]+) REQUESTS FOR CONNECTING TO NETWORK ON PORT ([0-9]+)$"

nodes_tree = []
nodes_tree_lock = threading.Lock()

def get_new_node(node_request):
    search_items = re.search(CONNECT_TO_NETWORK_RE, node_request, flags=re.IGNORECASE)
    if search_items:
        id_new = search_items.group(1)
        port_new = search_items.group(2)
        node_new = Node(port = port_new, id = id_new, firewall=None)
        return node_new
    return None

def get_new_node_father():
    index = (len(nodes_tree) - 1) // 2
    return nodes_tree[index]

def send_client_join_response(client_socket: socket.socket, id_parent: int, port_parent: int):
    response = f'CONNECT TO {id_parent} WITH PORT {port_parent}'.encode()
    client_socket.sendall(response)

def add_node_to_tree(node: Node):
    with nodes_tree_lock:
        if not nodes_tree:
            #return you are the first
            nodes_tree.append(node)
            return (-1, -1)
            pass
        else:
            #return who your father is 
            father: Node = get_new_node_father()
            nodes_tree.append(node)
            return(father.id, father.port)

def handle_client(client_socket: socket.socket, client_addr):
    msg = client_socket.recv(1024).decode()
    new_node = get_new_node(msg)
    if not new_node:
        print("shoot, it's not how we where supposed to talk man :/")
        return
    id_parent, port_parent = add_node_to_tree(new_node)
    send_client_join_response(client_socket, id_parent, port_parent)


if __name__ == "__main__":
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((MANAGER_HOST, MANAGER_PORT))
        print(f"[+] manager listening on {socket.gethostbyname(MANAGER_HOST)}: {MANAGER_PORT}")
        s.listen()
        while True:
            conn, addr = s.accept()
            threading._start_new_thread(handle_client, (conn, addr))