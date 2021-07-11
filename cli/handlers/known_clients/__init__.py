from cli.handlers import CommandHandler
from node import Node


class KnownClientsCommandHandler(CommandHandler):
    def __init__(self, node: Node):
        self.node = node

    def can_handle(self, command: str) -> bool:
        if command.strip() == "SHOW KNOWN CLIENTS":
            return True
        return False

    def handle(self, command: str):
        self.node.show_known_clients()
