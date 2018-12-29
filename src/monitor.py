import logging
from copy import deepcopy
from datetime import datetime, timedelta
from apscheduler.schedulers.blocking import BaseScheduler

from src.connection_tester import ConnectionTester
from src.status_tracker import StatusTracker, Status
from src.notifiers.entry_writer_notifier import EntryWriterNotifier


logger = logging.getLogger(__name__)

REQUIRED_CONFIG = (
    "test_interval",
    "retry_interval",
    "error_interval"
)


class Monitor:
    def __init__(self,
                 scheduler: BaseScheduler,
                 tester: ConnectionTester,
                 status_tracker: StatusTracker,
                 notifier: EntryWriterNotifier,
                 monitor_config: dict):
        self._scheduler = scheduler
        self._tester = tester
        self._status_tracker = status_tracker
        self._notifier = notifier
        self._validate_config(monitor_config)
        self._config = deepcopy(monitor_config)

    @classmethod
    def _validate_config(cls, to_validate):
        if not all(key in to_validate for key in REQUIRED_CONFIG):
            logger.error("Configuration failed validation, does not contain one of %s: %s.",
                         REQUIRED_CONFIG, to_validate)
            raise ValueError("Dictionary '{dict}' did not contain one of; {required}."
                             .format(dict=to_validate, required=REQUIRED_CONFIG))
        if any(key not in REQUIRED_CONFIG for key in to_validate):
            logger.error("Configuration failed validation, contains key which is not one of %s: %s.",
                         REQUIRED_CONFIG, to_validate)
            raise ValueError("Dictionary '{dict}' contains key which is not; {required}."
                             .format(dict=to_validate, required=REQUIRED_CONFIG))

    def _schedule_next_job(self, next_run_time: datetime):
        logger.info("Scheduling next job for %s.", next_run_time)
        self._scheduler.add_job(self.run_test, "date", run_date=next_run_time)

    def _get_next_job_time(self, previous_run_time: datetime, status: Status) -> datetime:
        if status == Status.OK:
            job_delay = self._config["test_interval"]
        elif status == Status.WARNING:
            job_delay = self._config["retry_interval"]
        elif status == Status.ERROR:
            job_delay = self._config["error_interval"]
        else:
            logger.error("Invalid branch reached, status s not recognised.", status)
            job_delay = self._config["error_interval"]

        next_time = previous_run_time + timedelta(seconds=job_delay)

        return next_time

    def run_test(self):
        logger.info("Beginning test run.")
        run_time = datetime.now()

        result = self._tester.run_test()

        status_change = self._status_tracker.submit_result(result)
        status = self._status_tracker.status

        self._notifier.notify(run_time, result, status, status_change)

        self._schedule_next_job(self._get_next_job_time(run_time, status))
