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
    id_src: int = None
    id_des: int = None


class NetFirewall(Firewall[NetRule]):
    def __init__(self, rules: List[Type[NetRule]] = None, default_action: Action = Action.ACCEPT):
        if rules is None:
            rules = []
        self.rules = rules
        self.default_action = default_action
        
    def add_rule(self, rule: NetRule):
        self.rules.append(rule)

    def remove_rule(self, rule: NetRule):
        self.rules.remove(rule)

    def filter(self, packet: Packet, *args, **kwargs) -> Action:
        for rule in self.rules:
            if self._match_rule(rule, packet):
                return rule.action

        return self.default_action

    def _match_rule(self, rule: NetRule, packet: Packet) -> bool:
        if rule.packet_type != packet.packet_type:
            return False

        if rule.direction == Direction.INPUT and rule.id_src != None and rule.id_src != packet.src_id:
            return False

        if rule.direction == Direction.OUTPUT and rule.id_des != None and rule.id_des != packet.dest_id:
            return False

        if rule.direction == Direction.FORWARD and (rule.id_des != None and rule.id_des != packet.dest_id) and (rule.id_src != None and rule.id_src != packet.src_id):
            return False

        return True
