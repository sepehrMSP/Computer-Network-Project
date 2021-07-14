from enum import IntEnum
from dataclasses import dataclass
from typing import List, Type
from packet import Packet, PacketType
from firewall import Action, Firewall


class Direction(IntEnum):
    INPUT = 0
    OUTPUT = 1
    FORWARD = 2


@dataclass
class NetRule:
    direction: Direction
    packet_type: PacketType
    action: Action
    src_id: int = None
    dst_id: int = None


class NetFirewall(Firewall[NetRule]):
    def __init__(self, rules: List[NetRule] = None, default_action: Action = Action.ACCEPT):
        if rules is None:
            rules = []
        self.rules = rules
        self.default_action = default_action

    def add_rule(self, rule: NetRule):
        self.rules.append(rule)

    def remove_rule(self, rule: NetRule):
        self.rules.remove(rule)

    def filter(self, packet: Packet, current_node_id: int) -> Action:
        packet_direction = self._get_packet_direction(packet, current_node_id)
        for rule in reversed(self.rules):
            if self._match_rule(rule, packet, packet_direction):
                return rule.action

        return self.default_action

    def _get_packet_direction(self, packet: Packet, current_node_id: int) -> Direction:
        if packet.dst_id == current_node_id:
            return Direction.INPUT
        elif packet.src_id == current_node_id:
            return Direction.OUTPUT
        else:
            return Direction.FORWARD

    @staticmethod
    def _match_rule(rule: NetRule, packet: Packet, packet_direction: Direction) -> bool:
        if rule.packet_type != packet.packet_type:
            return False

        if rule.direction != packet_direction:
            return False

        src_id_mismatch: bool = (rule.src_id is not None) and (rule.src_id != packet.src_id)
        dst_id_mismatch: bool = (rule.dst_id is not None) and (rule.dst_id != packet.dst_id)

        if rule.direction == Direction.INPUT and src_id_mismatch:
            return False

        if rule.direction == Direction.OUTPUT and dst_id_mismatch:
            return False

        if rule.direction == Direction.FORWARD and (dst_id_mismatch or src_id_mismatch):
            return False

        return True
