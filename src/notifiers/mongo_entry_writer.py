import logging
import json
from mongoengine import connect, Document, DateTimeField, BooleanField, StringField

from src.notifiers.connection_entry import ConnectionEntry
from src.notifiers.entry_writer_notifier import EntryWriter

logger = logging.getLogger(__name__)


class ConnectionDoc(Document):
    time = DateTimeField(required=True)
    result = BooleanField(required=True)
    status = StringField(required=True)
    status_change = StringField(required=True)

    @classmethod
    def from_connection_entry(cls, entry: ConnectionEntry):
        return ConnectionDoc.from_json(json.dumps(entry.to_json()))


class MongoEntryWriter(EntryWriter):
    def __init__(self, name: str, host: str, port: int):
        # Connect to MongoDB
        connect(name, host=host, port=port)

    def write_new_entry(self, entry: ConnectionEntry):
        logger.debug("Adding new entry: %s.", entry)

        new_entry = ConnectionDoc.from_connection_entry(entry)
        new_entry.save()
