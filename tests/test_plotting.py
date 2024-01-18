#!/bin/python3
# Test file for the bci_plotting utility file

import unittest

import matplotlib as plt
import numpy as np

from synapp.core import plotting
from tests import test_utils

class TestPlotting(unittest.TestCase):

    def test_playback(self):
        timestamps, samples, markers = test_utils.create_timestamps_samples_markers_arrays(5000, 4, 2)
        print(markers)
        plotting.playback_data(timestamps, samples, markers, 100, playback_speed=10, step_size=5, num_channels=4, fourier_channel=1)

    def test_playback_data_default_args(self):
        # Test playback_data() with default arguments
        timestamps = np.arange(0, 100, 0.1)
        samples = np.random.rand(5, 1000)
        markers = [("marker 1", 10), ("marker 2", 20), ("marker 3", 30)]
        display_window_length = 100
        
        plotting.playback_data(timestamps, samples, markers, display_window_length)
        
        # Verify that the plot has the expected number of channels
        assert len(plt.gcf().axes) == 6
        
        # Verify that the plot has the expected number of markers
        assert len(plt.gcf().axes[0].get_xticklabels()) == 4

    def test_playback_data_custom_args(self):
        # Test playback_data() with custom arguments
        timestamps = np.arange(0, 50, 0.1)
        samples = np.random.rand(5, 500)
        markers = [("marker 1", 5), ("marker 2", 10), ("marker 3", 15)]
        display_window_length = 50
        playback_speed = 2
        step_size = 5
        num_channels = 3
        fourier_channel = 1
        
        plotting.playback_data(timestamps, samples, markers, display_window_length, playback_speed, step_size, num_channels, fourier_channel)
        
        # Verify that the plot has the expected number of channels
        assert len(plt.gcf().axes) == 4
        
        # Verify that the plot has the expected number of markers
        assert len(plt.gcf().axes[0].get_xticklabels()) == 4


if __name__ == '__main__':
    unittest.main()
