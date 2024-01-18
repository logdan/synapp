#!/usr/bin/env python3
""" Scan for available EEG devices. Save devices to configuration file when they are detected. """

import argparse
import os

from synapp.core.enums import DeviceType
from synapp.core.logging import logger
from synapp.core.devices.device_scanner import DeviceScannerFactory


def scan_for_devices(destination=None, interactive_prompt=False):
    logger.info("Scanning devices")
    device_type = DeviceType.muse
    devices = DeviceScannerFactory.create(device_type).scan_for_devices()
    if devices:
        logger.info(f"Found devices: {devices}")
    else:
        logger.warning("No devices found.")

    # Serialize the Device objects to files
    if destination is not None:
        for device in devices:
            if interactive_prompt:
                should_save_device = input(
                    f"Would you like to save {device} to file?" + " (yes/no): "
                ).strip().lower() in [
                    "yes",
                    "y",
                ]
            else:
                should_save_device = True

            if should_save_device:
                file_path = device.save(destination)
                logger.info(f"Device '{device.name}' information saved to {file_path}")


parser = argparse.ArgumentParser(description="Scan for available devices. Interactive mode optional.")

parser.add_argument(
    "--confirm-interactively",
    action="store_true",
    default=False,
    help="Enable interactive confirmation. If false, automatically save all devices",
)

parser.add_argument(
    "--save-dir", nargs="?", type=str, default=None, help="An optional directory in which to save the scanned devices."
)

if __name__ == "__main__":
    args = parser.parse_args()
    if args.save_dir:
        resolved_path = os.path.abspath(os.path.expanduser(args.save_dir))
    else:
        resolved_path = None
    scan_for_devices(resolved_path, args.confirm_interactively)
