import win32com.client
import os
import tempfile

# WIA image format GUID for BMP
WIA_FORMAT_BMP = "{B96B3CAB-0728-11D3-9D7B-0000F81EF32E}"

manager = win32com.client.Dispatch("WIA.DeviceManager")

print("Available scanners:")
for i, device in enumerate(manager.DeviceInfos):
    print(f"{i}: {device.Properties('Name').Value}")

index = int(input("Select scanner number: "))

device = manager.DeviceInfos[index].Connect()

print("Connected.")

item = device.Items[1]

print("Place a document on the scanner...")
input("Press ENTER to start scanning...")

image = item.Transfer(WIA_FORMAT_BMP)

filename = os.path.join(tempfile.gettempdir(), "GraceScan_Test.bmp")

image.SaveFile(filename)

print()
print("SUCCESS!")
print("Image saved to:")
print(filename)
