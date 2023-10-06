
import enum
import logging
import selectors
import socket
from threading import Thread

import mido

LOGGER = logging.getLogger(__name__)


class ConnectionStatus(enum.Enum):
    Connected = enum.auto()
    Connecting = enum.auto()
    Disconnected = enum.auto()


class MidiTcpServer(Thread):

    MIDI_CLIENT_NAME = "MIDI-TCP for Allen & Heath"
    MIDI_PORT_NAME = "Allen & Heath Desk"
    PORT = 51325
    POLL = 0.5 # seconds
    TIMEOUT = 5 # seconds

    def __init__(self, ip_address, nowait_midi=False, noname_midi=False, discovery=None):
        Thread.__init__(self, daemon=False)

        self._socket = None
        self._status = ConnectionStatus.Disconnected

        self._midi_in_port = None
        self._midi_out_port = None
        self._midi_parser = mido.tokenizer.Tokenizer()
        if nowait_midi:
            self._start_midi(noname=True)
        self._noname = noname_midi

        self._ip_addr = ip_address
        self._request_restart = False
        self._request_shutdown = False

        self._discovery = discovery

    @property
    def is_connected(self):
        return self._status == ConnectionStatus.Connected

    def run(self):
        with selectors.DefaultSelector() as selector:
            while not self._request_shutdown:

                if self._request_restart:
                    self._update_status(ConnectionStatus.Disconnected)
                    selector.unregister(self._socket)
                    self._socket.close()
                    self._request_restart = False

                self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                selector.register(self._socket, selectors.EVENT_READ)

                prev = b''
                timeout = 0
                while not self._request_restart and not self._request_shutdown:
                    ready = selector.select(self.POLL)

                    if self._request_restart or self._request_shutdown:
                        break

                    if self._status in [ConnectionStatus.Disconnected, ConnectionStatus.Connecting]:
                        if self._status == ConnectionStatus.Disconnected:
                            self._update_status(ConnectionStatus.Connecting)
                        try:
                            self._socket.connect((self._ip_addr, self.PORT))
                            self._update_status(ConnectionStatus.Connected)
                            self._start_midi(self._noname)
                        except OSError as error:
                            if error.errno not in [10060, 10065]:
                                LOGGER.error(error)
                        finally:
                            continue

                    if ready:
                        timeout = 0
                        try:
                            recv = prev + self._socket.recv(1024)
                        except ConnectionResetError:
                            LOGGER.info(f"Connection to {self._ip_addr} reset")
                            self._request_restart = True
                            continue

                        if not recv:
                            # Empty string: the other side has closed the connection
                            LOGGER.info(f"Connection to {self._ip_addr} lost")
                            self._request_restart = True
                            continue

                        self._midi_parser.feed(recv)
                        for message in self._midi_parser:
                            self._midi_out_port.send(mido.Message.from_bytes(message))

                    else:
                        timeout += self.POLL
                        if timeout >= self.TIMEOUT:
                            if self._discovery.name_for_ipv4(self._ip_addr):
                                # Still discoverable on the network, so don't reconnect
                                timeout = 0
                                continue
                            LOGGER.info(f"Not received anything for {self.TIMEOUT} seconds and device not discoverable. Attempting to reconnect.")
                            self._request_restart = True


    def stop(self):
        LOGGER.info("Shutting down...")
        self._request_shutdown = True
        self.join()
        if self._midi_in_port:
            self._midi_in_port.close()
        if self._midi_out_port:
            self._midi_out_port.close()

    def send(self, message):
        if self._socket:
            self._socket.sendall(message.bin())
        else:
            raise ConnectionError

    def _start_midi(self, noname=False):
        if noname:
            name = self.MIDI_PORT_NAME
        else:
            name = self._discovery.name_for_ipv4(self._ip_addr)
            if not name:
                self._request_restart = True
                return
            name = f"{self.MIDI_PORT_NAME} '{name}'"

        if not self._midi_in_port:
            self._midi_in_port = mido.open_input(
                name=name,
                virtual=True,
                client_name=self.MIDI_CLIENT_NAME,
                callback=self.send
            )
        if not self._midi_out_port:
            self._midi_out_port = mido.open_output(
                name=name,
                virtual=True,
                client_name=self.MIDI_CLIENT_NAME
            )

    def _update_status(self, new_status: ConnectionStatus):
        self._status = new_status
