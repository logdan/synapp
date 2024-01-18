import asyncio
import os
import pickle
import threading
from abc import ABCMeta
from dataclasses import dataclass
from time import time
from typing import Callable, Dict, List

import pandas as pd
from muselsl.muse import Muse
from yaml import safe_dump

from synapp.core.utilities import get_time_string
from synapp.core.logging import logger

from synapp.misc.tqdm_provider import tqdm


class DeviceStreamer(metaclass=ABCMeta):
    def __init__(self):
        pass

    def stream(self):
        pass


class Device:
    def __init__(
        self,
        name: str,
        sampling_rate: int,
        channel_count_list: List[int],
    ):
        self.name = name
        self.sampling_rate = sampling_rate
        self.channel_count_list = channel_count_list

    def stream(self, block=False, callback: Callable = None):
        pass

    def record(self, folder, recording_time, block=False, notes=None):
        pass

    def folder_label(self, time_string):
        return f"{time_string or get_time_string()}_{self._simplify_name()}"

    def _simplify_name(self):
        return self.name.lower().replace(" ", "_")

    def save(self, folder) -> str:
        file_path = os.path.join(folder, self.name.lower().replace(" ", "_") + ".pkl")
        with open(file_path, "wb") as f:
            pickle.dump(self, f)
        return file_path

    @staticmethod
    def load(file_path):
        with open(file_path, "rb") as f:
            device = pickle.load(f)
            if not isinstance(device, Device):
                raise TypeError(f"Deserialized object not a Device : {device}")
            return device


class MuseDevice(Device):
    def __init__(self, name, mac_address):
        super().__init__(name, sampling_rate=256, channel_count_list=[4, 5])
        self.mac_address = mac_address

    def record(self, folder, recording_time, block=True, notes=None) -> str:
        """Record from the device for a set amount of time.

        Arguments:
            folder {str} -- File path of the folder to store the recording in.
                            A subdirectory will be created.
            recording_time {float} (sec) -- Number of seconds to record for

        Keyword Arguments:
            block {bool} -- Whether the script should wait for the recording to finish to continue (default: {True})
            notes {str} -- Notes to store with the recording (default: {None})

        Returns:
            str -- Directory that the data was stored in.
        """
        streamer = MuseStreamer()
        return streamer.record(self, folder, recording_time, block=block, notes=notes)

    def __str__(self):
        return f"Device: {self.name}, Mac Address: {self.mac_address}, Sampling Rate (Hz): {self.sampling_rate}"


class MuseStreamer:
    def __init__(self):
        self.cancel_recording_event = threading.Event()
        self.muse = None

    def stream(self, muse: MuseDevice, callback: Callable, block=False):
        self.muse = Muse(address=muse.mac_address, callback_eeg=callback, name=muse.name)
        self.muse.connect()
        self.muse.start()

    def record(
        self,
        device: MuseDevice,
        folder: str,
        recording_time: float = None,
        chunk_duration=None,
        block=False,
        notes: str = None,
    ) -> str:
        self.cancel_recording_event.clear()
        self.accumulated_data = []
        self.accumulated_timestamps = []

        def process_sample(samples, times):
            """This function is called by the Muse driver when it processes device input."""
            for ii in range(12):
                self.accumulated_data.append(samples[:, ii])
                self.accumulated_timestamps.append(times[ii])

        # Make a directory for the recordings to go into
        start_timestring = get_time_string()
        current_recording_folder = os.path.join(folder, device.folder_label(start_timestring))
        os.makedirs(current_recording_folder, exist_ok=False)
        # Write some information about the recording to file
        recording_info: dict = {
            "device": device.name,
            "recording_started": start_timestring,
            "notes": notes,
        }

        with open(os.path.join(current_recording_folder, "recording_info.yaml"), "w") as f:
            safe_dump(recording_info, f)

        self.muse = Muse(address=device.mac_address, callback_eeg=process_sample, name=device.name)
        self.muse.connect()
        self.muse.start()
        start = time()
        elapsed = 0.0
        last_num_samples = 0
        logger.info("Recording started")

        with tqdm(total=recording_time, unit="s") as progress_bar:
            while elapsed < recording_time and not self.cancel_recording_event.is_set():
                _wait(asyncio.sleep(1))
                elapsed = time() - start
                num_samples = len(self.accumulated_timestamps)
                samples_sec = num_samples - last_num_samples
                last_num_samples = num_samples
                # Progress bar management
                progress_bar.update(1)
                progress_bar.set_postfix(samples_recorded_sec=f"{samples_sec}", refresh=True)

        logger.info("Closing recording")

        self.muse.stop()
        self.muse.disconnect()
        self.muse = None

        timestamps = self.accumulated_timestamps
        eeg_samples = self.accumulated_data
        recording = pd.DataFrame(data=eeg_samples, columns=["TP9", "AF7", "AF8", "TP10", "Right AUX"])
        recording["timestamps"] = timestamps
        recording.set_index("timestamps", drop=True, inplace=True)

        # TODO: apply configuration to remove/add Right AUX channel
        recording.drop(["Right AUX"], axis=1, inplace=True)

        recording.to_pickle(os.path.join(current_recording_folder, "data.pkl"))

        recording_info.update(
            {
                "duration (s)": elapsed,
                "num_samples": len(recording),
                "sample_rate": device.sampling_rate,
            }
        )

        with open(os.path.join(current_recording_folder, "recording_info.yaml"), "w") as f:
            safe_dump(recording_info, f)

        logger.info(f"Recording data and metadata saved to {current_recording_folder}")

        return current_recording_folder

    def stop_recording(self):
        """If a recording is active, stop it normally. Await the result of the recording process"""
        self.cancel_recording_event.set()

    def stop_streaming(self):
        if self.muse:
            self.muse.stop()
            self.muse.disconnect()
        self.muse = None


def _wait(coroutine):
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(coroutine)


class DeviceConfiguration:
    def __init__(self, num_active_channels: int, electrode_map: Dict[str, str]):
        self.num_active_channels = num_active_channels
        self.electrode_map = electrode_map

    def is_compatible_with_device(self, device: Device) -> bool:
        return self.num_active_channels in device.channel_count_list


class DefaultConfigurations:
    muse = DeviceConfiguration(4, {0: "TP9", 1: "AF7", 2: "AF8", 3: "TP10"})


@dataclass
class RecordingSettings:
    record_duration: float  # sec
    recording_rotation_duration: float  # sec
