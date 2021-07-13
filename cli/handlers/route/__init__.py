import re
from typing import Type
from node import Node
from cli.handlers import CommandHandler


class RouteCommandHandler(CommandHandler):
    def __init__(self, node: Type[Node]):
        self.node = node

    def can_handle(self, command: str) -> bool:
        if re.fullmatch(self._get_pattern(), command):
            return True
        return False

    def handle(self, command: str):
        captured_args = re.fullmatch(self._get_pattern(), command).groupdict()
        self.node.route_req(dst_id=int(captured_args['id']))

    @staticmethod
    def _get_pattern():
        return rf'ROUTE (?P<id>\d+|-1)'
