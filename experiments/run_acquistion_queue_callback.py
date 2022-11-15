"""
A script to run a basic acquisition using the Arduino, with a callback 
function to place data on a queue.
Author: Patrick McCarthy
"""
# Python standard library imports
from multiprocessing import Queue

# third-part library imports
import numpy as np

# acquisition library imports
from arduino_eeg.acquisition import ArduinoAcquisition


def queue_placer(data: np.ndarray, queue: Queue):
    """
    Function which places data on queue each time it is called.

    Args:
        data (np.ndarray):
        queue (Queue): Queue to place data on.

    """
    queue.put(data)


if __name__ == "__main__":

    # callback parameters
    queue = Queue(...)
    queue_placer_args = {}
    queue_placer_args["queue"] = queue

    # acquisition parameters
    run_time = 5 * 60  # secs
    dest_dir = "/Users/pmccthy/Documents/EEG-from-scratch"
    dest_file = "test_file"
    dest_path = f"{dest_dir}/{dest_file}"

    # create acquisition object and set up
    acq = ArduinoAcquisition()
    acq.setup()

    # start acquisition
    acq.run(run_time, dest_path, call_back=queue_placer_args)

    # close connection with Arduino
    acq.finish()
