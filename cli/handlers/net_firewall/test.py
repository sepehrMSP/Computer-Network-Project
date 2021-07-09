from unittest import TestCase
from packet import PacketType
from firewall.net import NetFirewall
from cli.handlers.net_firewall import NetFirewallCommandHandler


class NetFirewallCommandHandlerTest(TestCase):
    def setUp(self):
        self.firewall = NetFirewall()
        self.command_handler = NetFirewallCommandHandler(self.firewall)
    
    def test_valid_command(self):
        cmd = "FILTER INPUT 1 * 21 DROP"
        self.assertTrue(self.command_handler.can_handle(cmd))
        self.command_handler.handle(cmd)
        self.assertEqual(len(self.firewall.rules), 1)
        rule = self.firewall.rules[0]
        self.assertEqual(rule.packet_type, PacketType.PUBLIC_ADV)
        self.assertEqual(rule.dst_id, None)

    def test_command_with_invalid_action(self):
        cmd = "FILTER INPUT 1 2 21 CHERT"
        self.assertFalse(self.command_handler.can_handle(cmd))
