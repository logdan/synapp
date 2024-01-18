#!/usr/bin/env python

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from synapp.core import data_parsing as data_parsing
from synapp.core.data_parsing import get_FFT_from_timeseries

DEFAULT_PLAYBACK_SPEED = 1.0
DEFAULT_STEP_SIZE = 64
DEFAULT_SAMPLE_RATE = 2


def playback_data(
    timestamps,
    samples,
    markers,
    display_window_length,
    playback_speed=DEFAULT_PLAYBACK_SPEED,
    step_size=DEFAULT_STEP_SIZE,
    num_channels=5,
    fourier_channel=5,
):
    curr_start = 0
    curr_end = display_window_length
    display_timestamps = timestamps[curr_start:curr_end]
    display_samples = samples[:, curr_start:curr_end]

    display_amp, display_freq = data_parsing.get_FFT_from_timeseries(display_samples, DEFAULT_SAMPLE_RATE)

    fig = plt.figure(constrained_layout=True)
    gs = fig.add_gridspec(5, 2)
    axes = []
    for i in range(0, num_channels):
        axes.append(fig.add_subplot(gs[i, 0]))
    fourier_ax = fig.add_subplot(gs[:, 1])

    fig.suptitle("Playback")

    fourierticks = np.asarray([0, 5, 10, 12, 15, 20, 25, 30, 35, 40])

    for i in range(0, num_channels):
        axes[i].plot(display_timestamps, display_samples[i, :], color="blue", linewidth=0.25)
    fourier_ax.set_xlim([0.2, 40])
    fourier_ax.set_ylim([0, 10])
    fourier_ax.plot(display_freq, display_amp, color="green", linewidth=0.25)

    plt.pause(0.1)

    while curr_end + step_size <= np.shape(timestamps)[0]:
        curr_start += step_size
        curr_end += step_size

        display_timestamps = timestamps[curr_start:curr_end]
        display_samples = samples[:, curr_start:curr_end]

        display_amp, display_freq = data_parsing.get_FFT_from_timeseries(display_samples[fourier_channel - 1], 256)

        fourier_ax.cla()

        fourier_ax.set_xlim([1, 40])
        fourier_ax.set_ylim([0, 10])
        fourier_ax.set_xticks(fourierticks)

        display_marker_timestamps, display_marker_strings = data_parsing.get_markers_between_timestamps(
            display_timestamps[0],
            display_timestamps[-1],
            markers,
        )

        for i in range(0, num_channels):
            axes[i].cla()
            axes[i].grid()
            axes[i].plot(display_timestamps, display_samples[i, :], color="blue", linewidth=0.25)
            plot_vertical_markers(axis=axes[0], markers=display_marker_timestamps, strings=display_marker_strings)
        fourier_ax.plot(display_freq, display_amp, color="green", linewidth=0.33)

        fig.canvas.draw()

        plt.pause(1 / playback_speed)

    plt.show()


def plot_vertical_markers(axis, markers, strings):
    if markers.size != 0:
        axis.vlines(markers, -1, 1, linestyles="-", label=strings[0])


def plot_timeseries_dataframe(dataframe: pd.DataFrame, sample_rate, plot_fft=True, title="", show=True):
    """Plot a dataframe representing an EEG recording

    Arguments:
        dataframe {pd.DataFrame} -- Time-series dataframe with

    Keyword Arguments:
        plot_fft {bool} -- Whether to also show Fourier Transform plots (default: {True})
        title {str} -- Title of the entire figure (default: {""})
        show {bool} -- Whether to automatically call `plt.show()` (default: {True})
    """
    fig, axs = plt.subplots(len(dataframe.keys()), 2 if plot_fft else 1, figsize=(10, 15), sharex="col")

    normalized_time = dataframe.index - dataframe.index[0]

    fig.suptitle(title)

    cmap = plt.get_cmap("viridis", len(dataframe.keys()))

    for i, (col_name, column) in enumerate(dataframe.items()):
        # Plot the time series dataframe
        ax = axs[i] if not plot_fft else axs[i, 0]
        ax.plot(normalized_time, column, color=cmap(i))
        ax.set_ylabel(f"{col_name}\nAmplitude (mv)")
        ax.spines["right"].set_visible(False)
        ax.spines["top"].set_visible(False)
        ax.spines["left"].set_visible(True)
        ax.yaxis.set_ticks_position("left")

        if i == 0:
            ax.set_title("Time-Series Voltage")

        if i == len(dataframe.keys()) - 1:
            ax.set_xlabel("Time (sec)")
        else:
            ax.spines["bottom"].set_visible(False)

        if plot_fft:
            # Compute and plot the Fourier Transform
            amplitudes, frequency = get_FFT_from_timeseries(column, 256)
            ax = axs[i, 1]
            ax.plot(frequency, amplitudes)
            ax.set_xlim(-0.1, 65)

            if i == 0:
                ax.set_title("FFT")

            ax.set_xlabel("Frequency (Hz)")
            ax.set_ylabel(f"{col_name}\nMagnitude")

    # Adjust layout to prevent overlap
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])  # Adjust the rect parameter as needed
    plt.subplots_adjust(hspace=0.1)  # Reduce the space between subplots

    if show:
        plt.show()
