
import argparse
import logging
import signal
import sys
from time import sleep

from . import __doc__ as DESCRIPTION
from .discovery import Discovery
from .server import MidiTcpServer
from .utils import restrict_ip, validate_ip


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
    console_handler.setLevel(logging.WARNING)
    root_logger.addHandler(console_handler)

    LOGGER = logging.getLogger(__name__)

    # Read the arguments passed
    parser = argparse.ArgumentParser(
        description=DESCRIPTION
    )
    parser.add_argument(
        "-a",
        "--address",
        help="IP (v4) Address of Target Device",
    )
    parser.add_argument(
        "-n",
        "--no-name",
        action='store_true',
        help="Don't name the local MIDI ports with the name of the attached desk.",
    )
    parser.add_argument(
        "-w",
        "--no-wait",
        action='store_true',
        help="Don't wait for a connection to a remote device to create MIDI ports locally. Implies no-name.",
    )
    args = parser.parse_args()

    # Validate IP Address, if one provided
    ip_address = None
    if args.address:
        if validate_ip(args.address):
            if restrict_ip(args.address):
                ip_address = args.address
            else:
                LOGGER.error("Please provide a valid IPv4 Address within an IETF Private Block.")
                quit()
        else:
            LOGGER.error("Invalid IPv4 Address supplied. Please recheck your entry.")
            quit()

    # Start Discovery
    discovery = Discovery()
    discovery.start()

    # Initialise server
    if ip_address:
        server = MidiTcpServer(ip_address, nowait_midi=args.no_wait, noname_midi=args.no_name, discovery=discovery)

    # Gracefully handle SIGTERM and SIGINT
    def handle_quit_signal(*_):
        discovery.stop()
        server.stop()

    signal.signal(signal.SIGTERM, handle_quit_signal)
    signal.signal(signal.SIGINT, handle_quit_signal)

    # Run the application
    if ip_address:
        server.start()
    else:
        print("Searching network, please wait...")
        sleep(2)
        discovery.print_discovered()


if __name__ == "__main__":
    main()

