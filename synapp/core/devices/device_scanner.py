from typing import List
from synapp.core.devices.device import Device, MuseDevice
import pygatt
import muselsl
from synapp.core.logging import logger
from synapp.core.enums import DeviceType


class NoDevicesFoundError(Exception):
    """Scan was successful, but no devices were found."""

    pass


class ScanFailedException(Exception):
    """General exception for a device scan failing - could not communicate in expected manner."""

    pass


class DeviceScanner:
    def scan_for_devices(self) -> List[Device]:
        pass


class DeviceScannerFactory:
    @staticmethod
    def create(device_type: str) -> DeviceScanner:
        if device_type == DeviceType.muse:
            return MuseDeviceScanner()
        elif device_type == DeviceType.ganglion:
            return GanglionDeviceScanner()


class MuseDeviceScanner(DeviceScanner):
    def scan_for_devices(self) -> List[Device]:
        try:
            muses = muselsl.list_muses() or []
        except Exception as e:
            # Do popup that says no BLED112 connected
            logger.error(e, exc_info=1)
            muses = []

        devices = []

        for muse in muses:
            devices.append(MuseDevice(muse["name"], muse["address"]))

        return devices


class GanglionDeviceScanner(DeviceScanner):
    def scan_for_devices(self) -> List[Device]:
        ...
