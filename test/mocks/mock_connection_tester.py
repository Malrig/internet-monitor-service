from src.connection_tester import ConnectionTester
from unittest.mock import MagicMock


class MockConnectionTester(ConnectionTester):
    def __init__(self, *args, **kwargs):
        super(ConnectionTester, self).__init__(*args, **kwargs)

        # Mock out functions
        self.run_test = MagicMock()
