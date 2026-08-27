import win32com.client

manager = win32com.client.Dispatch("WIA.DeviceManager")

print("Available scanners:")
for i, device in enumerate(manager.DeviceInfos):
    print(f"{i}: {device.Properties("Name").Value}")

index = int(input("Select scanner number: "))

device = manager.DeviceInfos[index].Connect()

print("Connected successfully!")

print("\nDevice Items:")

for i, item in enumerate(device.Items):

    print(f"\nItem {i}")

    try:
        for prop in item.Properties:
            try:
                print(f"{prop.Name} = {prop.Value}")
            except Exception:
                pass
    except Exception as e:
        print(e)
