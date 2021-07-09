from enum import IntEnum
from dataclasses import dataclass
from typing import List, Type
from packet import PacketType
from firewall import Action, FireWall


class Direction(IntEnum):
    INPUT = 0
    OUTPUT = 1
    FORWARD = 2


@dataclass
class NetRule:
    direction: Direction
    packet_type: PacketType
    action: Action
    id_src: int = None
    id_des: int = None


class NetFireWall(FireWall[NetRule]):
    def __init__(self, rules: List[Type[NetRule]] = []):
        self.rules = rules
        
    def add_rule(self, rule: NetRule):
        pass

    def remove_rule(self, rule: NetRule):
        pass

    def filter(self, *args, **kwargs) -> Action:
        pass
