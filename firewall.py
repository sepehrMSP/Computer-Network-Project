from enum import IntEnum
from dataclasses import dataclass
from packet import PacketType


class Action(IntEnum):
    DROP = 0
    ACCEPT = 1


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


class FireWall:
    def __init__(self):
        self.table = dict()

    def add_rule(self):
        pass

    def remove_rule(self):
        pass

    def filter(self):
        pass


class AppFireWall(FireWall):
    pass


class NetFireWall(FireWall):
    pass
