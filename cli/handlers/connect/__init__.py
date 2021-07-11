import re

from cli.handlers import CommandHandler
from node import Node


class ConnectCommandHandler(CommandHandler):
    def __init__(self, node: Node):
        self.node = node

    def can_handle(self, command: str) -> bool:
        if re.fullmatch(self._get_pattern(), command):
            return True
        return False

    def handle(self, command: str):
        captured_args = re.fullmatch(self._get_pattern(), command).groupdict()
        self.node.join_network(
            port=int(captured_args['port']),
            id=int(captured_args['id']),
        )

    @staticmethod
    def _get_pattern():
        return 'CONNECT AS (?P<id>\d+) ON PORT (?P<port>\d+)'
