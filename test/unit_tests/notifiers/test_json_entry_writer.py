import unittest
import os
import json
from datetime import datetime
from unittest.mock import MagicMock, patch

from src.notifiers.json_entry_writer import JsonEntryWriter, FileType
from src.status_tracker import Status, StatusChange
from src.notifiers.connection_entry import ConnectionEntry

connection_entry_data = [
    {
        "time": "2018-08-03 20:35:43",
        "result": True,
        "status": "UNKNOWN",
        "status_change": "WARNING_RESOLVED"
    },
    {
        "time": "2018-08-03 22:35:43",
        "result": False,
        "status": "ERROR",
        "status_change": "NEW_ERROR"
    }
]


class TestJsonEntryWriterInitialisation(unittest.TestCase):
    def setUp(self):
        self.data_file = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                      "test_data.json")

    def tearDown(self):
        os.remove(self.data_file)

    def test_initiation_creates_file(self):
        json_writer = JsonEntryWriter(self.data_file)

        self.assertEquals(1, os.path.exists(self.data_file))
        self.assertEquals([], json_writer._get_test_data())

    def test_initiation_doesnt_override_existing_file(self):
        with open(self.data_file, "w+") as new_json_file:
            json.dump(connection_entry_data, new_json_file)

        JsonEntryWriter(self.data_file)

        with open(self.data_file, "r") as blame_data:
            data = json.load(blame_data)
            self.assertListEqual(connection_entry_data, data)


class TestJsonEntryWriterWithFile(unittest.TestCase):
    def setUp(self):
        self.data_file = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                      "test_data.json")

        with open(self.data_file, "w+") as new_json_file:
            json.dump(connection_entry_data, new_json_file)

        self.json_writer = JsonEntryWriter(self.data_file)

    def tearDown(self):
        os.remove(self.data_file)

    def test_write_entry(self):
        new_entry = ConnectionEntry(datetime(2018, 9, 24),
                                    True,
                                    Status.WARNING,
                                    StatusChange.ERROR_RESOLVED)
        self.json_writer.write_new_entry(new_entry)

        final_data = [
            {
                "time": "2018-08-03 20:35:43",
                "result": True,
                "status": "UNKNOWN",
                "status_change": "WARNING_RESOLVED"
            },
            {
                "time": "2018-08-03 22:35:43",
                "result": False,
                "status": "ERROR",
                "status_change": "NEW_ERROR"
            },
            {
                "time": "2018-09-24 00:00:00",
                "result": True,
                "status": "WARNING",
                "status_change": "ERROR_RESOLVED"
            }
        ]

        with open(self.data_file, "r") as blame_data:
            data = json.load(blame_data)
            self.assertListEqual(final_data, data)


class TestJsonEntryWriterWithoutFile(unittest.TestCase):
    def setUp(self):
        # Mock external dependencies
        self.patcher = patch("src.notifiers.json_entry_writer.prepare_data_file")
        self.addCleanup(self.patcher.stop)
        self.mock_prepare_data_file = self.patcher.start()

        self.json_writer = JsonEntryWriter("some_invalid_file_path")

        # Mock internal functions
        self.json_writer._get_test_data = MagicMock(return_value=connection_entry_data)
        self.json_writer._save_test_data = MagicMock()

    def test_create_blame_entry(self):
        new_entry = ConnectionEntry(datetime(2018, 9, 24),
                                    True,
                                    Status.WARNING,
                                    StatusChange.ERROR_RESOLVED)
        self.json_writer.write_new_entry(new_entry)

        final_data = [
            {
                "time": "2018-08-03 20:35:43",
                "result": True,
                "status": "UNKNOWN",
                "status_change": "WARNING_RESOLVED"
            },
            {
                "time": "2018-08-03 22:35:43",
                "result": False,
                "status": "ERROR",
                "status_change": "NEW_ERROR"
            },
            {
                "time": "2018-09-24 00:00:00",
                "result": True,
                "status": "WARNING",
                "status_change": "ERROR_RESOLVED"
            }
        ]

        self.mock_prepare_data_file.assert_called_with("some_invalid_file_path", FileType.JSON_LIST)
        self.json_writer._get_test_data.assert_called()
        self.json_writer._save_test_data.assert_called_with(final_data)
