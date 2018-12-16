import logging
from datetime import datetime
from src.status_tracker import Status, StatusChange

logger = logging.getLogger(__name__)


class ConnectionEntry:
    def __init__(self, time: datetime, result: bool, status: Status, status_change: StatusChange):
        self._time = time
        self._result = result
        self._status = status
        self._status_change = status_change

    @classmethod
    def from_json(cls, json_entry: dict):
        if not all(key in json_entry for key in ("time", "result", "status", "status_change")):
            logger.error("Failed to create ConnectionEntry from dictionary: %s.", json_entry)
            raise ValueError("Dictionary '{dict}' did not contain one of; time, result, status or status_change."
                             .format(dict=json_entry))
        if any(key not in ("time", "result", "status", "status_change") for key in json_entry):
            logger.error("Failed to create ConnectionEntry from dictionary: %s.", json_entry)
            raise ValueError("Dictionary '{dict}' contains key which is not; time, result, status or status_change."
                             .format(dict=json_entry))

        return ConnectionEntry(datetime.strptime(json_entry["time"],
                                                 "%Y-%m-%d %H:%M:%S"),
                               bool(json_entry["result"]),
                               Status[json_entry["status"]],
                               StatusChange[json_entry["status_change"]])

    def to_json(self):
        json_dict = {
            "time": str(self._time),
            "result": self._result,
            "status": self._status.name,
            "status_change": self._status_change.name
        }

        return json_dict

    def __eq__(self, other):
        return ((isinstance(other, ConnectionEntry)) and
                (self._time == other._time) and
                (self._result == other._result) and
                (self._status == other._status) and
                (self._status_change == other._status_change))

    def __str__(self):
        return str(self.to_json())
