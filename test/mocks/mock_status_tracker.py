from src.status_tracker import StatusTracker
from unittest.mock import MagicMock


class MockStatusTracker(StatusTracker):
    def __init__(self, *args, **kwargs) -> None:
        super(StatusTracker, self).__init__(*args, **kwargs)

        # Mock out functions
        self.submit_result = MagicMock()
