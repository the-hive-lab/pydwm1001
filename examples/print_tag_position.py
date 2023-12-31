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
    tag = dwm1001.ActiveTag(serial_handle)
    tag.start_position_reporting()

    while True:
        print(tag.position)


if __name__ == "__main__":
    main()
