"""
A script defining a simple repetitive auditory stimulus experiment.
Author: Patrick McCarthy
"""
# Python standard library imports
from multiprocessing import Process
import json
import os

# third-party library imports
import numpy as np
import matplotlib.pyplot as plt
from scipy.io import wavfile
from playsound import playsound

# Arduino EEG imports 
from arduino_eeg.acquisition import ArduinoAcquisition


# configuarable parameters
fs = 10e3                   # sampling frequency of waveform [Hz]
f_sound = 1000              # frequency of sound [Hz]
stim_block_period = 1       # length of period in which stimulus will be played [s]
pause_block_period = 1      # length of pause period [s]
stim_period = 0.5           # length of stimulus [s]
num_stim = 10               # number of stimuli to be played
init_pause_period = 1     # length of initial pause period [s]
randomise_time = True       # flag specifying whether to randomise stimulus onset times within stimulus blocks
plot_waveform = True        # flag specifying whether to save 

# directory to save data
save_dir = "/Users/pmccthy/Documents/EEG-from-scratch/data/aud_stim_test"

if __name__ == "__main__":

    # create directory if it does not exist
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    # compute additional parameters
    # total experiment duration
    total_period = init_pause_period + num_stim * (stim_block_period + pause_block_period)
    # generate stimulus onset times (within periods)
    if randomise_time:
        rel_onsets = np.random.uniform(
            low=0, high=stim_block_period - stim_period, size=(num_stim,)
        )
    else:
        rel_onsets = np.zeros((num_stim,))

    # generate sound waveform
    sound = np.empty(int(total_period * fs))
    sound[: int(init_pause_period * fs)] = np.zeros(int(init_pause_period * fs))
    for period_idx in range(num_stim):

        # compute indices delimiting stimulus and pause periods
        stim_block_period_start_idx = int(
            (init_pause_period + (period_idx * (stim_block_period + pause_block_period))) * fs
        )
        stim_block_period_end_idx = int(
            (
                init_pause_period
                + (period_idx * (stim_block_period + pause_block_period))
                + stim_block_period
            )
            * fs
        )
        pause_block_period_start_idx = int(
            (
                init_pause_period
                + (period_idx * (stim_block_period + pause_block_period))
                + stim_block_period
            )
            * fs
        )
        pause_block_period_end_idx = int(
            (
                init_pause_period
                + (period_idx * (stim_block_period + pause_block_period))
                + stim_block_period
                + pause_block_period
            )
            * fs
        )

        # generate pause block signal
        pause_block = np.zeros(int(pause_block_period * fs))

        # generate stimulus block signal
        stim_block = np.zeros(int(stim_block_period * fs))
        stim_time_ax = np.arange(stim_period * fs) / fs
        stim = np.sin(2 * np.pi * f_sound * stim_time_ax)
        stim_block[
            int(rel_onsets[period_idx] * fs) : int(
                (rel_onsets[period_idx] + stim_period) * fs
            )
        ] = stim

        # fill array with stimulus and pause signals
        sound[stim_block_period_start_idx:stim_block_period_end_idx] = stim_block
        sound[pause_block_period_start_idx:pause_block_period_end_idx] = pause_block

    # save parameters
    params = {
        "fs": fs,
        "f_sound": f_sound,
        "stim_block_period": stim_block_period,
        "pause_block_period": pause_block_period,
        "stim_period": stim_period,
        "num_stim": num_stim,
        "init_pause_period": init_pause_period,
        "randomise_time": randomise_time,
    }
    with open(f"{save_dir}/params.json", "w+") as f:
        json.dump(params, f)

    # save stimulus times
    stim_onset_times = []
    for period_idx in range(num_stim):
        stim_onset_time = (
            init_pause_period
            + (period_idx * (stim_block_period + pause_block_period))
            + rel_onsets[period_idx]
        )
        stim_onset_times.append(stim_onset_time)

    # save sound waveform as CSV and wav
    np.savetxt(f"{save_dir}/sound.csv", sound)
    wavfile.write(f"{save_dir}/sound.wav", rate=int(fs), data=sound)

    # plot waveform if specified
    time_ax = np.arange(len(sound)) / fs
    fig = plt.figure()
    plt.plot(time_ax, sound)
    plt.xlabel("time (s)")
    fig.patch.set_facecolor("w")
    fig.savefig(f"{save_dir}/stim.png", dpi=100)

    # create acquisition object and set up
    acq = ArduinoAcquisition()
    acq.setup()

    # create process for acquisition
    acq_process = Process(target=acq.run, args=(total_period, save_dir))

    # create process for sound
    sound_process = Process(target=playsound, args=(f"{save_dir}/sound.wav"))

    # start acquisition
    acq.run(run_time=total_period, dest_path=save_dir)

    # start playing sound and acquisition
    print("Starting experiment.")
    acq_process.start()
    acq_process.join()
    sound_process.start()
    sound_process.join()
    print("Experiment ended.")

    # close connection with Arduino
    acq.finish()