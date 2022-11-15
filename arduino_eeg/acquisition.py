"""
A class defining an Arduino data logger to enable configurable data acquisition. 
Author: Patrick McCarthy
"""


# Python standard package imports
import time
import csv

# third-party package imports
import serial
from serial.tools import list_ports

# TODO: - finish acquisition class (including writing to another process which will accept)
#       - callback implementation example script
#       - draft real-time signal processing
#       - create custom exception class
#       - refactor out to exist as module
#       - convert print statements to log output so log output can be saved


class ConnectionException(BaseException):
    # TODO: define custom exception class to throw when issues with serial connection to Arduino
    #       are encountered
    ...


class ArduinoAcquisition:
    """Arduino data logger for configurable data acquisition from a serial connection to pin A0
    of Ardunio Uno (or equivalent) connected via a USB-USBC adapter.
    """

    def __init__(
        self, baud_rate: int = 9600, fs: int = 500, timeout: float = 10
    ) -> None:
        """Class constructor.

        Args:
            baud_rate (int): Baud rate for serial comms [Hz].
            fs (int): Sampling frequency of Arduino [Hz].
            timeout (float): Timeout for serial port [ms].
        """
        # initialise acquisition parameters
        self.baud_rate = baud_rate
        self.fs = fs  # TODO: raise exception if sampling frequency is above maximum
        self.timeout = timeout
        self.is_setup = False
        self.port = "/dev/.tty.usbmodem1301"
        self.conn_open = False

    def _find_port(self):
        """Internal function to find port to which Arduino is connected."""

        # list ports
        ports = list_ports.comports()

        # find port corresponding to Arduino
        for port in ports:
            if port.manufacturer.startswith("Arduino"):
                self.port = port.split(" ")[0]

    def setup(self) -> None:
        """Enable serial communication with Arduino by establishing connection to port
        at which it is connected.

        Raises:
            ..."""
        # change state of setup variable
        self.is_setup = True

        # find Arduino port
        self._find_port()

        # establish connection with Arduino (pin A0)
        try:
            # TODO: automate finding Arduino port
            self.arduino_conn = serial.Serial(
                "/dev/tty.usbmodem1201", baudrate=self.baud_rate, timeout=self.timeout
            )
            self.conn_open = True
            # notify user that
            print(f"Established connection with Arduino at port: {self.port}.")
        except:
            raise BaseException("Could not establish connection with Arduino.")

    def run(
        self,
        acq_period: float,
        dest_path: str,
        call_back: callable = None,
        call_back_args: dict = None,
    ) -> None:
        """Run acquisition

        Args:
            acq_period (float): Period of acquisition [secs].
            dest_path (str): Full path of CSV file to save data (excluding extension).
            call_back (callable): Optional callback function to be called each time
                new data is available (if provided).

        Raises:
            ...
        """
        if not self.is_setup:
            raise BaseException("Arduino has not been configured for acquisition.")

        with open(f"{dest_path}.csv", "w") as file:

            # CSV writer object
            writer = csv.writer(file, delimiter=",")

            # acquire data based on acquisition parameters
            start_time = time.time()
            the_time = start_time

            # notify user that acquisition is beginning
            print(
                f"Beginning acquisiton of {acq_period} seconds, writing to file: {dest_path}.csv"
            )

            # acquisition loop
            while time.time() - start_time < acq_period:

                # only acquire if data longer than sample rate
                if time.time() - the_time < 1 / self.fs:

                    # retrieve data from serial port
                    read_data = self.arduino_conn.readline().decode()

                    # remove return characters
                    read_data = read_data.strip("\r\n")

                    # if callback function supplied, call and pass data
                    if call_back is not None:
                        call_back(read_data, **call_back_args)

                    # write to file (pass as list to avoid char separation)
                    writer.writerow([read_data])

                    # update time-keeping variable
                    the_time = time.time()

            # notify user that acquisition has finished
            print("Acquisition finished.")

    def finish(self) -> None:
        """Close connection to Arduino.

        Raises:
            ...
        """
        # close serial connection if it exists
        if not self.conn_open:
            BaseException("There is no connection with Arduino.")
        else:
            # close serial connection
            self.arduino_conn.close()
            # notify user that serial connection is closed
            print("Closed connection with Arduino.")
