from node import Node
import re
from typing import Type
from cli.handlers import CommandHandler


class AdvertiseCommandHandler(CommandHandler):
    def __init__(self, node: Type[Node]):
        self.node = node

    def can_handle(self, command: str) -> bool:
        if re.fullmatch(self._get_pattern(), command):
            return True
        return False

    def handle(self, command: str):
        captured_args = re.fullmatch(self._get_pattern(), command).groupdict()
        self.node.public_advertise(destination_id=captured_args['dst_id'])

    def _get_pattern(self):
        return rf'Advertise (?P<dst_id>\d+)'
