#!/usr/bin/env python3

# Standard library imports
from pathlib import Path
import sys
from typing import NoReturn

# Third party imports
from serial import Serial

# Allows us to find dwm1001 library without installing it
sys.path.append(str(Path(__file__).resolve().parents[1]))
import dwm1001


def main() -> NoReturn:
    serial_handle = Serial("/dev/ttyACM0", baudrate=115_200)
    listener = dwm1001.Listener(serial_handle)
    listener.start_position_reporting()

    while True:
        tag_id, tag_position = listener.wait_for_position_report()
        print(f"{tag_id}: {tag_position}")


if __name__ == "__main__":
    main()
