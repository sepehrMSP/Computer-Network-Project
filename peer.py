from firewall.app.detectors.greet import GreetAppDetector
import socket
import threading

from cli.handlers.advertise import AdvertiseCommandHandler
from cli.handlers.route import RouteCommandHandler

from cli.handlers.app_firewall import AppFirewallCommandHandler
from cli.handlers.connect import ConnectCommandHandler
from cli.handlers.known_clients import KnownClientsCommandHandler
from cli.handlers.net_firewall import NetFirewallCommandHandler
from cli.handlers.app_greeting import AppGreetingCommandHandler
from cli.handlers.start_chat import StartChatCommandHandler
from cli.manager import CommandLineManager
from firewall.app import AppFirewall
from firewall.app.detectors.chat import ChatAppDetector
from firewall.net import NetFirewall
from node import Node
from server import Server


def cli_thread(clm: CommandLineManager):
    while True:
        clm.handle(input())


def main():
    app_firewall = AppFirewall(
        detectors=[
            ChatAppDetector(),
            GreetAppDetector(),
        ],
    )
    net_firewall = NetFirewall()
    server = Server(daemon=True)
    node = Node(
        server=server,
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
        AppGreetingCommandHandler(node),
        StartChatCommandHandler(node),
    ]
    cl_manager = CommandLineManager(command_handlers)
    c_thread = threading.Thread(target=cli_thread, args=(cl_manager,), daemon=True)
    c_thread.start()
    c_thread.join()


if __name__ == '__main__':
    main()
