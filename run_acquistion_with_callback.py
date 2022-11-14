from acquisition.arduino_acq_class import ArduinoAcquisition


def queue_placer():
    """
    Function which places
    """
    ...


if __name__ == "__main__":

    # acquisition parameters
    run_time = 5 * 60  # secs
    dest_dir = "/Users/pmccthy/Documents/EEG-from-scratch"
    dest_file = "test_file"
    dest_path = f"{dest_dir}/{dest_file}"

    # create acquisition object and set up
    acq = ArduinoAcquisition()
    acq.setup()

    # start acquisition
    acq.run(run_time, dest_path)

    # close connection with Arduino
    acq.finish()
