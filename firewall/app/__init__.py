from enum import IntEnum
from dataclasses import dataclass
from typing import List, Type
from firewall import Action, FireWall
from firewall.app.detectors import AppDetector


class App(IntEnum):
    CHAT = 0
    GREET = 1


@dataclass
class AppRule:
    app: App
    action: Action


class AppFireWall(FireWall[AppRule]):
    def __init__(self, rules: List[Type[AppRule]] = [], detectors: List[Type[AppDetector]] = []):
        self.rules = rules
        self.detectors = detectors

    def add_rule(self, rule: AppRule):
        self.rules.append(rule)

    def remove_rule(self, rule: AppRule):
        self.rules.remove(rule)

    def filter(self, packet_data, *args, **kwargs) -> Action:
        detected_app = self._detect_app(packet_data)
        for rule in self.rules:
            if rule.app == detected_app:
                return rule.action

    def _detect_app(self, packet_data: str) -> App:
        for detector in self.detectors:
            if detector.detect():
                return detector.APP
