import unittest
from datetime import datetime
from freezegun import freeze_time
from src.status_tracker import StatusChange, Status, StatusTracker


class TestStatusTracker(unittest.TestCase):
    def setUp(self):
        self.status_tracker = StatusTracker()

    def submit_result_and_expect(self, to_submit, expect_status, expect_status_change):
        status_change = self.status_tracker.submit_result(to_submit)

        self.assertEqual(expect_status, self.status_tracker.status)
        self.assertEqual(expect_status_change, status_change)

    def test_initialised_correctly(self):
        # External properties
        self.assertEqual(Status.UNKNOWN, self.status_tracker.status)
        self.assertEqual(datetime.min, self.status_tracker.last_success)
        # Internal properties
        self.assertEqual(5, self.status_tracker._number_retry_attempts)
        self.assertEqual(0, self.status_tracker._number_failures)

    @freeze_time("2018-08-03")
    def test_submit_result_status_first_ok(self):
        self.submit_result_and_expect(True, Status.OK, StatusChange.NONE)

        self.assertEqual(datetime(2018, 8, 3), self.status_tracker.last_success)

    @freeze_time("2018-08-03")
    def test_submit_result_status_ok_no_change(self):
        # Initial state
        self.status_tracker._status = Status.OK

        self.submit_result_and_expect(True, Status.OK, StatusChange.NONE)

        self.assertEqual(datetime(2018, 8, 3), self.status_tracker.last_success)

    def test_submit_result_status_warning_no_change(self):
        # Initial state
        self.status_tracker._status = Status.WARNING

        self.submit_result_and_expect(False, Status.WARNING, StatusChange.NONE)

        self.assertEqual(datetime.min, self.status_tracker.last_success)

    def test_submit_result_status_error_no_change(self):
        # Initial state
        self.status_tracker._status = Status.ERROR
        self.status_tracker._number_retry_attempts = 0

        self.submit_result_and_expect(False, Status.ERROR, StatusChange.NONE)

        self.assertEqual(datetime.min, self.status_tracker.last_success)

    def test_submit_result_status_ok_new_warning(self):
        # Initial state
        self.status_tracker._status = Status.OK

        self.submit_result_and_expect(False, Status.WARNING, StatusChange.NEW_WARNING)

        # Expect last success to have not changed
        self.assertEqual(datetime.min, self.status_tracker.last_success)

    def test_submit_result_status_ok_new_error(self):
        # Initial state
        self.status_tracker._status = Status.OK
        self.status_tracker._number_retry_attempts = 0

        self.submit_result_and_expect(False, Status.ERROR, StatusChange.NEW_ERROR)

        # Expect last success to have not changed
        self.assertEqual(datetime.min, self.status_tracker.last_success)

    def test_submit_result_status_warning_new_error(self):
        # Initial state
        self.status_tracker._status = Status.WARNING
        self.status_tracker._number_retry_attempts = 0

        self.submit_result_and_expect(False, Status.ERROR, StatusChange.NEW_ERROR)

        # Expect last success to have not changed
        self.assertEqual(datetime.min, self.status_tracker.last_success)

    @freeze_time("2018-08-03")
    def test_submit_result_status_warning_resolved(self):
        # Initial state
        self.status_tracker._status = Status.WARNING
        self.status_tracker._number_retry_attempts = 0

        self.submit_result_and_expect(True, Status.OK, StatusChange.WARNING_RESOLVED)
        self.assertEqual(datetime(2018, 8, 3), self.status_tracker.last_success)

    @freeze_time("2018-08-03")
    def test_submit_result_status_error_resolved(self):
        # Initial state
        self.status_tracker._status = Status.ERROR
        self.status_tracker._number_retry_attempts = 0

        self.submit_result_and_expect(True, Status.OK, StatusChange.ERROR_RESOLVED)

        self.assertEqual(datetime(2018, 8, 3), self.status_tracker.last_success)

    def test_submit_result_retry_attempts(self):
        self.submit_result_and_expect(False, Status.WARNING, StatusChange.NEW_WARNING)
        self.submit_result_and_expect(False, Status.WARNING, StatusChange.NONE)
        self.submit_result_and_expect(False, Status.WARNING, StatusChange.NONE)
        self.submit_result_and_expect(False, Status.WARNING, StatusChange.NONE)
        self.submit_result_and_expect(False, Status.WARNING, StatusChange.NONE)
        self.submit_result_and_expect(False, Status.ERROR, StatusChange.NEW_ERROR)

        # Expect last success to have not changed
        self.assertEqual(datetime.min, self.status_tracker.last_success)

    def test_set_status_invalid_value_error_to_warning(self):
        # Initial state
        self.status_tracker._status = Status.ERROR

        status_change = self.status_tracker._set_status(Status.WARNING)

        self.assertEqual(Status.WARNING, self.status_tracker.status)
        self.assertEqual(StatusChange.INVALID, status_change)
        self.assertEqual(datetime.min, self.status_tracker.last_success)

    def test_set_status_invalid_type(self):
        with self.assertRaises(TypeError):
            self.status_tracker._set_status(-1)

        self.assertEqual(Status.UNKNOWN, self.status_tracker.status)
        self.assertEqual(datetime.min, self.status_tracker.last_success)

    @freeze_time("2018-08-03")
    def test_set_status_invalid_initial_state(self):
        # Initial state
        self.status_tracker._status = -1

        status_change = self.status_tracker._set_status(Status.OK)

        self.assertEqual(Status.OK, self.status_tracker.status)
        self.assertEqual(StatusChange.INVALID, status_change)
        self.assertEqual(datetime(2018, 8, 3), self.status_tracker.last_success)
