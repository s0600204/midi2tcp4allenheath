
import argparse
import logging
import signal
import sys

from .server import MidiTcpServer


def main():

    # Setup logging
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    logging_format = logging.Formatter(
        datefmt='%Y-%m-%d %H:%M:%S',
        fmt="{asctime}\t{levelname}\t{name}::{funcName}\t{message}",
        style='{')

    # Write to console stdout/stderr
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging_format)
    console_handler.setLevel(logging.INFO)
    root_logger.addHandler(console_handler)

    # Read the arguments passed
    parser = argparse.ArgumentParser(
        description="MIDI <-> TCP Server for Allen & Heath Desks"
    )
    parser.add_argument(
        "-a",
        "--address",
        required=True,
        help="IP (v4) Address of Target Device",
    )
    parser.add_argument(
        "-w",
        "--no-wait",
        action='store_true',
        help="Don't wait for a connection to a remote device to create MIDI ports locally.",
    )
    args = parser.parse_args()

    # @todo: validate this
    ip_address = args.address

    # Initialise server
    server = MidiTcpServer(ip_address, nowait_midi=args.no_wait)

    # Gracefully handle SIGTERM and SIGINT
    def handle_quit_signal(*_):
        server.stop()

    signal.signal(signal.SIGTERM, handle_quit_signal)
    signal.signal(signal.SIGINT, handle_quit_signal)

    # Run the application
    server.start()


if __name__ == "__main__":
    main()

