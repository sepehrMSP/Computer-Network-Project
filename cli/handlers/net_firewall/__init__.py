import re
from cli.handlers import CommandHandler
from packet import PacketType
from firewall import Action
from firewall.net import NetRule, NetFirewall, Direction


class NetFirewallCommandHandler(CommandHandler):
    def __init__(self, firewall: NetFirewall):
        self.firewall = firewall

    def can_handle(self, command: str) -> bool:
        if re.fullmatch(self._get_pattern(), command):
            return True
        return False

    def handle(self, command: str):
        captured_args = re.fullmatch(self._get_pattern(), command).groupdict()
        src_id = int(captured_args['src_id']) if captured_args['src_id'] != "*" else None
        dst_id = int(captured_args['dst_id']) if captured_args['dst_id'] != "*" else None
        action = Action[captured_args['action']]
        direction = Direction[captured_args['direction']]
        packet_type = PacketType(int(captured_args['packet_type']))
        self.firewall.add_rule(
            NetRule(
                direction=direction,
                packet_type=packet_type,
                action=action,
                src_id=src_id,
                dst_id=dst_id,
            )
        )

    @staticmethod
    def _get_pattern():
        directions = '|'.join([i.name for i in Direction])
        actions = '|'.join([i.name for i in Action])
        packet_types = '|'.join([str(i.value) for i in PacketType])

        return rf'FILTER (?P<direction>{directions}) (?P<src_id>\d+|\*) (?P<dst_id>\d+|\*) (?P<packet_type>{packet_types}) (?P<action>{actions})'
