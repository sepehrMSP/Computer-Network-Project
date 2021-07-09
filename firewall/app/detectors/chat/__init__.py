from firewall.app.detectors import AppDetector
from firewall.app import App


class ChatAppDetector(AppDetector):
    APP = App.CHAT

    def detect(self, packet_data: str) -> bool:
        lines = packet_data.splitlines()

        if len(lines) < 2:
            return False

        if lines[0] != "CHAT:":
            return False

        return True
