#!/bin/python3
# Utility file for use in testing this library.
# Data and object generation

import unittest
import numpy as np

def create_timestamps_samples_markers_arrays(desired_num_samples, num_channels, hz, generator_function = None) -> tuple[np.ndarray, np.ndarray, np.recarray]:
    if not generator_function:
        def generator_function(length):
            return np.sin(np.arange(length))
    
    samples = []

    for _ in range(num_channels):
        samples.append(generator_function(desired_num_samples))
    
    samples = np.asarray(samples)

    timestamps = np.arange(0, desired_num_samples/hz, 1/hz)

    markers = np.core.records.fromarrays([np.array(['one', 'two']), [timestamps[int(np.floor(len(timestamps)/3))], timestamps[int(np.floor(len(timestamps)/2))]]], dtype=np.dtype([('marker', '<U3'), ('timestamp', np.float64)]))
    
    return timestamps, samples, markers


# Test the utility functions -- we need to know they work as expected

class TestUtils(unittest.TestCase):
    def test_create_timestamps_samples_markers_arrays(self):
        timestamps, samples, markers = create_timestamps_samples_markers_arrays(5000, 4, 2)

        self.assertEqual(np.shape(timestamps)[0], 5000)
        self.assertTupleEqual(np.shape(samples), (4, 5000))

        self.assertTrue("one" in markers['marker'])
        self.assertFalse("abcdef" in markers['marker'])

    
    
if __name__ == '__main__':
    unittest.main()
