import re

from cli.handlers import CommandHandler
from firewall import Action
from firewall.app import AppFirewall, App, AppRule


class AppFirewallCommandHandler(CommandHandler):
    def __init__(self, firewall: AppFirewall):
        self.firewall = firewall

    def can_handle(self, command: str) -> bool:
        if re.fullmatch(self._get_pattern(), command):
            return True
        return False

    def handle(self, command: str):
        captured_args = re.fullmatch(self._get_pattern(), command).groupdict()
        app = App[captured_args['app']]
        action = Action[captured_args['action']]
        self.firewall.add_rule(
            AppRule(
                app=app,
                action=action,
            )
        )

    @staticmethod
    def _get_pattern():
        apps = '|'.join([i.name for i in App])
        actions = '|'.join([i.name for i in Action])

        return rf'FW (?P<app>{apps}) (?P<action>{actions})'
