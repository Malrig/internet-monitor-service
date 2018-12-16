import unittest
from datetime import datetime
from src.connection_entry import ConnectionEntry
from src.status_tracker import Status, StatusChange


class TestConnectionEntry(unittest.TestCase):
    def test_initialisation(self):
        connection_entry = ConnectionEntry(datetime(2018, 8, 3),
                                           True,
                                           Status.OK,
                                           StatusChange.NEW_WARNING)

        self.assertEqual(datetime(2018, 8, 3), connection_entry._time)
        self.assertEqual(True, connection_entry._result)
        self.assertEqual(Status.OK, connection_entry._status)
        self.assertEqual(StatusChange.NEW_WARNING, connection_entry._status_change)

    def test_from_json_valid(self):
        input_json = {
            "time": str(datetime(2018, 8, 3)),
            "result": str(True),
            "status": Status.UNKNOWN.name,
            "status_change": StatusChange.WARNING_RESOLVED.name
        }

        connection_entry = ConnectionEntry.from_json(input_json)

        self.assertEqual(ConnectionEntry(datetime(2018, 8, 3),
                                         True,
                                         Status.UNKNOWN,
                                         StatusChange.WARNING_RESOLVED),
                         connection_entry)

    def test_from_json_missing_time(self):
        input_json = {
            "result": str(True),
            "status": Status.UNKNOWN.name,
            "status_change": StatusChange.WARNING_RESOLVED.name
        }

        with self.assertRaises(ValueError) as ex:
            ConnectionEntry.from_json(input_json)

        self.assertEqual("Dictionary '{dict}' did not contain one of; time, result, status or status_change."
                         .format(dict=input_json),
                         str(ex.exception))

    def test_from_json_missing_result(self):
        input_json = {
            "time": str(datetime(2018, 8, 3)),
            "status": Status.UNKNOWN.name,
            "status_change": StatusChange.WARNING_RESOLVED.name
        }

        with self.assertRaises(ValueError) as ex:
            ConnectionEntry.from_json(input_json)

        self.assertEqual("Dictionary '{dict}' did not contain one of; time, result, status or status_change."
                         .format(dict=input_json),
                         str(ex.exception))

    def test_from_json_missing_status(self):
        input_json = {
            "time": str(datetime(2018, 8, 3)),
            "result": str(True),
            "status_change": StatusChange.WARNING_RESOLVED.name
        }

        with self.assertRaises(ValueError) as ex:
            ConnectionEntry.from_json(input_json)

        self.assertEqual("Dictionary '{dict}' did not contain one of; time, result, status or status_change."
                         .format(dict=input_json),
                         str(ex.exception))

    def test_from_json_missing_status_change(self):
        input_json = {
            "time": str(datetime(2018, 8, 3)),
            "result": str(True),
            "status": Status.UNKNOWN.name,
        }

        with self.assertRaises(ValueError) as ex:
            ConnectionEntry.from_json(input_json)

        self.assertEqual("Dictionary '{dict}' did not contain one of; time, result, status or status_change."
                         .format(dict=input_json),
                         str(ex.exception))

    def test_from_json_extra_parameters(self):
        input_json = {
            "time": str(datetime(2018, 8, 3)),
            "result": str(True),
            "status": Status.UNKNOWN.name,
            "status_change": StatusChange.WARNING_RESOLVED.name,
            "additional_parameter": "unknown_parameter"
        }

        with self.assertRaises(ValueError) as ex:
            ConnectionEntry.from_json(input_json)

        self.assertEqual("Dictionary '{dict}' contains key which is not; time, result, status or status_change."
                         .format(dict=input_json),
                         str(ex.exception))

    def test_to_json(self):
        connection_entry = ConnectionEntry(datetime(2018, 8, 3),
                                           True,
                                           Status.OK,
                                           StatusChange.NEW_WARNING)

        self.assertEqual({
                "time": str(datetime(2018, 8, 3)),
                "result": True,
                "status": Status.OK.name,
                "status_change": StatusChange.NEW_WARNING.name
            },
            connection_entry.to_json()
        )

    def test_to_from_json_loop(self):
        first_connection_entry = ConnectionEntry(datetime(2018, 8, 3),
                                                 True,
                                                 Status.OK,
                                                 StatusChange.NEW_WARNING)

        second_connection_entry = ConnectionEntry.from_json(first_connection_entry.to_json())

        self.assertEqual(first_connection_entry,
                         second_connection_entry)

    def test_from_to_json_loop(self):
        first_json = {
            "time": str(datetime(2018, 8, 3)),
            "result": True,
            "status": Status.UNKNOWN.name,
            "status_change": StatusChange.WARNING_RESOLVED.name
        }

        second_json = ConnectionEntry.from_json(first_json).to_json()

        self.assertEqual(first_json, second_json)
