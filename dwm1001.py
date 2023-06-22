# Standard library imports
from dataclasses import dataclass
from enum import Enum
import math
import time
from typing import Tuple

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
    ENTER = b"\r"
    DOUBLE_ENTER = b"\r\r"
    LEP = b"lep"
    RESET = b"reset"


class ParsingError(Exception):
    pass


class UartDwm1001:
    # These delay periods were experimentally determined
    RESET_DELAY_PERIOD = 0.1
    SHELL_STARTUP_DELAY_PERIOD = 1.0
    SHELL_COMMAND_DELAY_PERIOD = 0.5

    def __init__(self, serial_handle: Serial) -> None:
        self.serial_handle = serial_handle

    def send_shell_command(self, command: ShellCommand) -> None:
        self.serial_handle.write(command.value)
        self.serial_handle.write(ShellCommand.ENTER.value)
        self.serial_handle.flush()

        time.sleep(self.SHELL_COMMAND_DELAY_PERIOD)

    def reset(self) -> None:
        self.send_shell_command(ShellCommand.RESET)

        time.sleep(self.RESET_DELAY_PERIOD)

    def enter_shell_mode(self) -> None:
        self.serial_handle.write(ShellCommand.DOUBLE_ENTER.value)
        self.serial_handle.flush()

        time.sleep(self.SHELL_STARTUP_DELAY_PERIOD)

    def exit_shell_mode(self) -> None:
        # If you quit shell mode (with `quit` command) without stopping
        # a running command, the command will automatically continue
        # when re-entering shell mode. This can be confusing, so we
        # reset the device instead to ensure previously-running commands
        # terminate.
        self.reset()


class Listener(UartDwm1001):
    def __init__(self, serial_handle: Serial) -> None:
        super().__init__(serial_handle)

        # Device may not have shutdown properly previously
        self.reset()
        self.enter_shell_mode()

    def start_position_reporting(self) -> None:
        self.send_shell_command(ShellCommand.LEP)

        # The first line after invoking the command will have part of
        # the shell prompt mixed in, which would mess up parsing.
        self.serial_handle.reset_input_buffer()

    def stop_position_reporting(self) -> None:
        self.send_shell_command(ShellCommand.ENTER)

    def wait_for_position_report(self) -> Tuple[TagId, TagPosition]:
        report = self.serial_handle.readline().decode().split(",")

        if len(report) != 8:
            raise ParsingError("Position report has unexpected length.")

        if report[0] != "POS":
            raise ParsingError("Position report has incorrect tag.")

        position_data = [float(substr) for substr in report[3:6]]
        position_data.append(int(report[6]))

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
