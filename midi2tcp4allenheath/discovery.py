
import logging
import selectors
import socket
import sys
from threading import Thread


LOGGER = logging.getLogger(__name__)


class Discovery(Thread):

    ADDR = ("255.255.255.255", 51320)
    MSG = bytes("GLD Find\0V2\n", "utf-8")
    POLL = 0.5 # seconds
    RETRANSMIT_INTERVAL = 10 # seconds

    def __init__(self):
        Thread.__init__(self, daemon=True)

        self._socket = None
        self._request_shutdown = False
        self._request_retransmit = False

    def run(self):
        with selectors.DefaultSelector() as selector:

            self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            selector.register(self._socket, selectors.EVENT_READ)

            while not self._request_shutdown:

                LOGGER.info("Transmitting discovery message.")
                self._socket.sendto(self.MSG, self.ADDR)
                self._request_retransmit = False

                timeout = 0
                while not self._request_retransmit and not self._request_shutdown:
                    ready = selector.select(self.POLL)

                    if self._request_shutdown:
                        break

                    if ready:
                        received = self._socket.recvfrom(1024)
                        LOGGER.info(f"Received: {received}")

                    else:
                        timeout += self.POLL
                        if timeout >= self.RETRANSMIT_INTERVAL:
                            self._request_retransmit = True

    def stop(self):
        LOGGER.info("Stopping...")
        self._request_shutdown = True
        self._socket = None
        self.join()
