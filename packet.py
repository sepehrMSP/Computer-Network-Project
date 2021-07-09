from dataclasses import dataclass
from enum import IntEnum


class PacketType(IntEnum):
    MESSAGE = 0
    ROUTING_REQ = 10
    ROUTING_RESP = 11
    PARENT_ADV = 20
    PUBLIC_ADV = 21
    DEST_NOT_FOUND = 31
    CONN_REQ = 41


@dataclass
class Packet:
    data: str
    dst_id: int
    src_id: int
    packet_type: PacketType
