import re
from typing import Type
from cli.handlers import CommandHandler
from node import Node


class ConnectCommandHandler(CommandHandler):
    def __init__(self, node: Type[Node]):
        self.node = node

    def can_handle(self, command: str) -> bool:
        if re.fullmatch(self._get_pattern(), command):
            return True
        return False

    def handle(self, command: str):
        captured_args = re.fullmatch(self._get_pattern(), command).groupdict()
        self.node.join_network(
            port=captured_args['port'],
            id=captured_args['id'],
        )
        
    def _get_pattern(self):
        return 'CONNECT AS (?P<id>\d+) ON PORT (?P<port>\d+)'
