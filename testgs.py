try:
    import twain
    print("TWAIN : OK")
except Exception as e:
    print("TWAIN :", e)

try:
    import win32com.client
    print("WIA (pywin32) : OK")
except Exception as e:
    print("WIA  :", e)
    
try:
    from PIL import Image
    print("Pillow : OK")
except Exception as e:
    print("Pillow  :", e)
    
try:
    import reportlab
    print("Report Lab : OK")
except Exception as e:
    print(" ReportLab  :", e)
print("\n GraceScan Environment Ready")