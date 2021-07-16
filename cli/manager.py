from typing import List

from cli import CommandError
from cli.handlers import CommandHandler
from enum import IntEnum
from chat import Chat, ChatState
from cli.handlers.start_chat import StartChatCommandHandler

class CliState(IntEnum):
    NONE_CHAT = 0
    JOINED_CHAT = 1
    CONFIRM_JOIN_CHAT = 2
    CHOOSE_NAME = 3


class CommandLineManager:
    def __init__(self, handlers: List[CommandHandler] = None, state: CliState=None, ongoing_chat: Chat=None):
        if handlers is None:
            handlers = []
        self.handlers = handlers
        self.state = state
        self.ongoing_chat = ongoing_chat
        self.start_chat_handler: StartChatCommandHandler = self.get_start_chat_handler()
    
    def get_start_chat_handler(self) -> StartChatCommandHandler:
        for handler in self.handlers:
            if type(handler) == StartChatCommandHandler:
                return handler
    
    def cleanup_onexit(self):
        self.state = CliState.NONE_CHAT
        self.ongoing_chat = None
        self.start_chat_handler.node.ongoing_chat = None

    def handle(self, command: str):
        if not self.ongoing_chat:   
            self.ongoing_chat = self.start_chat_handler.node.ongoing_chat
            if self.ongoing_chat and self.ongoing_chat.state == ChatState.JOINED:
                self.state = CliState.JOINED_CHAT
        if self.ongoing_chat and self.ongoing_chat.state == ChatState.START_REQUEST:
            self.state = CliState.CONFIRM_JOIN_CHAT
        if self.state == CliState.NONE_CHAT and self.start_chat_handler.can_handle(command):
            self.ongoing_chat = self.start_chat_handler.handle(command)
            self.state = CliState.JOINED_CHAT
            self.ongoing_chat.state = ChatState.JOINED
            return
        elif self.state == CliState.CONFIRM_JOIN_CHAT:
            if command.strip().upper() == 'Y':
                print("Choose a name for yourself")
                self.state = CliState.CHOOSE_NAME
                self.ongoing_chat.state = ChatState.CONFIRM_JOIN
            else:
                self.cleanup_onexit()
            return
        elif self.state == CliState.CHOOSE_NAME:
            name = command.split()[0]
            self.ongoing_chat.accept_chat(name=name)
            self.state = CliState.JOINED_CHAT
            self.ongoing_chat.state = ChatState.JOINED
            return
        elif self.state == CliState.JOINED_CHAT:
            if command == "EXIT CHAT":
                self.ongoing_chat.exit_chat()
                self.cleanup_onexit()
                return
            self.ongoing_chat.send_normal_chat_msg(command)
            return
        else:
            for handler in self.handlers:
                if handler.can_handle(command):
                    try:
                        handler.handle(command)
                    except CommandError as e:
                        print(e)
                    return
        print("Invalid Command !")
