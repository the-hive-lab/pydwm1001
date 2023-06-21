# Standard library imports
from dataclasses import dataclass
from enum import Enum
import math
import time

# Third party imports
from serial import Serial


class TagId(str):
    pass


@dataclass
class TagPosition:
    x_m: float
    y_m: float
    z_m: float
    quality: int

    def almost_equal(self, other: "TagPosition") -> bool:
        return (
            math.isclose(self.x_m, other.x_m)
            and math.isclose(self.y_m, other.y_m)
            and math.isclose(self.z_m, other.z_m)
            and self.quality == other.quality
        )


class ShellCommand(Enum):
    DOUBLE_ENTER = b"\r\r"
    LEP = b"lep"


class Listener:
    def __init__(self, serial_handle: Serial) -> None:
        self.serial_handle = serial_handle

        self.serial_handle.write(ShellCommand.DOUBLE_ENTER.value)
        time.sleep(1)
        self.serial_handle.write(ShellCommand.LEP.value)

    def wait_for_position_report(self) -> tuple[TagId, TagPosition]:
        report = self.serial_handle.readline().decode().split(",")

        if len(report) != 8 or report[0] != "POS":
            raise ValueError("Could not parse position report.")

        position_data = [float(substr) for substr in report[3:7]]

        return TagId(report[2]), TagPosition(*position_data)


class Tag:
    def __init__(self, serial_handle) -> None:
        self.serial_handle = serial_handle

        self.serial_handle.write(ShellCommand.DOUBLE_ENTER.value)
        time.sleep(1)
        self.serial_handle.write(ShellCommand.LEP)

    @property
    def position(self) -> TagPosition:
        report = self.serial_handle.readline().decode().split(",")

        if len(report) != 5 or report[0] != "POS":
            raise ValueError("Could not parse position report.")

        position_data = [float(substr) for substr in report[1:]]

        return TagPosition(*position_data)
