from typing import List

from cli import CommandError
from cli.handlers import CommandHandler


class CommandLineManager:
    def __init__(self, handlers: List[CommandHandler] = None):
        if handlers is None:
            handlers = []
        self.handlers = handlers

    def handle(self, command: str):
        for handler in self.handlers:
            if handler.can_handle(command):
                try:
                    handler.handle(command)
                except CommandError as e:
                    print(e)
                break
