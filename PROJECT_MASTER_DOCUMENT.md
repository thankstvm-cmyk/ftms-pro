# FTMS PRO - Project Master Document

Generated: 2026-07-01  
Workspace: `D:\FTMS PRO`  
Entry point: `ftms_pro.py`

## 1. Project Overview

FTMS PRO is a Python desktop fleet management system built mainly with Tkinter, SQLite, Pillow, pandas, ReportLab, openpyxl, tkcalendar, and Windows scanner support through pywin32. The current active workflow focuses on vehicle records, vehicle document images, insurance entry, commercial vehicle editing, reports, and PDF export.

The project currently contains active production-style modules, incomplete feature modules, and older prototype files in the same root folder.

## 2. Folder Structure

```text
D:\FTMS PRO
|-- ftms_pro.py                  Main application shell / entry point
|-- FTMS_Add_Vehicle_UI.py        Active add vehicle form
|-- edit_vehicles.py              Edit category/menu page
|-- edit_commercial.py            Commercial vehicle edit screen
|-- vehicle_insurance.py          Vehicle insurance form
|-- vehicle_report.py             Vehicle reporting/filter/export screen
|-- convert_pdf.py                PDF report settings and generation
|-- document_to_pdf.py            Scanner/document-to-PDF prototype
|-- database.py                   Outdated DB creation script
|-- company_setup.py              Company setup standalone/prototype
|-- login.py                      Old edit-login prototype
|-- newlogin.py                   Active simple admin password dialog
|-- newvehicle.py                 Old add-vehicle prototype
|-- vehicle_management_module.py  Old vehicle-management prototype
|-- font_manager.py               Font discovery/ReportLab helper
|-- globals.py                    Constants
|-- ui_components.py              Shared header/title helpers
|-- header.py                     Older header helper
|-- models.py                     FontInfo dataclass
|-- ftms.db                       Active SQLite database
|-- IMAGES                        App images/logos/backgrounds
|-- FTMS_DATA                     Saved vehicle document images
|-- MODELS                        Report/font model dataclasses
|-- repositories                  Repository placeholders
|-- edit trial                    Notes/prototype snippets
```

## 3. Python Files, Classes, and Purpose

| File | Classes / Major Functions | Purpose |
|---|---|---|
| `ftms_pro.py` | `FTMSApp` | Main Tkinter app, sidebar, dashboard, menu routing, overlays, opens add/edit/insurance/report pages. |
| `FTMS_Add_Vehicle_UI.py` | `AddVehicleWindow` | Active add vehicle form; validates vehicle data; loads brands/models/plate codes; saves vehicles and document images. |
| `edit_vehicles.py` | `EditPage` | Admin edit landing page; opens commercial vehicle edit screen. |
| `edit_commercial.py` | `EditCommercial` | Lists/searches vehicles, loads selected vehicle, enables edit mode, updates vehicle fields, writes history. |
| `vehicle_insurance.py` | `InsurancePage` | Insurance details form; loads vehicles; calculates expiry date; saves insurance record. |
| `vehicle_report.py` | `VehicleReportPage` | Vehicle report table, basic/advanced filtering, sorting, Excel export, PDF export launcher. |
| `convert_pdf.py` | `ConvertPdf` | PDF settings UI, field selection, margins, fonts, company/logo options, preview, ReportLab PDF generation. |
| `document_to_pdf.py` | `GraceScan` | Scanner/document conversion prototype with WIA scanner detection and file list UI. |
| `database.py` | `create_database()` | Creates an older schema; does not match the current active database. |
| `company_setup.py` | standalone functions | Standalone company profile editor; prototype/legacy. |
| `login.py` | `LoginEdit` | Old edit authorization prototype; imports missing `edit` module. |
| `newlogin.py` | `LoginDialog` | Simple admin password popup using hardcoded password. |
| `newvehicle.py` | `AddVehicleWindow` | Old simple add vehicle prototype. |
| `vehicle_management_module.py` | `vehicle_management()` | Old embedded add vehicle form using outdated schema. |
| `font_manager.py` | `FontManager` | Scans Windows fonts, stores font metadata, registers fonts for ReportLab. |
| `models.py` | `FontInfo` | Dataclass for font metadata. |
| `MODELS/report_font_settings.py` | `ReportFontSettings` | Dataclass for report font settings. |
| `repositories/report_font_repository.py` | `ReportFontRepository` | Placeholder repository for report font settings. |
| `globals.py` | constants | Emirate codes, system/company names, shared colors/fonts. |
| `ui_components.py` | `create_header()`, `create_page_title()` | Shared UI helpers used by active screens. |
| `header.py` | `create_header()` | Older header helper used by legacy/prototype screens. |
| `testgs.py` | import checks | Scanner/Pillow/ReportLab environment test script. |

