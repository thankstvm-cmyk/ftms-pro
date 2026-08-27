import win32com.client
import win32com.client
import os
import tempfile
from datetime import datetime

class ScannerEngine:

    def __init__(self):
        self.device_manager = win32com.client.Dispatch("WIA.DeviceManager")
        self.scanners = []
        self.connected_device = None

    def detect_scanners(self):

        self.scanners = []

        for device in self.device_manager.DeviceInfos:

            name = device.Properties("Name").Value

            self.scanners.append(name)

        return self.scanners


    def connect_scanner(self, scanner_name):

        for device in self.device_manager.DeviceInfos:

            name = device.Properties("Name").Value

            if name == scanner_name:

                self.connected_device = device.Connect()

                return True

        return False

    # ← ADD THE NEW METHOD HERE

    def scan_page(self, scanner_name, settings): 

        try:
            print("1. Connecting scanner...")
            if not self.connect_scanner(scanner_name):
                print("Connection failed.")
                return None

            print("2. Applying settings...")
            self.apply_scanner_settings(settings)

            print("3. Connected Device:", self.connected_device)

            item = self.connected_device.Items[1]
            print("4. Got scanner item.")

            print("5. Starting Transfer...")
            image = item.Transfer()
            print("6. Transfer Successful.")

            # User selected output type
            output_type = settings["output_type"].strip().lower()

            # WIA cannot save directly as PDF
            if output_type == "pdf":
                extension = ".bmp"        # Internal working file only
            elif output_type in ("jpg", "jpeg"):
                extension = ".jpg"
            elif output_type == "png":
                extension = ".png"
            elif output_type == "tif":
                extension = ".tif"
            elif output_type == "tiff":
                extension = ".tiff"
            elif output_type == "bmp":
                extension = ".bmp"
            else:
                extension = ".bmp"

            # Unique filename
            filename = f"GraceScan_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}{extension}"
            temp_file = os.path.join(tempfile.gettempdir(), filename)

            print("7. Saving File...")
            image.SaveFile(temp_file)

            print("8. File Saved:", temp_file)

            return temp_file

        except Exception as e:
            print("SCAN ERROR:", e)
            return None

    def apply_scanner_settings(self, settings):
   
        scan_source   = settings["scan_source"]
        dpi           = settings["dpi"]
        colour        = settings["colour"]
        output_type   = settings["output_type"]
        document_size = settings["document_size"]
        scan_type     = settings["scan_type"] 
        print("===== Scanner Settings =====")
        print("Source :", scan_source)
        print("DPI :", dpi)
        print("Colour :", colour)
        print("Output :", output_type)
        print("Document Size :", document_size)
        print("Scan Type :", scan_type)
        print("============================")
        
        # GET SCANNER ITEM
        item = self.connected_device.Items[1]
        #DISPLAY ALL AVAILBLE SCANNER PROPERTIES 
        print("\n ====AVAILABLE WIA PROPERTIES====")
        for prop in item.Properties:
            try:
                print(prop.PropertyID, "-", prop,__name__, "=", prop.Value)
            except:
                pass
            print("=========================================\n")

        return True
