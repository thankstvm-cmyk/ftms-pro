import os
import sqlite3
from datetime import datetime

from employees_form import EmployeeForm as LegacyEmployeeForm


class EmployeeForm(LegacyEmployeeForm):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self.employee_id_var = getattr(self, "emp_no_var", None)
        if hasattr(self, "new_btn"):
            self.new_btn.config(state="normal")
        self._refresh_employee_id_preview()

    def _get_database_path(self):
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), "ftms.db")

    def _compute_next_employee_code(self, connection):
        year = datetime.today().strftime("%Y")
        next_code = f"{year}/001"
        if connection is None:
            return next_code

        columns = {
            row[1]
            for row in connection.execute("PRAGMA table_info(employees)")
        }
        if "employee_code" not in columns:
            return next_code

        highest = 0
        rows = connection.execute(
            "SELECT employee_code FROM employees WHERE employee_code LIKE ?",
            (f"{year}/%",),
        ).fetchall()

        for (code,) in rows:
            if not code:
                continue
            try:
                _, sequence = str(code).split("/", 1)
                highest = max(highest, int(sequence))
            except ValueError:
                continue

        return f"{year}/{highest + 1:03d}"

    def _refresh_employee_id_preview(self):
        next_id = f"{datetime.today().strftime('%Y')}/001"
        database_path = self._get_database_path()

        try:
            if os.path.isfile(database_path):
                with sqlite3.connect(database_path) as connection:
                    next_id = self._compute_next_employee_code(connection)
        except sqlite3.Error:
            pass

        if self.employee_id_var is not None:
            self.employee_id_var.set(next_id)
        return next_id

    def _normalize_eid_value(self, eid):
        return (eid or "").strip()

    def new_employee(self):
        self.resetting_form = True
        self.name_var.set("")
        self.name.delete(0, "end")
        self.dob_var.set("")
        self.dob_entry.delete(0, "end")
        self.dob_entry.insert(0, "__-__-____")
        self.eid_var.set("")
        self.eid_entry.delete(0, "end")
        self.eid_entry.insert(0, "784-XXXX-XXXXXXX-X")
        self.mobile_var.set("")
        self.mobile_status.config(text="", fg="black")
        self.nationality_var.set("")
        self.jdt_var.set("")
        self.jdt_entry.delete(0, "end")
        self.jdt_entry.insert(0, "DD-MM-YYYY")
        self.jdt_entry.config(fg="grey")
        self.emp_role.set("")
        self.emp_status.set("Active")
        self.availability_var.set("Available")
        self.exit_dt.set("")
        self.exit_entry.config(state="normal")
        self.exit_entry.delete(0, "end")
        self.exit_entry.insert(0, "DD-MM-YYYY")
        self.exit_entry.config(state="disabled")
        self.license_frame.grid_remove()
        for code, var in self.license_vars.items():
            var.set(0)
            self.license_checkboxes[code].grid()
            self.license_checkboxes[code].config(state="normal", bg="white")
        self.set_btn.config(text="SET", bg="#1e3a5f")
        self.category_mode = "SET"
        self.message_var.set("")

        next_id = f"{datetime.today().strftime('%Y')}/001"
        database_path = self._get_database_path()
        try:
            if os.path.isfile(database_path):
                with sqlite3.connect(database_path) as connection:
                    next_id = self._compute_next_employee_code(connection)
        except sqlite3.Error:
            pass

        if self.employee_id_var is not None:
            self.employee_id_var.set(next_id)

        self.name.focus_set()
        self.resetting_form = False
        self.show_message("New form opened. Enter employee details.", "INFO")

    def new_vehicle(self):
        self.new_employee()

    def update_documents(self):
        if hasattr(self, "eid_var"):
            eid = self._normalize_eid_value(self.eid_var.get())
            self.eid_var.set(eid)
        else:
            eid = self._normalize_eid_value("")

        if not eid:
            self.show_message("Enter employee EID before updating documents.", "WARNING")
            if hasattr(self, "eid_entry"):
                self.eid_entry.focus_set()
            return None

        return self.save_vehicle()
