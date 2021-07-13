from node import Node
import re
from typing import Type
from cli.handlers import CommandHandler


class AppGreetingCommandHandler(CommandHandler):
    def __init__(self, node: Type[Node]):
        self.node = node

    def can_handle(self, command: str) -> bool:
        if re.fullmatch(self._get_pattern(), command, flags=re.IGNORECASE):
            return True
        return False

    def handle(self, command: str):
        captured_args = re.fullmatch(self._get_pattern(), command).groupdict()
        self.node.send_new_message(msg="Salam Salam Sad Ta Salam", dst=int(captured_args['dst_id']))

    def _get_pattern(self):
        return rf'Salam Salam Sad Ta Salam (?P<dst_id>\d+|-1)'
