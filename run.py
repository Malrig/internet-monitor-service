import os
import yaml
import logging.config

from apscheduler.schedulers.blocking import BlockingScheduler

from config import ROOT_DIR
from src.monitor import Monitor
from src.connection_tester import ConnectionTester
from src.status_tracker import StatusTracker
from src.notifiers.entry_writer_notifier import EntryWriterNotifier
from src.notifiers.json_entry_writer import JsonEntryWriter


def setup_logging() -> None:
    with open(os.path.join(ROOT_DIR, "logging.yaml"), "rt") as log_file:
        config = yaml.safe_load(log_file.read())
    logging.config.dictConfig(config)


setup_logging()

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    scheduler = BlockingScheduler()
    connection_tester = ConnectionTester()
    status_tracker = StatusTracker()
    json_writer = JsonEntryWriter(os.path.join(os.path.dirname(os.path.realpath(__file__)), "data", "test_data.json"))
    notifier = EntryWriterNotifier(json_writer)
    monitor_config = {
        "test_interval": 300,
        "retry_interval": 10,
        "error_interval": 60
    }
    monitor = Monitor(scheduler, connection_tester, status_tracker, notifier, monitor_config)

    try:
        logger.info("Run the first initial test.")
        monitor.run_test()
        logger.info("Start the scheduler proper.")
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Shutting down the scheduler.")
        scheduler.shutdown()
        pass
