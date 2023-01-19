"""
A script to run a basic acquisition using the Arduino.
Author: Patrick McCarthy
"""

from arduino_eeg.acquisition import ArduinoAcquisition

if __name__ == "__main__":

    # acquisition parameters
    run_time = 30  # secs
    dest_dir = "/Users/pmccthy/Documents/EEG-from-scratch/data"
    dest_file = "neurosky_test_1"
    dest_path = f"{dest_dir}/{dest_file}"

    # create acquisition object and set up
    acq = ArduinoAcquisition()
    acq.setup()

    # start acquisition
    acq.run(run_time, dest_path)

    # close connection with Arduino
    acq.finish()
