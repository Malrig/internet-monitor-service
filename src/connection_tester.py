import logging
import socket

logger = logging.getLogger()


class ConnectionTester:
    def __init__(self, remote_to_check: str = "www.google.com"):
        logger.debug("PingTester created.")
        self.remote_to_check = remote_to_check

    def run_test(self) -> bool:
        try:
            # see if we can resolve the host name -- tells us if there is
            # a DNS listening
            host = socket.gethostbyname(self.remote_to_check)
            # connect to the host -- tells us if the host is actually
            # reachable
            socket.create_connection((host, 80), 2)
            return True
        except socket.error:
            logger.exception("Test")
            pass
        return False
