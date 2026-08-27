from scanner_engine import ScannerEngine

engine = ScannerEngine()

scanners = engine.detect_scanners()

print("Scanners:", scanners)

filename = engine.scan_page("HP904D03 (HP Smart Tank 530 series)")

print("Returned:", filename)
