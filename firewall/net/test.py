from unittest import TestCase
from firewall import Action
from firewall.net import NetFirewall, NetRule, Direction
from packet import Packet, PacketType


class NetFirewallTest(TestCase):
    def setUp(self):
        self.firewall = NetFirewall()

    def test_input_direction(self):
        rule = NetRule(
            direction=Direction.INPUT,
            packet_type=PacketType.ROUTING_REQ,
            action=Action.DROP,
            dst_id=2,
        )
        packet = Packet(
            src_id=1,
            dst_id=2,
            packet_type=PacketType.ROUTING_REQ,
            data="",
        )
        self.firewall.add_rule(rule)
        self.assertEqual(self.firewall.filter(packet), Action.DROP)

    def test_forward_direction_with_destination(self):
        rule = NetRule(
            direction=Direction.FORWARD,
            packet_type=PacketType.CONN_REQ,
            action=Action.DROP,
            dst_id=2,
        )
        packet = Packet(
            src_id=1,
            dst_id=2,
            packet_type=PacketType.CONN_REQ,
            data="",
        )
        self.firewall.add_rule(rule)
        self.assertEqual(self.firewall.filter(packet), Action.DROP)

    def test_packet_type_mismatch(self):
        rule = NetRule(
            direction=Direction.INPUT,
            packet_type=PacketType.ROUTING_REQ,
            action=Action.DROP,
            dst_id=2,
        )
        packet = Packet(
            src_id=1,
            dst_id=2,
            packet_type=PacketType.CONN_REQ,
            data="",
        )
        self.firewall.add_rule(rule)
        self.assertEqual(self.firewall.filter(packet), self.firewall.default_action)
