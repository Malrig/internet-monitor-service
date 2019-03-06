import unittest
import os
import json
from datetime import datetime
from unittest.mock import MagicMock

from src.notifiers.entry_writer_notifier import EntryWriterNotifier, EntryWriter, FileType, prepare_data_file
from src.status_tracker import Status, StatusChange
from src.notifiers.connection_entry import ConnectionEntry


class TestEntryWriterNotifier(unittest.TestCase):
    def setUp(self):
        self.entry_writer = EntryWriter()
        self.entry_writer.write_new_entry = MagicMock()

        self.entry_writer_notifier = EntryWriterNotifier(self.entry_writer)

    def test_entry_writer_notify(self):
        self.entry_writer_notifier.notify(datetime(2018, 8, 3), True, Status.OK, StatusChange.ERROR_RESOLVED)

        self.entry_writer.write_new_entry.assert_called_with(ConnectionEntry(datetime(2018, 8, 3),
                                                                             True,
                                                                             Status.OK,
                                                                             StatusChange.ERROR_RESOLVED))


class TestPrepareDataFile(unittest.TestCase):
    def setUp(self):
        self.data_file = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                      "test_data.json")

    def tearDown(self):
        os.remove(self.data_file)

    def test_creates_file(self):
        prepare_data_file(self.data_file)

        self.assertEquals(1, os.path.exists(self.data_file))
        with open(self.data_file, "r") as file:
            contents = file.read()
            self.assertEqual("", contents)

    def test_doesnt_override_existing_file(self):
        with open(self.data_file, "w+") as new_json_file:
            new_json_file.write("Putting some text into the file")

        prepare_data_file(self.data_file)

        with open(self.data_file, "r") as file:
            contents = file.read()
            self.assertEqual("Putting some text into the file", contents)

    def test_creates_json_list_file(self):
        prepare_data_file(self.data_file, file_type=FileType.JSON_LIST)

        self.assertEquals(1, os.path.exists(self.data_file))
        with open(self.data_file, "r") as json_file:
            json_data = json.load(json_file)
            self.assertEqual([], json_data)
