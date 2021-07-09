from unittest import TestCase
from firewall import Action
from firewall.app import App, AppFirewall
from cli.handlers.app_firewall import AppFirewallCommandHandler


class AppFirewallCommandHandlerTest(TestCase):
    def setUp(self):
        self.firewall = AppFirewall()
        self.command_handler = AppFirewallCommandHandler(self.firewall)
    
    def test_valid_command(self):
        cmd = "FW CHAT DROP"
        self.assertTrue(self.command_handler.can_handle(cmd))
        self.command_handler.handle(cmd)
        self.assertEqual(len(self.firewall.rules), 1)
        rule = self.firewall.rules[0]
        self.assertEqual(rule.action, Action.DROP)
        self.assertEqual(rule.app, App.CHAT)
