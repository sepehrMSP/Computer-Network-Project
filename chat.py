from node import Node
from typing import Dict, List, Tuple
import re
from enum import IntEnum
from threading import Lock

class ChatMessageType(IntEnum):
    NORMAL_CHAT_MESSAGE = 0
    START_REQUEST = 1
    CHOOSE_NAME = 2
    EXIT_CHAT = 3

class ChatState(IntEnum):
    JOINED = 0
    START_REQUEST = 1
    CONFIRM_JOIN = 2

class Chat:
    NORMAL_CHAT_MESSAGE_RE = rf"(?P<name>[a-zA-Z]+): (?P<msg>.+)"
    START_REQUEST_RE = rf"REQUESTS FOR STARTING CHAT WITH (?P<chat_name>[a-zA-Z]+): (?P<all_ids>((\d+), )*(\d+))"
    CHOOSE_NAME_RE = rf"(?P<id>\d+): (?P<chat_name>[a-zA-Z]+)"
    EXIT_CHAT_RE = rf"EXIT CHAT (?P<id>\d+)"

    def __init__(self, owner: int, members: List[int], node: Node):
        self.owner = owner
        self.members = members.copy()
        if owner not in self.members:
            self.members.insert(0, owner)
        self.node = node
        self.my_chat_name = None
        self.accepted_members: Dict[int, bool] = {owner: True}
        self.member_names : Dict[int, str] = {}
        self.modification_lock = Lock()
        self.state: ChatState = None

    def send_chat_msg(self, msg, only_accepted=False):
        msg_for_send = f"CHAT:\n{msg}"
        for member in self.members:
            try:
                member_has_accepted = self.accepted_members[member]
            except KeyError:
                member_has_accepted = False
            if self.node.id != member and (not only_accepted or member_has_accepted):
                self.node.send_new_message(msg=msg_for_send, dst_id=member)
    
    def send_normal_chat_msg(self, msg):
        self.send_chat_msg(msg=f"{self.member_names[self.node.id]}: {msg}", only_accepted=True)

    def start_chat(self, name):
        with self.modification_lock:
            self.member_names[self.node.id] = name
            self.state = ChatState.JOINED
        message = f"REQUESTS FOR STARTING CHAT WITH {name}: {str(self.members)[1:-1]}"
        self.send_chat_msg(msg=message, only_accepted=False)
    
    def accept_chat(self, name):
        self.my_chat_name = name
        with self.modification_lock:
            self.accepted_members[self.node.id] = False
            self.member_names[self.node.id] = name
            self.state = ChatState.JOINED
        self.send_chat_msg(f"{self.node.id}: {name}", only_accepted=False)

    def exit_chat(self):
        with self.modification_lock:
            self.accepted_members[self.node.id] = True
            del self.member_names[self.node.id]
        self.send_chat_msg(f"EXIT CHAT {self.node.id}", only_accepted=False)
    
    @staticmethod
    def onmessage_request_join(msg: str, node: Node):
        captured_args = re.fullmatch(Chat.START_REQUEST_RE, msg).groupdict()
        owner_name = captured_args['chat_name']
        all_ids = [int(member_id) for member_id in captured_args['all_ids'].split(',')]
        owner_id = all_ids[0]
        members = all_ids[1:]
        result = Chat(owner=owner_id, members=members, node=node)
        result.member_names[owner_id] = owner_name
        result.state = ChatState.START_REQUEST
        return result, f"{owner_name} with id {owner_id} has asked you to join a chat. Would you like to join?[Y/N]"
    
    def onmessage_normal(self, msg):
        return msg
    
    def onmessage_accept(self, msg):
        captured_args = re.fullmatch(Chat.CHOOSE_NAME_RE, msg).groupdict()
        accepted_member_chat_name = captured_args['chat_name']
        accepted_member_id = int(captured_args['id'])
        with self.modification_lock:
            self.accepted_members[accepted_member_id] = True
            self.member_names[accepted_member_id] = accepted_member_chat_name
        return f"{accepted_member_chat_name}({accepted_member_id}) was joined to the chat."

    def onmessage_exit(self, msg):
        captured_args = re.fullmatch(Chat.EXIT_CHAT_RE, msg).groupdict()
        exited_member_id = int(captured_args['id'])
        exited_member_chat_name = self.member_names[exited_member_id]
        with self.modification_lock:
            self.accepted_members[exited_member_id] = False
            del self.member_names[exited_member_id]
        return f"{exited_member_chat_name}({exited_member_id}) left the chat."

    @staticmethod
    def get_chat_msg_type(msg):
        if re.fullmatch(Chat.NORMAL_CHAT_MESSAGE_RE, msg):
            return ChatMessageType.NORMAL_CHAT_MESSAGE
        if re.fullmatch(Chat.START_REQUEST_RE, msg):
            return ChatMessageType.START_REQUEST
        if re.fullmatch(Chat.CHOOSE_NAME_RE, msg):
            return ChatMessageType.CHOOSE_NAME
        if re.fullmatch(Chat.EXIT_CHAT_RE, msg):
            return ChatMessageType.EXIT_CHAT
    