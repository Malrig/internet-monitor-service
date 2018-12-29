from src.notifiers.entry_writer_notifier import EntryWriterNotifier
from unittest.mock import MagicMock


class MockEntryWriterNotifier(EntryWriterNotifier):
    def __init__(self, *args, **kwargs):
        super(EntryWriterNotifier, self).__init__(*args, **kwargs)

        # Mock out functions
        self.notify = MagicMock()
