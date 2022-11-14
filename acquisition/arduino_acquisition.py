"""
A class defining an Arduino data logger to enable configurable data acquisition. 
Author: Patrick McCarthy
"""

# TODO: configure as a module

# Python standard package imports
import time
import csv

# third-party package imports
import serial

# TODO: - callback implementation
#       - finish acquisition class (including writing to another process which will accept)
#       - callback implementation example script
#       - draft real-time signal processing
#       - create custom exception class
#       - refactor out to exist as module


class ArduinoAcquisition:
    """Arduino data logger for configurable data acquisition.

    Form a serial connection to pin A0 of Ardunio Uno (or equivalent) connected via
    a USB-USBC adapter.
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

    def setup(self) -> None:
        """Enable serial communication with Arduino by establishing connection to port
        at which it is connected."""
        # change state of setup variable
        self.is_setup = True

        # establish connection with Arduino (pin A0)
        try:
            self.arduino_conn = serial.Serial(
                "/dev/tty.usbmodem1301", baudrate=self.baud_rate, timeout=self.timeout
            )
        except:
            raise BaseException("Could not establish connection with Arduino.")

    def run(
        self, acq_period: float, dest_path: str, call_back: callable = None
    ) -> None:
        """Run acquisition

        Args:
            acq_period (float): Period of acquisition [secs].
            dest_path (str): Full path of CSV file to save data (excluding extension).
            call_back (callable): Optional callback function to be called each time
                new data is available (if provided).
        """
        if not self.is_setup:
            raise BaseException("Arduino has not been configured for acquisition.")

        with open(f"{dest_path}.csv", "w") as file:

            # CSV writer object
            writer = csv.writer(file, delimiter=",")

            # acquire data based on acquisition parameters
            start_time = time.time()
            the_time = start_time
            while time.time() - start_time < acq_period:

                # only acquire if data longer than sample rate
                if time.time() - the_time < 1 / self.fs:

                    # retrieve data from serial port
                    read_data = self.arduino_conn.readline().decode()

                    # remove return characters
                    read_data = read_data.strip("\r\n")

                    # if callback function supplied, call and pass data
                    if call_back is not None:
                        call_back(read_data)

                    # write to file (pass as list to avoid char separation)
                    writer.writerow([read_data])

                    # update time-keeping variable
                    the_time = time.time()

    def finish(self) -> None:
        """Close connection to Arduino."""
        # close serial connection
        self.arduino_conn.close()
