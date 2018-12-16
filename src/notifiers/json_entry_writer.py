import logging
import json
from src.connection_entry import ConnectionEntry
from src.notifiers.entry_writer_notifier import EntryWriter, FileType, prepare_data_file

logger = logging.getLogger(__name__)


class JsonEntryWriter(EntryWriter):
    def __init__(self, output_file: str):
        self._output_file = output_file
        prepare_data_file(output_file, FileType.JSON_LIST)

    def write_new_entry(self, entry: ConnectionEntry):
        logger.debug("Adding new entry: %s.", entry)

        current_info = self._get_test_data()
        current_info.append(entry.to_json())

        self._save_test_data(current_info)

    def _get_test_data(self):
        with open(self._output_file, "r") as test_data:
            data = json.load(test_data)

        return data

    def _save_test_data(self, new_test_data: list):
        with open(self._output_file, "w") as test_data:
            json.dump(new_test_data, test_data)
