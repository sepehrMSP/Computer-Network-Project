from firewall.app import AppFirewall
from firewall.app.detectors.chat import ChatAppDetector
from firewall.net import NetFirewall
from cli.manager import CommandLineManager
from cli.handlers.net_firewall import NetFirewallCommandHandler
from cli.handlers.app_firewall import AppFirewallCommandHandler


def main():
    app_firewall = AppFirewall(
        detectors=[
            ChatAppDetector(),
        ],
    )
    net_firewall = NetFirewall()

    command_handlers = [
        NetFirewallCommandHandler(net_firewall),
        AppFirewallCommandHandler(app_firewall),
    ]
    cl_manager = CommandLineManager(command_handlers)
    # Todo


if __name__ == '__main__':
    main()
