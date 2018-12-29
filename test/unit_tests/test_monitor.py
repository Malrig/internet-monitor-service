import unittest
from unittest.mock import MagicMock
from freezegun import freeze_time
from datetime import datetime, timedelta
from apscheduler.schedulers.blocking import BaseScheduler
from parameterized import parameterized

from src.status_tracker import Status, StatusChange

from test.mocks.mock_connection_tester import MockConnectionTester
from test.mocks.mock_status_tracker import StatusTracker
from test.mocks.notifiers.mock_entry_writer_notifier import MockEntryWriterNotifier

from src.monitor import Monitor, REQUIRED_CONFIG


class MockScheduler(BaseScheduler):
    def __init__(self, *args, **kwargs):
        super(BaseScheduler, self).__init__(*args, **kwargs)

        # Mock out functions
        self.shutdown = MagicMock()
        self.wakeup = MagicMock()
        self.add_job = MagicMock()

    def wakeup(self):
        pass

    def shutdown(self, wait=True):
        pass


class TestMonitorInitialisation(unittest.TestCase):
    def setUp(self):
        self.mock_scheduler = MockScheduler()
        self.mock_tester = MockConnectionTester()
        self.mock_status_tracker = StatusTracker()
        self.mock_notifier = MockEntryWriterNotifier()

    def test_successful_initialisation(self):
        monitor_config = {
            "test_interval": 40,
            "retry_interval": 5,
            "error_interval": 10
        }

        monitor = Monitor(self.mock_scheduler,
                          self.mock_tester,
                          self.mock_status_tracker,
                          self.mock_notifier,
                          monitor_config)

        self.assertEqual(monitor._config, monitor_config)

    def test_missing_test_interval(self):
        monitor_config = {
            "retry_interval": 5,
            "error_interval": 10
        }

        with self.assertRaises(ValueError) as ex:
            Monitor(self.mock_scheduler,
                    self.mock_tester,
                    self.mock_status_tracker,
                    self.mock_notifier,
                    monitor_config)

        self.assertEqual("Dictionary '{dict}' did not contain one of; {required}."
                         .format(dict=monitor_config, required=REQUIRED_CONFIG),
                         str(ex.exception))

    def test_missing_retry_interval(self):
        monitor_config = {
            "test_interval": 40,
            "error_interval": 10
        }

        with self.assertRaises(ValueError) as ex:
            Monitor(self.mock_scheduler,
                    self.mock_tester,
                    self.mock_status_tracker,
                    self.mock_notifier,
                    monitor_config)

        self.assertEqual("Dictionary '{dict}' did not contain one of; {required}."
                         .format(dict=monitor_config, required=REQUIRED_CONFIG),
                         str(ex.exception))

    def test_missing_error_interval(self):
        monitor_config = {
            "test_interval": 40,
            "retry_interval": 5
        }

        with self.assertRaises(ValueError) as ex:
            Monitor(self.mock_scheduler,
                    self.mock_tester,
                    self.mock_status_tracker,
                    self.mock_notifier,
                    monitor_config)

        self.assertEqual("Dictionary '{dict}' did not contain one of; {required}."
                         .format(dict=monitor_config, required=REQUIRED_CONFIG),
                         str(ex.exception))

    def test_additional_parameter(self):
        monitor_config = {
            "test_interval": 40,
            "retry_interval": 5,
            "error_interval": 10,
            "random_parameter": 50
        }

        with self.assertRaises(ValueError) as ex:
            Monitor(self.mock_scheduler,
                    self.mock_tester,
                    self.mock_status_tracker,
                    self.mock_notifier,
                    monitor_config)

        self.assertEqual("Dictionary '{dict}' contains key which is not; {required}."
                         .format(dict=monitor_config, required=REQUIRED_CONFIG),
                         str(ex.exception))


class TestMonitorRunTest(unittest.TestCase):
    def setUp(self):
        self.mock_scheduler = MockScheduler()
        self.mock_tester = MockConnectionTester()
        self.mock_status_tracker = StatusTracker()
        self.mock_notifier = MockEntryWriterNotifier()
        self.monitor_config = {
            "test_interval": 40,
            "retry_interval": 5,
            "error_interval": 10
        }

        self.monitor = Monitor(self.mock_scheduler,
                               self.mock_tester,
                               self.mock_status_tracker,
                               self.mock_notifier,
                               self.monitor_config)

    # Run tests with various different returns (e.g. new_error etc).

    def generic_run_test(self, test_result: bool, status_change: StatusChange, status: Status, interval_type: str):
        self.mock_tester.run_test = MagicMock(return_value=test_result)
        self.mock_status_tracker.submit_result = MagicMock(return_value=status_change)
        self.mock_status_tracker._status = status

        self.monitor.run_test()

        self.mock_tester.run_test.assert_called()
        self.mock_status_tracker.submit_result.assert_called_with(test_result)
        self.mock_notifier.notify.assert_called_with(datetime(2018, 8, 3), test_result, status, status_change)
        new_run_date = datetime(2018, 8, 3) + timedelta(seconds=self.monitor_config[interval_type])
        self.mock_scheduler.add_job.assert_called_with(self.monitor.run_test, "date", run_date=new_run_date)

    @parameterized.expand([
        ("invalid", StatusChange.INVALID),
        ("none", StatusChange.NONE),
        ("error_resolved", StatusChange.ERROR_RESOLVED),
        ("warning_resolved", StatusChange.WARNING_RESOLVED),
        ("new_error", StatusChange.NEW_ERROR),
        ("new_warning", StatusChange.NEW_WARNING)
    ])
    @freeze_time("2018-08-03")
    def test_run_test_ok_status_uses_test_interval_with_status_change(self,
                                                                      name: str,
                                                                      status_change: StatusChange):
        self.generic_run_test(True, status_change, Status.OK, "test_interval")

    @parameterized.expand([
        ("invalid", StatusChange.INVALID),
        ("none", StatusChange.NONE),
        ("error_resolved", StatusChange.ERROR_RESOLVED),
        ("warning_resolved", StatusChange.WARNING_RESOLVED),
        ("new_error", StatusChange.NEW_ERROR),
        ("new_warning", StatusChange.NEW_WARNING)
    ])
    @freeze_time("2018-08-03")
    def test_run_test_warning_status_uses_retry_interval_with_status_change(self,
                                                                            name: str,
                                                                            status_change: StatusChange):
        self.generic_run_test(False, status_change, Status.WARNING, "retry_interval")

    @parameterized.expand([
        ("invalid", StatusChange.INVALID),
        ("none", StatusChange.NONE),
        ("error_resolved", StatusChange.ERROR_RESOLVED),
        ("warning_resolved", StatusChange.WARNING_RESOLVED),
        ("new_error", StatusChange.NEW_ERROR),
        ("new_warning", StatusChange.NEW_WARNING)
    ])
    @freeze_time("2018-08-03")
    def test_run_test_error_status_uses_error_interval_with_status_change(self,
                                                                          name: str,
                                                                          status_change: StatusChange):
        self.generic_run_test(False, status_change, Status.ERROR, "error_interval")
