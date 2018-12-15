import unittest
from src.connection_tester import ConnectionTester


class TestConnectionTester(unittest.TestCase):
    def setUp(self):
        self.connection_tester = ConnectionTester("www.google.com")

    def test_current_real_connection(self):
        have_connection = self.connection_tester.run_test()

        self.assertTrue(have_connection, "No connection established, this could be due to your connection being down or"
                                         "a software bug.")