## 4. Major Workflow

Application startup:

1. Run `ftms_pro.py`.
2. `FontManager.register_fonts()` scans Windows fonts.
3. `FTMSApp` builds the main window, sidebar, submenu area, content area, and dashboard.

Vehicle add workflow:

1. `FTMSApp.open_add_vehicle()` creates an overlay.
2. `AddVehicleWindow` displays the add vehicle form.
3. Brand/model/plate codes load from SQLite.
4. User enters vehicle details, VIN, engine number, Mulkiya dates, odometer, and uploads images.
5. Vehicle is inserted into `vehicles`.
6. Images are copied to `FTMS_DATA\VEHICLE_DOCS\<plate_number>`.

Vehicle edit workflow:

1. User opens edit vehicle.
2. `LoginDialog` checks password.
3. `EditPage` opens edit category screen.
4. `EditCommercial` lists/searches vehicles.
5. User selects vehicle, enables edit, updates allowed fields.
6. `vehicles` is updated and `vehicle_history` is written.

Insurance workflow:

1. `InsurancePage` loads vehicle list.
2. User enters insurance details.
3. Expiry date is calculated.
4. Record is saved to `vehicle_insurance`.

Report/PDF workflow:

1. `VehicleReportPage` loads vehicle records into Treeview.
2. User filters/sorts/searches.
3. Excel export uses pandas.
4. PDF export opens `ConvertPdf`.
5. `ConvertPdf` lets user select fields, page settings, fonts, company/logo options, then generates PDF using ReportLab.

## 5. SQLite Tables

Active database: `ftms.db`

| Table | Purpose |
|---|---|
| `vehicles` | Main active vehicle master table. Contains plate data, brand/model, vehicle type, fuel, odometer, image paths, status, VIN, engine number, ownership, Mulkiya dates. |
| `VEHICLES_OLD` | Old vehicle table retained in DB; some old foreign keys still point here. |
| `vehicle_insurance` | Insurance policy records linked to vehicles by `vehicle_id`. |
| `vehicle_brands` | Brand master list. |
| `vehicle_models` | Model master list linked by `brand_id`. |
| `plate_codes` | Plate source and code master data. |
| `vehicle_history` | Stores vehicle field changes. |
| `drivers` | Driver master table. |
| `odometer_entries` | Odometer readings. |
| `fuel_entries` | Fuel records. |
| `accidents` | Accident records. |
| `breakdowns` | Breakdown records. |
| `repairs` | Repair records. |
| `battery_replacements` | Battery replacement records. |
| `tyre_replacements` | Tyre replacement records. |
| `admin_baseline` | Default/baseline configuration. |
| `company` | Company profile used by PDF/company setup. |
| `settings` | Alternate settings/company table. |
| `sqlite_sequence` | SQLite internal autoincrement table. |

Important database issue: `database.py` creates an older schema using `vehicles.vehicle_number`, while the active app uses `plate_source`, `plate_code`, `plate_number`, `vehicle_type`, `fuel_type`, `chassis_no`, and many other newer fields. Fresh setup from `database.py` will not recreate the current working database.

## 6. Module Relationships

```text
ftms_pro.py
|-- FTMS_Add_Vehicle_UI.AddVehicleWindow
|-- vehicle_insurance.InsurancePage
|-- vehicle_report.VehicleReportPage
|-- edit_vehicles.EditPage
|-- newlogin.LoginDialog
|-- font_manager.FontManager

FTMS_Add_Vehicle_UI.py
|-- ui_components
|-- vehicle_insurance
|-- ftms.db: vehicles, vehicle_brands, vehicle_models, plate_codes

edit_vehicles.py
|-- edit_commercial.EditCommercial

edit_commercial.py
|-- ftms.db: vehicles, vehicle_history

vehicle_report.py
|-- convert_pdf.ConvertPdf
|-- ftms.db: vehicles

convert_pdf.py
|-- font_manager.FontManager
|-- reportlab
|-- pandas
|-- ftms.db: company, vehicles
```

