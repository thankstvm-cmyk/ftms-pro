"""
Central project path configuration for FTMS PRO.

This module defines filesystem paths relative to the project folder so the
application does not need hard-coded absolute paths such as ``D:\FTMS PRO``.

Existing modules have not been changed to use this file yet.
"""

from pathlib import Path


from pathlib import Path

# Root folder of the FTMS PRO project.
BASE_DIR = Path(__file__).resolve().parent

# Database
DATABASE_PATH = BASE_DIR / "ftms.db"

# Assets
IMAGE_DIR = BASE_DIR / "IMAGES"
LOGO_DIR = IMAGE_DIR

# Data folders
FTMS_DATA_DIR = BASE_DIR / "FTMS_DATA"
VEHICLE_DOCS_DIR = FTMS_DATA_DIR / "VEHICLE_DOCS"

# Utils
UTILS_DIR = BASE_DIR / "UTILS"
PHONE_UTILS_FILE = UTILS_DIR / "phone_utils.py"
EIDVALIDATOR_UTILS_FILE = UTILS_DIR / "eidvalidator_utils.py"

