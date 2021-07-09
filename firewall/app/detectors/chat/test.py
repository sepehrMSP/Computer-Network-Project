from unittest import TestCase
from firewall.app.detectors.chat import ChatAppDetector


class ChatAppDetectorTest(TestCase):
    def setUp(self):
        self.detector = ChatAppDetector()

    def test_start_chat_data(self):
        packet_data = "START‬‬ ‫‪CHAT test: 3, 50"
        self.assertTrue(self.detector.detect(packet_data))
