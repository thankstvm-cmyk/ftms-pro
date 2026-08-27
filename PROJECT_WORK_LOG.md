# FTMS PRO - Project Work Log

## 2026-07-01 - Session 01

### Tasks Completed Today

- Analyzed the FTMS PRO project structure and current codebase.
- Created `PROJECT_MASTER_DOCUMENT.md` as a concise master project reference.
- Created `config.py` to centralize project-relative paths using `pathlib.Path`.
- Updated `ftms_pro.py` to use `IMAGE_DIR` from `config.py` instead of hard-coded image paths.
- Updated `globals.py` to use `IMAGE_DIR` from `config.py` for `IMAGE_FOLDER`.
- Reviewed `ui_components.py` for hard-coded paths; no changes were needed.
- Inspected `font_manager.py` for project paths and Windows font paths; no changes were made.

### Files Modified

- `PROJECT_MASTER_DOCUMENT.md`
- `PROJECT_WORK_LOG.md`
- `config.py`
- `ftms_pro.py`
- `globals.py`

### Files Reviewed Without Changes

- `ui_components.py`
- `font_manager.py`

### Verification Performed

- Ran `python -m py_compile ftms_pro.py` successfully.
- Ran `python -m py_compile globals.py` successfully.
- Ran `python -m py_compile ui_components.py` successfully.
- Ran `python -m py_compile font_manager.py` successfully.
- Scanned `ftms_pro.py` for remaining hard-coded project paths; none found.
- Scanned `globals.py` for remaining hard-coded project paths; none found.
- Scanned `ui_components.py` for hard-coded project paths; none found.
- Confirmed `font_manager.py` has no hard-coded FTMS project paths.

### Decisions Taken

- Use `config.py` as the central location for project paths.
- Use `pathlib.Path` for all new project path constants.
- Refactor path usage gradually, one file at a time, to reduce risk.
- Do not change application logic during path refactoring.
- Leave `font_manager.py` unchanged for now because its hard-coded path is a Windows system font directory, not an FTMS project path.
- Keep `PROJECT_MASTER_DOCUMENT.md` and `PROJECT_WORK_LOG.md` as daily review documents.

### Problems Found

- Many modules still contain hard-coded project paths outside the files already updated.
- `database.py` does not match the active `ftms.db` schema.
- `font_manager.py` contains a hard-coded Windows font directory: `C:\Windows\Fonts`.
- `font_manager.py` also has non-path bugs to fix later, including `startswitch` and fallback font `"Aria"`.
- Several active modules have known runtime issues documented in `PROJECT_MASTER_DOCUMENT.md`.

### Next Tasks For Tomorrow

- Review `PROJECT_MASTER_DOCUMENT.md` and this work log before starting.
- Continue path refactoring one module at a time.
- Suggested next file: `FTMS_Add_Vehicle_UI.py`, because it contains database paths and vehicle document storage paths.
- After that, review `vehicle_insurance.py`, `vehicle_report.py`, `convert_pdf.py`, `company_setup.py`, and `header.py`.
- Begin planning a database schema/migration document after path refactoring.

