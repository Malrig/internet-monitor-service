import logging
from enum import Enum
from datetime import datetime

logger = logging.getLogger(__name__)


class Status(Enum):
    """
        This enum is used to indicate the status of the app being monitored.
    """
    UNKNOWN = 0     # Status of app has not yet been established
    OK = 1          # App is running as expected
    WARNING = 2     # Some tests have been failed but not enough to warrant reporting an error
    ERROR = 3       # The app has displayed an issue consistently


class StatusChange(Enum):
    INVALID = -1
    NONE = 0
    ERROR_RESOLVED = 1
    WARNING_RESOLVED = 2
    NEW_ERROR = 3
    NEW_WARNING = 4


class StatusTracker:
    def __init__(self, number_retry_attempts=None) -> None:
        # Don't know the initial status
        self._status = Status.UNKNOWN
        self._last_successful_run = datetime.min
        self._number_failures = 0

        # Config to be set somehow
        self._number_retry_attempts = number_retry_attempts or 5

    @property
    def status(self) -> Status:
        return self._status

    @property
    def last_success(self) -> datetime:
        return self._last_successful_run

    def submit_result(self, test_passed: bool) -> StatusChange:
        if not test_passed:
            self._number_failures += 1
        else:
            self._number_failures = 0

        if self._number_failures == 0:
            new_status = Status.OK
        elif self._number_failures < self._number_retry_attempts + 1:
            new_status = Status.WARNING
        else:
            new_status = Status.ERROR

        return self._set_status(new_status)

    def _set_status(self, status: Status) -> StatusChange:
        if not isinstance(status, Status):
            raise TypeError("Received type {type} when expected type <enum 'Status'>.".format(type=type(status)))

        logger.info("Setting status to %s", status)

        # No status change just return.
        if status == self._status:
            logger.debug("Branch: no status change.")
            # Make sure to update the last_successful_run if the status is OK and it hasn't changed.
            if self._status == Status.OK:
                self._last_successful_run = datetime.now()

            status_change = StatusChange.NONE

        # Below branches all handle different status *changes*
        elif ((self._status != Status.OK) and
              (status == Status.OK)):
            logger.debug("Branch: status set to OK.")
            resolved_time = datetime.now()

            if self._status == Status.ERROR:
                status_change = StatusChange.ERROR_RESOLVED
            elif self.status == Status.WARNING:
                status_change = StatusChange.WARNING_RESOLVED
            elif self.status == Status.UNKNOWN:
                status_change = StatusChange.NONE
            else:
                logger.error("Invalid current status set, current value is %s", self.status)
                status_change = StatusChange.INVALID

            self._last_successful_run = resolved_time

        elif ((self._status != Status.WARNING) and
              (status == Status.WARNING)):
            logger.debug("Branch: status set to WARNING.")
            status_change = StatusChange.NEW_WARNING

            if self._status == Status.ERROR:
                logger.error("Invalid branch reached in set_error_status of EmailNotifier. "
                             "Downgrading from ERROR to WARNING is not supported.")
                status_change = StatusChange.INVALID

        elif ((self._status != Status.ERROR) and
              (status == Status.ERROR)):
            logger.debug("Branch: status set to ERROR.")
            status_change = StatusChange.NEW_ERROR

        else:
            logger.error(
                "Invalid branch reached in set_error_status of EmailNotifier. "
                "Current status: %s, New status: %s.", self._status, status)
            status_change = StatusChange.INVALID

        # Regardless of which branch we use need to update the status.
        self._status = status

        return status_change
