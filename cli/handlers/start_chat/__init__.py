from node import Node
import re
from typing import Type
from cli.handlers import CommandHandler
from chat import Chat, ChatState


class StartChatCommandHandler(CommandHandler):
    def __init__(self, node: Type[Node]):
        self.node = node

    def can_handle(self, command: str) -> bool:
        if re.fullmatch(self._get_pattern(), command, flags=re.IGNORECASE):
            return True
        return False

    def handle(self, command: str):
        captured_args = re.fullmatch(self._get_pattern(), command, flags=re.IGNORECASE).groupdict()
        chat_name = captured_args['chat_name']
        proposed_members = captured_args['all_ids']
        real_members = self.get_real_members(proposed_members)
        chat = Chat(self.node.id, members=real_members, node = self.node)
        chat.start_chat(chat_name)
        # chat.state = ChatState.JOINED
        # message = f"REQUESTS FOR STARTING CHAT WITH {chat_name}: {self.node.id}, {str(real_members)[1:-1]}"
        # chat.send_chat_msg(message)
        self.node.ongoing_chat = chat
        return chat
        #send this message to all chat members
        # self.propagate_chat_message(message=message, members=real_members)
        # self.node.send_new_message(msg="Salam Salam Sad Ta Salam", dst_id=int(captured_args['dst_id']))

    def get_real_members(self, proposed_members: str):
        temp_members = [int(member) for member in proposed_members.split(',')]
        result = []
        for member in temp_members:
            if member in self.node.known_clients:
                result.append(member)
        return result
    
    # def propagate_chat_message(self, message, members):
    #     for member in members:
    #         self.node.send_new_message(msg=message, dst_id=member)

    @staticmethod
    def _get_pattern():
        return rf'START CHAT (?P<chat_name>[a-zA-Z]+): (?P<all_ids>((\d+), )*(\d+))'
