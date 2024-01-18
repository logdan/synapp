#!/usr/bin/env python

# from synapp.Devices import Device

from time import time, sleep
import argparse
from threading import Event
from synapp.core.devices.device import Device, MuseStreamer
from synapp.core.devices.device_scanner import DeviceScannerFactory
from synapp.core.enums import DeviceType
from synapp.core.logging import logger


def record_for_time(save_dir, timeout=60, device=None):
    if not device:
        logger.info("Scanning devices")
        device_type = DeviceType.muse
        devices = DeviceScannerFactory.create(device_type).scan_for_devices()
        if devices:
            device = devices[0]
        else:
            logger.warning("No devices found while scanning")
            return
    else:
        device = Device.load(device)

    logger.info(f"Beginning recording from {device}...")
    recording_info = device.record(save_dir, recording_time=timeout, block=True, notes='testing')        
    
    logger.info(f"Recording completed. Elapsed: {recording_info}")


parser = argparse.ArgumentParser(description="Scan for available devices. Interactive mode optional.")

parser.add_argument(
    "--load-device-info",
    type=str,
    default=None,
    help=".pkl file to load device info from. Otherwise, will scan and select first device.",
)

parser.add_argument(
    "--save-dir",
    nargs="?",
    type=str,
    default=None,
    help="Where to save the recorded data. A subdirectory will be made.",
)

if __name__ == "__main__":
    args = parser.parse_args()
    device_pkl = args.load_device_info
    save_dir = args.save_dir
    record_for_time(save_dir, timeout=60, device=device_pkl)
