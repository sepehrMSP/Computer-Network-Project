from unittest import TestCase
from firewall.app import App, AppFirewall, AppRule
from firewall.app.detectors.chat import ChatAppDetector
from firewall import Action


class AppFirewallTest(TestCase):
    def setUp(self):
        self.firewall = AppFirewall(detectors=[ChatAppDetector()])

    def test_disable_and_enable(self):
        chat_data = "CHAT:\nSTART‬‬ ‫‪CHAT test: 3, 50"
        drop_rule = AppRule(
            app=App.CHAT,
            action=Action.DROP,
        )
        self.firewall.add_rule(drop_rule)
        self.assertEqual(self.firewall.filter(chat_data), Action.DROP)

        accept_rule = AppRule(
            app=App.CHAT,
            action=Action.ACCEPT,
        )
        self.firewall.add_rule(accept_rule)
        self.assertEqual(self.firewall.filter(chat_data), Action.ACCEPT)
