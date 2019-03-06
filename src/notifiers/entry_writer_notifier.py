import json
import os
import logging
from enum import Enum
from datetime import datetime

from src.notifiers.connection_entry import ConnectionEntry
from src.status_tracker import Status, StatusChange

logger = logging.getLogger(__name__)


class EntryWriter:
    def write_new_entry(self, entry: ConnectionEntry):
        pass


class EntryWriterNotifier:
    def __init__(self, writer: EntryWriter):
        self._writer = writer

    def notify(self, time: datetime, result: bool, status: Status, status_change: StatusChange):
        new_entry = ConnectionEntry(time, result, status, status_change)

        self._writer.write_new_entry(new_entry)


class FileType(Enum):
    NONE = 0
    JSON_LIST = 1


def prepare_data_file(file_path: str, file_type: FileType = FileType.NONE):
    logger.debug("Preparing data file at %s.", file_path)

    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    if os.path.isfile(file_path):
        logger.debug("Existing file found, do not recreate.")
        return

    with open(file_path, "w+") as new_file:
        logger.debug("No existing file found, create a new one.")
        if file_type == FileType.JSON_LIST:
            json.dump([], new_file)
