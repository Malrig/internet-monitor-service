import unittest
import docker
# import os
# import json
from datetime import datetime

from src.notifiers.mongo_entry_writer import MongoEntryWriter, ConnectionDoc
from src.status_tracker import Status, StatusChange
from src.notifiers.connection_entry import ConnectionEntry

from test.mocks.mongo_utils.mock_mongo_db import MongoMocked


class TestConnectionDoc(unittest.TestCase):
    def setUp(self):
        self.test_entry = ConnectionEntry(datetime(2018, 9, 24),
                                          True,
                                          Status.WARNING,
                                          StatusChange.ERROR_RESOLVED)

    def test_initialisation(self):
        doc = ConnectionDoc(time=self.test_entry.to_json()["time"],
                            result=self.test_entry.to_json()["result"],
                            status=self.test_entry.to_json()["status"],
                            status_change=self.test_entry.to_json()["status_change"])

        self.assertEqual(self.test_entry.to_json()["time"], doc.time)
        self.assertEqual(self.test_entry.to_json()["result"], doc.result)
        self.assertEqual(self.test_entry.to_json()["status"], doc.status)
        self.assertEqual(self.test_entry.to_json()["status_change"], doc.status_change)

    def test_from_connection_entry(self):
        doc = ConnectionDoc.from_connection_entry(self.test_entry)

        self.assertEqual(self.test_entry.to_json()["time"], doc.time)
        self.assertEqual(self.test_entry.to_json()["result"], doc.result)
        self.assertEqual(self.test_entry.to_json()["status"], doc.status)
        self.assertEqual(self.test_entry.to_json()["status_change"], doc.status_change)


class TestMongoEntryWriter(unittest.TestCase):
    mocked_db: MongoMocked

    @classmethod
    def setUpClass(cls):
        cls.mocked_db = MongoMocked()

    @classmethod
    def tearDownClass(cls):
        cls.mocked_db.tear_down_mongo()

    def setUp(self):
        self.mongo_writer = MongoEntryWriter(None, "localhost", 27017)

    def tearDown(self):
        self.mocked_db.clean_mongo()

    def test_write_new_entry(self):
        entry = ConnectionEntry(datetime(2018, 9, 24),
                                True,
                                Status.WARNING,
                                StatusChange.ERROR_RESOLVED)
        expected_object = ConnectionDoc.from_connection_entry(entry)

        self.mongo_writer.write_new_entry(entry)

        entry_objects = ConnectionDoc.objects
        new_object = entry_objects[0]

        self.assertEqual(1, len(entry_objects))
        self.assertEqual(datetime(2018, 9, 24), new_object.time)
        self.assertEqual(expected_object.result, new_object.result)
        self.assertEqual(expected_object.status, new_object.status)
        self.assertEqual(expected_object.status_change, new_object.status_change)
