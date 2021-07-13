from firewall.app.detectors import AppDetector
from firewall.app import App


class GreetAppDetector(AppDetector):
    APP = App.GREET

    def detect(self, packet_data: str) -> bool:
        for msg in (
            "Salam Salam Sad Ta Salam",
            "Hezaro Sisad Ta Salam",
        ):
            if msg == packet_data:
                return True
        return False
