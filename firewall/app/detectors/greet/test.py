from unittest import TestCase
from firewall.app.detectors.greet import GreetAppDetector


class GreetAppDetectorTest(TestCase):
    def setUp(self):
        self.detector = GreetAppDetector()

    def test_start_greet_data(self):
        packet_data = "Salam Salam Sad Ta Salam"
        self.assertTrue(self.detector.detect(packet_data))
