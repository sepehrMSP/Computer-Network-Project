import re
from firewall.app.detectors import AppDetector
from firewall.app import App


class ChatAppDetector(AppDetector):
    APP = App.CHAT
    patterns = (
        r"START‬‬ ‫‪CHAT \w+: \d+(, \d+)*",
        # Todo: Add other patterns
    )

    def detect(self, packet_data: str) -> bool:
        for pattern in self.patterns:
            if re.fullmatch(pattern, packet_data):
                return True
        return False
