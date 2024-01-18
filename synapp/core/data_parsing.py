#!/usr/bin/env python

import numpy as np

DEFAULT_NUM_SAMPLES = 128
DEFAULT_NUM_TILES = 5


def get_data_window_after_time(time, timestamps, samples, num_samples=DEFAULT_NUM_SAMPLES):
    """ Numpy utility to gets num_samples samples from all channels after the input time"""
    start_indices = np.searchsorted(
        timestamps,
        time,
        side="right",
    )  # finds the index of the nearest timestamp value above time
    data_window = None

    if isinstance(start_indices, np.ndarray):
        start_index = start_indices[0]
    elif start_indices is not None and start_indices >= 0:
        start_index = start_indices
    else:
        return None
    end_index = start_index + num_samples
    try:
        data_window = samples[:, start_index:end_index]
    except IndexError:
        print("Out of bounds in get_data_window_after_time: not enough data after time " + str(time))

    return data_window, start_index


# Gets num_samples samples from all channels after timestep
def get_data_window_after_index(index, samples, num_samples=DEFAULT_NUM_SAMPLES):
    end_index = index + num_samples
    try:
        data_window = samples[:, index:end_index]
    except IndexError:
        data_window = None
        print("Out of bounds in getdata_windowafterindex: not enough data after index " + str(index))

    return data_window


# Takes a window of data and tiles it, for filtering (if a window is [0, 3, 1] it will become [0, 3, 1, 0, 3, 1, 0, 3, 1] if numtiles is 3)
def tile_window(window, numtiles=DEFAULT_NUM_TILES):
    return np.tile(window, numtiles)


# Input: Set of markers and timestamps, as well as the data samples
# Output: 3d array of (trials, channels, samples) where the trials index is the same index as the marker. can directly use as X_train (or X_test)
# (so markers[5] will correspond to the chunk of data at output[5], which will be the window of data over all channels, num_samples after the marker occurs
def get_ML_set_from_data(markers, timestamps, samples, samples_per_trial=DEFAULT_NUM_SAMPLES):
    X_outputshape = (markers.shape[0], samples.shape[0], samples_per_trial)
    X_output = np.zeros(X_outputshape)
    Y_output = markers[:]["marker"]

    for i in range(0, markers.shape[0]):
        print(markers[i]["timestamp"])
        samplewindow, s_index = get_data_window_after_time(
            markers[i]["timestamp"], timestamps, samples, samples_per_trial
        )
        print(np.shape(samplewindow))
        # indicestoremove = []
        if samplewindow is None:
            print(
                "Attempt to get data from marker {0} at timestamp {1} failed.".format(
                    markers[i, "marker"], markers[i, "timestamp"]
                )
            )
        else:
            X_output[i] = samplewindow

    return X_output, Y_output



def untile_window(tiled_window, original_size, num_tiles=DEFAULT_NUM_TILES):
    """ Take a window of data that has been tiled and take the center to return it
        to the same size as original data with no repetition.
        This undoes windowing needed to have enough data to successfully bandpass filter.
    """
    start_index = original_size * (num_tiles // 2)
    end_index = start_index + original_size
    return tiled_window[start_index:end_index]


def get_FFT_from_timeseries(data, sample_rate=256):
    """ From a single time-series array, get the amplitudes and frequencies from performing an FFT. """
    data = np.asarray(data)
    fft_array = np.fft.fft(data / len(data))  # Gives complex numbers, including imaginary "phase" component
    amplitude_array = abs(
        fft_array
    )  # Abs of complex number is amplitude component, gives two-sided frequency array of positive values
    amplitude_array_range = np.arange(len(amplitude_array))  # make array from 0 to length of data
    epoch_number = len(fft_array) / sample_rate  # divide each value by how many seconds of data
    total_frequency = amplitude_array_range / epoch_number  # both-sided frequency range
    positive_frequency = total_frequency[range(int(len(amplitude_array) / 2))]  # one side frequency range of frequency
    positive_amplitudes = amplitude_array[range(int(len(amplitude_array) / 2))]  # one side array of hz power values

    return positive_amplitudes, positive_frequency


def ssvep_eval(samples, possible_freqs, sample_rate=256):
    """ Basic heuristic estimate which SSVEP frequency is most likely from the provided data. """
    amplitudes, frequencies = get_FFT_from_timeseries(samples, sampleRate=sample_rate)
    closest_indices = []
    for freq in possible_freqs:
        closest_indices.append(nearest_index(freq, frequencies))
    ssvep_amplitudes = amplitudes[closest_indices]
    max_ssvep = np.argmax(ssvep_amplitudes)
    predicted_freq = possible_freqs[max_ssvep]
    return predicted_freq


def nearest_index(value, array):
    """ Numpy helper to get the closest index of a value in the array. """
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return idx


def slide_window(old_samples, new_samples):
    """ Appends new samples on the end of old_samples and slides the same amount off.
    if you have [0, 3, 6, 1, 5] and new_samples is [2, 9], output will be [6, 1, 5, 2, 9]
    data should be of shape (channels, samples]
    """
    output_samples = None
    window_length = np.shape(old_samples)[1]
    new_samples_length = np.shape(new_samples)[1]
    if new_samples_length <= window_length:
        output_samples = np.zeros(shape=(np.shape(old_samples)))
        new_start_index = window_length - new_samples_length
        output_samples[:, 0:new_start_index] = old_samples[:, new_samples_length:]
        output_samples[:, new_start_index:] = new_samples
    output_samples = new_samples[:, new_samples_length-window_length:]
    return output_samples


def get_markers_between_timestamps(start, end, markers):
    """ Returns an np array of markers objects which fall between the start and end timestamps """
    markers_timestamps = []
    markers_corresponding_strings = []
    if end >= start:
        for markerobj in markers:
            if start <= markerobj["timestamp"] < end:
                markers_timestamps.append(markerobj["timestamp"])
                markers_corresponding_strings.append(markerobj["marker"])
                print(markers_corresponding_strings)

    return np.asarray(markers_timestamps), np.asarray(markers_corresponding_strings)
