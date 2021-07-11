import threading
from typing import Type
from node import Node
from firewall.app import AppFirewall
from firewall.app.detectors.chat import ChatAppDetector
from firewall.net import NetFirewall
from cli.manager import CommandLineManager
from cli.handlers.net_firewall import NetFirewallCommandHandler
from cli.handlers.app_firewall import AppFirewallCommandHandler
from cli.handlers.connect import ConnectCommandHandler


def cli_thread(clm: Type[CommandLineManager]):
    while True:
        clm.handle(input())


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
    ]
    cl_manager = CommandLineManager(command_handlers)
    cli_thread(cl_manager)


if __name__ == '__main__':
    main()