## 7. External Libraries Used

Standard Python:

- `tkinter`, `tkinter.ttk`, `messagebox`, `filedialog`
- `sqlite3`
- `datetime`
- `os`, `shutil`, `tempfile`
- `re`, `math`
- `dataclasses`

Third-party:

- `Pillow` / `PIL`
- `tkcalendar`
- `pandas`
- `reportlab`
- `openpyxl`
- `fontTools`
- `pywin32` / `win32com.client`
- `twain` is referenced in `testgs.py` but is not installed in the current environment.

## 8. Incomplete Modules

- `convert_pdf.py`: preview/export has incomplete logic; `show_preview()` references undefined `row_height`; `export_document_pdf()` references mismatched/undefined variables.
- `document_to_pdf.py`: scanner UI exists, but `create_bottom_panel`, `create_status_bar`, `detect_scanners`, and `refresh_scanners` are placeholders.
- `repositories/report_font_repository.py`: `get_settings()` is not implemented.
- `MODELS/font_info.py`: empty file.
- `font_manager.py`: some methods are incomplete/buggy, including `get_tk_font()` and `get_family_fonts()`.
- `database.py`: incomplete for current system because it does not create the active schema.

## 9. Prototype / Legacy Modules

- `newvehicle.py`: old simple add vehicle form.
- `vehicle_management_module.py`: old vehicle insert form using outdated `vehicle_number` schema.
- `login.py`: old edit authorization prototype; imports missing `edit`.
- `company_setup.py`: standalone company setup utility; not integrated cleanly with main app.
- `document_to_pdf.py`: scanner/document prototype.
- `testgs.py`: dependency test script.
- `header.py`: older header helper.
- `edit trial/*.txt`: development notes/prototype snippets.

## 10. Missing Features and Current Gaps

Missing business features:

- Driver management screens.
- Employee creation/editing.
- Vehicle assignment/undertake workflow.
- Route assignment.
- Odometer entry module.
- Fuel entry module.
- Accident, breakdown, maintenance, document renewal, total expense reports.
- Staff reports.
- Admin user management, roles, and settings.
- Complete scanner/document-to-PDF workflow.

Technical gaps:

- No real authentication system; admin password is hardcoded as `Admin123`.
- No role-based permissions.
- No password hashing.
- No migration system.
- No `requirements.txt` or packaging file.
- No automated tests.
- Hard-coded absolute paths such as `D:\FTMS PRO`.
- Inconsistent database paths and casing: `ftms.db`, `D:/FTMS PRO/ftms.db`, `D:\FTMS PRO\Ftms.db`.
- SQL/report filter logic should be parameterized.
- Some foreign keys still reference `VEHICLES_OLD`.
- Active and prototype files are mixed together.

## 11. Key Known Bugs

- `FTMSApp.set_page_title()` displays literal `(text)` instead of the provided title.
- `vehicle_insurance.py` assigns buttons with `.grid()`, so button variables become `None`.
- `vehicle_insurance.py` stores vehicle display text in `vehicle_id` instead of numeric `vehicles.id`.
- `vehicle_report.py` has a missing comma between `"30 - Articulated Truck"` and `"40 - Semi Trailer"`.
- `vehicle_report.py` builds raw SQL strings for advanced filters.
- `convert_pdf.py` preview and document export paths contain undefined variables.
- `edit_commercial.py` uses `stat="disabled"` instead of `state="disabled"`.
- `company_setup.py` also uses `stat="disabled"`.
- `login.py` imports missing module `edit`.

## 12. Recommended Next Steps

1. Back up `ftms.db`.
2. Fix critical runtime bugs in insurance, report filtering, PDF preview, and edit workflow.
3. Add a central `config.py` for `BASE_DIR`, `DB_PATH`, `IMAGE_DIR`, and `DATA_DIR`.
4. Replace hard-coded paths with project-relative paths.
5. Create a real migration/setup script matching the active DB schema.
6. Move database logic into repository/service modules.
7. Separate active files from prototype/legacy files.
8. Add authentication with hashed passwords and user roles.
9. Add automated smoke tests for startup, vehicle save, insurance save, report loading, and PDF generation.

