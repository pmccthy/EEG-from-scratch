"""
A script to acquire data from pin A0 of Ardunio connected through
USB-USBC adapter.
Author: Patrick McCarthy 
 """
import serial
import time
import csv
import numpy as np

# acquisition parameters
fs = 500
acq_period = 2
acq_name = "test"
dest_dir = "/Users/pmccthy/Documents/EEG-from-scratch/data"

# serial connection parameters
timeout = 10
baud_rate = 9600

if __name__ == "__main__":

    # establish connection with Arduino (pin A0)
    arduino_conn = serial.Serial("/dev/tty.usbmodem1301", baud_rate, timeout=timeout)

    # enable I/O to destinatiin file
    with open(f"{dest_dir}/{acq_name}.csv", "w") as file:

        # CSV writer object
        writer = csv.writer(file, delimiter=",")

        # acquire data based on acquisition parameters
        start_time = time.time()
        the_time = start_time
        while time.time() - start_time < acq_period:

            # only acquire if data longer than sample rate
            if time.time() - the_time < 1 / fs:

                # retrieve data from serial port
                read_data = arduino_conn.readline().decode()

                # remove return characters
                read_data = read_data.strip("\r\n")

                # write to file (pass as list to avoid char separation)
                writer.writerow([read_data])

                # # print data
                # print(read_data)

                # update time-keeping variable
                the_time = time.time()

        # close serial connection
        arduino_conn.close()
