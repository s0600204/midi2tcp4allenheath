
import logging
import selectors
import socket
from threading import Lock, Thread


LOGGER = logging.getLogger(__name__)


class Discovery(Thread):

    ADDR = ("255.255.255.255", 51320)
    MSG = bytes("GLD Find\0V2\n", "utf-8")
    POLL = 0.5 # seconds
    RETRANSMIT_INTERVAL = 10 # seconds
    TIMEOUT = 15 # seconds, should be greater than RETRANSMIT_INTERVAL

    def __init__(self):
        Thread.__init__(self, daemon=True)

        self._socket = None
        self._request_shutdown = False
        self._request_retransmit = False

        self._storage_mutex = Lock()
        self._storage = {}

    def name_for_ipv4(self, ipv4):
        with self._storage_mutex:
            if ipv4 not in self._storage:
                return None
            return self._storage[ipv4]['name']

    def print_discovered(self):
        with self._storage_mutex:
            if not self._storage:
                print("No devices discovered.")
                return

            print("Devices discoved on network:")
            for address, details in self._storage:
                print(f"> {address} -- {details['name']}")

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
                        received, address = self._socket.recvfrom(1024)
                        LOGGER.info("Received: %s", received)

                        with self._storage_mutex:
                            if address[0] not in self._storage:
                                self._storage[address[0]] = {
                                    'name': str(received[:-1], 'UTF-8'),
                                }
                            self._storage[address[0]]['timeout'] = 0

                    else:
                        timeout += self.POLL
                        with self._storage_mutex:
                            for ipv4, context in self._storage.items():
                                if context['timeout'] >= self.TIMEOUT:
                                    del self._storage[ipv4]
                                else:
                                    context['timeout'] += self.POLL
                        if timeout >= self.RETRANSMIT_INTERVAL:
                            self._request_retransmit = True

    def stop(self):
        LOGGER.info("Stopping...")
        self._request_shutdown = True
        self._socket = None
        self.join()
