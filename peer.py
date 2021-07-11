import socket
import threading

from cli.handlers.advertise import AdvertiseCommandHandler
from cli.handlers.route import RouteCommandHandler

from cli.handlers.app_firewall import AppFirewallCommandHandler
from cli.handlers.connect import ConnectCommandHandler
from cli.handlers.known_clients import KnownClientsCommandHandler
from cli.handlers.net_firewall import NetFirewallCommandHandler
from cli.manager import CommandLineManager
from firewall.app import AppFirewall
from firewall.app.detectors.chat import ChatAppDetector
from firewall.net import NetFirewall
from node import Node


def cli_thread(clm: CommandLineManager):
    while True:
        clm.handle(input())


def server_thread(node: Node):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((socket.gethostname(), node.get_receiving()))
        s.listen()
        while True:
            conn, addr = s.accept()
            threading.Thread(target=node.receive_tcp, args=(conn, addr), daemon=True).start()


def main():
    app_firewall = AppFirewall(
        detectors=[
            ChatAppDetector(),
        ],
    )
    net_firewall = NetFirewall()
    node = Node(
        net_firewall=net_firewall,
        app_firewall=app_firewall,
    )
    command_handlers = [
        NetFirewallCommandHandler(net_firewall),
        AppFirewallCommandHandler(app_firewall),
        ConnectCommandHandler(node),
        AdvertiseCommandHandler(node),
        KnownClientsCommandHandler(node),
        RouteCommandHandler(node),
    ]
    cl_manager = CommandLineManager(command_handlers)
    cli_thread(cl_manager)


if __name__ == '__main__':
    main()
