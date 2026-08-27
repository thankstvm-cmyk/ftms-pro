import win32com.client


class ScannerEngine:

    def __init__(self):
        self.device_manager = None
        self.scanners = []

    def detect_scanners(self):

        self.scanners = []

        self.device_manager = win32com.client.Dispatch(
            "WIA.DeviceManager"
        )

        for device in self.device_manager.DeviceInfos:

            name = device.Properties("Name").Value

            self.scanners.append(name)

        return self.scanners
