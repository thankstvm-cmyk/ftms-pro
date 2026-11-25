import sqlite3
import tkinter as tk
from datetime import date, datetime, timedelta
from math import isfinite
from tkinter import filedialog, messagebox, ttk
from pathlib import Path

from PIL import Image, ImageTk

from config import DATABASE_PATH


VEHICLE_KINDS = ("Bike", "Bus")
PLATE_SOURCES = (
    "Abu Dhabi",
    "Ajman",
    "Dubai",
    "Fujairah",
    "Ras Al Khaimah",
    "Sharjah",
    "Umm Al Quwain",
)
FUEL_TYPES = ("Petrol", "Diesel", "Electric", "Hybrid", "CNG", "Other")
TRANSMISSIONS = ("Manual", "Automatic", "CVT", "Other")
FALLBACK_PLATE_CODES = {
    "Abu Dhabi": ("AD", "1", "2", "3"),
    "Ajman": ("1", "2", "3"),
    "Dubai": tuple("ABCDEFGHIJKLMNOPQRSTUVWXYZ") + ("AA", "BB"),
    "Fujairah": ("1", "2", "3"),
    "Ras Al Khaimah": ("1", "2", "3"),
    "Sharjah": ("1", "2", "3"),
    "Umm Al Quwain": ("1", "2", "3"),
}


def ensure_bike_bus_details_table(connection):
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS bike_bus_details (
            vehicle_id INTEGER PRIMARY KEY,
            registration_id TEXT UNIQUE NOT NULL,
            vehicle_kind TEXT NOT NULL,
            colour TEXT,
            engine_capacity_cc INTEGER,
            transmission_type TEXT,
            air_conditioning TEXT,
            assigned_driver TEXT,
            assigned_route TEXT,
            department TEXT,
            remarks TEXT,
            insurance_document_path TEXT,
            other_document_path TEXT,
            FOREIGN KEY (vehicle_id) REFERENCES vehicles(id)
        )
        """
    )


def save_bike_bus(connection, values):
    cursor = connection.cursor()
    existing_plate = cursor.execute(
        """
        SELECT 1 FROM vehicles
        WHERE plate_source = ? AND plate_code = ? AND plate_number = ?
        LIMIT 1
        """,
        (values["plate_source"], values["plate_code"], int(values["plate_number"])),
    ).fetchone()
    if existing_plate:
        raise sqlite3.IntegrityError("This plate is already registered.")
    cursor.execute("SAVEPOINT save_bike_bus")
    try:
        cursor.execute(
            """
            INSERT INTO vehicles (
                plate_source, plate_code, plate_number, brand, model, year,
                ton_capacity, body_type, vehicle_type, tail_lift, tank_capacity,
                current_odometer, image_path, status, mulkiya_front_path,
                mulkiya_back_path, vehicle_category, seating_capacity, created_at,
                updated_at, fuel_type, chassis_no, engine_no, ownership_type,
                mulkiya_issue_date, mulkiya_expiry_date
            ) VALUES (?, ?, ?, ?, ?, ?, 0, ?, ?, 'No', ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                      ?, ?, ?, ?, ?, ?)
            """,
            (
                values["plate_source"],
                values["plate_code"],
                int(values["plate_number"]),
                values["brand"],
                values["model"],
                int(values["year"]),
                "Motorcycle" if values["vehicle_kind"] == "Bike" else "Bus",
                values["vehicle_kind"],
                float(values["tank_capacity"] or 0),
                int(values["current_odometer"] or 0),
                values.get("vehicle_photo"),
                values["status"],
                values.get("mulkiya_front"),
                values.get("mulkiya_back"),
                values["vehicle_kind"],
                int(values["seating_capacity"] or (2 if values["vehicle_kind"] == "Bike" else 30)),
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                values["fuel_type"],
                values["chassis_number"],
                values["engine_number"],
                values["ownership_type"],
                values["mulkiya_issue_date"],
                values["mulkiya_expiry_date"],
            ),
        )
        vehicle_id = cursor.lastrowid
        registration_id = f"{values['vehicle_kind'].upper()}-{vehicle_id:06d}"
        cursor.execute(
            """
            INSERT INTO bike_bus_details (
                vehicle_id, registration_id, vehicle_kind, colour, engine_capacity_cc,
                transmission_type, air_conditioning, assigned_driver, assigned_route,
                department, remarks, insurance_document_path, other_document_path
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                vehicle_id,
                registration_id,
                values["vehicle_kind"],
                values["colour"],
                int(values["engine_capacity_cc"] or 0),
                values["transmission_type"],
                values["air_conditioning"],
                values["assigned_driver"],
                values["assigned_route"],
                values["department"],
                values["remarks"],
                values.get("insurance_document"),
                values.get("other_document"),
            ),
        )
        cursor.execute("RELEASE SAVEPOINT save_bike_bus")
        connection.commit()
    except (sqlite3.Error, ValueError, TypeError, KeyError):
        cursor.execute("ROLLBACK TO SAVEPOINT save_bike_bus")
        cursor.execute("RELEASE SAVEPOINT save_bike_bus")
        raise
    return registration_id


class BikeBusRegistration:
    def __init__(self, parent, controller, vehicle_kind="Bike"):
        self.parent = parent
        self.controller = controller
        self.vehicle_kind = vehicle_kind if vehicle_kind in VEHICLE_KINDS else "Bike"
        self.connection = sqlite3.connect(DATABASE_PATH)
        ensure_bike_bus_details_table(self.connection)
        self.fields = {}
        self.documents = {}
        self.frame = tk.Frame(parent, bg="#eaf1fa")
        self.frame.pack(fill="both", expand=True)
        self._build()

    def _build(self):
        header = tk.Frame(self.frame, bg="#102f59", padx=20, pady=12)
        header.pack(fill="x")
        tk.Label(
            header,
            text="BIKE & BUS REGISTRATION",
            bg="#102f59",
            fg="white",
            font=("Segoe UI", 18, "bold"),
        ).pack(side="left")
        tk.Label(
            header,
            text="Register and manage two-wheelers and buses",
            bg="#102f59",
            fg="#dbeafe",
            font=("Segoe UI", 10),
        ).pack(side="left", padx=18, pady=(5, 0))
        ttk.Button(header, text="Close", command=self.close).pack(side="right")

        toolbar = tk.Frame(self.frame, bg="#eaf1fa", padx=18, pady=8)
        toolbar.pack(fill="x")
        tk.Label(toolbar, text="Vehicle type", bg="#eaf1fa", fg="#18365d",
                 font=("Segoe UI", 10, "bold")).pack(side="left", padx=(0, 10))
        self.kind_var = tk.StringVar(value=self.vehicle_kind)
        for kind in VEHICLE_KINDS:
            ttk.Radiobutton(
                toolbar,
                text=f"Add {kind}",
                value=kind,
                variable=self.kind_var,
                command=self._kind_changed,
            ).pack(side="left", padx=6)

        self.notebook = ttk.Notebook(self.frame)
        self.notebook.pack(fill="both", expand=True, padx=16, pady=(0, 8))
        self.registration_tab = self._tab("Registration Details")
        self.technical_tab = self._tab("Technical Specifications")
        self.operations_tab = self._tab("Operational Information")
        self.documents_tab = self._tab("Documents & Others")
        self._build_registration()
        self._build_technical()
        self._build_operations()
        self._build_documents()

        actions = tk.Frame(self.frame, bg="#eaf1fa", padx=18, pady=10)
        actions.pack(fill="x")
        ttk.Button(actions, text="Save", command=self.save).pack(side="left", padx=4)
        ttk.Button(actions, text="New", command=self.new_form).pack(side="left", padx=4)
        ttk.Button(actions, text="Reset", command=self.reset_form).pack(side="left", padx=4)
        ttk.Button(actions, text="Open Insurance", command=self.open_insurance).pack(side="left", padx=4)
        ttk.Button(actions, text="Documents", command=lambda: self.notebook.select(self.documents_tab)).pack(side="left", padx=4)
        self.status_label = tk.Label(actions, text="", bg="#eaf1fa", fg="#16733c")
        self.status_label.pack(side="left", padx=14)

    def _tab(self, title):
        tab = tk.Frame(self.notebook, bg="#f8fafc", padx=16, pady=14)
        self.notebook.add(tab, text=title)
        return tab

    def _section(self, parent, title, column, row):
        section = ttk.LabelFrame(parent, text=title, padding=(12, 10))
        section.grid(row=row, column=column, sticky="nsew", padx=8, pady=8)
        parent.grid_columnconfigure(column, weight=1)
        return section

    def _field(self, parent, label, name, row, column, values=None, readonly=False, default=""):
        tk.Label(parent, text=label, bg="#f8fafc", fg="#18365d",
                 font=("Segoe UI", 9)).grid(row=row, column=column * 2, sticky="w", padx=(4, 8), pady=7)
        if values is not None:
            widget = ttk.Combobox(parent, values=values, state="readonly" if readonly else "normal")
            if default:
                widget.set(default)
        elif name == "registration_id":
            variable = tk.StringVar(value=self._next_registration_id())
            widget = ttk.Entry(parent, textvariable=variable, state="readonly")
        else:
            widget = ttk.Entry(parent)
            if default:
                widget.insert(0, default)
        widget.grid(row=row, column=column * 2 + 1, sticky="ew", padx=(0, 12), pady=5)
        parent.grid_columnconfigure(column * 2 + 1, weight=1)
        self.fields[name] = widget
        return widget

    def _build_registration(self):
        self.registration_tab.grid_columnconfigure((0, 1), weight=1)
        info = self._section(self.registration_tab, "Registration Information", 0, 0)
        photo = self._section(self.registration_tab, "Vehicle Preview & Documents", 1, 0)
        self._field(info, "Vehicle ID", "registration_id", 0, 0)
        self._field(info, "Plate Source *", "plate_source", 1, 0, PLATE_SOURCES, True)
        self._field(info, "Plate Code *", "plate_code", 2, 0, ("A", "B", "C", "D", "E", "F", "G", "H", "I", "J"), True)
        self._field(info, "Plate Number *", "plate_number", 3, 0)
        self._field(info, "Brand *", "brand", 0, 1, self._brands())
        self._field(info, "Model *", "model", 1, 1)
        current_year = date.today().year
        self._field(info, "Manufacturing Year *", "year", 2, 1,
                    tuple(str(year) for year in range(current_year, 1989, -1)), True, str(current_year))
        self._field(info, "Colour *", "colour", 3, 1,
                    ("Black", "Blue", "Green", "Grey", "Red", "White", "Other"))
        preview = tk.Label(photo, text="Vehicle photo preview", bg="#e6edf7", fg="#60758f",
                           height=8, font=("Segoe UI", 11))
        preview.pack(fill="both", expand=True, padx=4, pady=5)
        self.preview_label = preview
        ttk.Button(photo, text="Upload Vehicle Photo", command=lambda: self._choose_document("vehicle_photo", "Vehicle Photo", True)).pack(pady=(4, 8))
        self.fields["plate_source"].bind("<<ComboboxSelected>>", self._load_plate_codes)

    def _build_technical(self):
        self.technical_tab.grid_columnconfigure((0, 1), weight=1)
        left = self._section(self.technical_tab, "Engine & Identification", 0, 0)
        right = self._section(self.technical_tab, "Capacity & Equipment", 1, 0)
        self._field(left, "Engine Number *", "engine_number", 0, 0)
        self._field(left, "Chassis Number *", "chassis_number", 1, 0)
        self._field(left, "Fuel Type *", "fuel_type", 2, 0, FUEL_TYPES, True, "Petrol")
        self._field(left, "Engine Capacity (CC)", "engine_capacity_cc", 3, 0)
        self._field(right, "Tank Capacity (L)", "tank_capacity", 0, 0)
        self._field(right, "Current Odometer (km)", "current_odometer", 1, 0)
        self._field(right, "Seating Capacity *", "seating_capacity", 2, 0, default="2" if self.vehicle_kind == "Bike" else "30")
        self._field(right, "Transmission Type", "transmission_type", 3, 0, TRANSMISSIONS)
        self._field(right, "Air Conditioning", "air_conditioning", 4, 0, ("Yes", "No"), True, "No")

    def _build_operations(self):
        self.operations_tab.grid_columnconfigure((0, 1), weight=1)
        left = self._section(self.operations_tab, "Ownership & Status", 0, 0)
        right = self._section(self.operations_tab, "Assignment & Notes", 1, 0)
        self._field(left, "Ownership Type *", "ownership_type", 0, 0,
                    ("Company Owned", "Rented In", "Leased"), True, "Company Owned")
        self._field(left, "Vehicle Status *", "status", 1, 0,
                    ("Active", "Under Repair", "Inactive"), True, "Active")
        self._field(right, "Assigned Driver", "assigned_driver", 0, 0)
        self._field(right, "Assigned Route", "assigned_route", 1, 0)
        self._field(right, "Department", "department", 2, 0)
        self._field(right, "Remarks", "remarks", 3, 0)

    def _build_documents(self):
        self.documents_tab.grid_columnconfigure((0, 1), weight=1)
        dates = self._section(self.documents_tab, "Mulkiya (Registration Card)", 0, 0)
        uploads = self._section(self.documents_tab, "Vehicle Documents", 1, 0)
        self._field(dates, "Mulkiya Issue Date *", "mulkiya_issue_date", 0, 0, default=date.today().isoformat())
        self._field(dates, "Mulkiya Expiry Date *", "mulkiya_expiry_date", 1, 0,
                    default=(date.today() + timedelta(days=364)).isoformat())
        self.fields["mulkiya_issue_date"].bind("<FocusOut>", self._update_expiry)
        for row, (key, title, images_only) in enumerate((
            ("mulkiya_front", "Mulkiya (Front)", True),
            ("mulkiya_back", "Mulkiya (Back)", True),
            ("insurance_document", "Insurance", False),
            ("other_document", "Other Document", False),
        )):
            line = tk.Frame(uploads, bg="#f8fafc")
            line.grid(row=row, column=0, sticky="ew", padx=4, pady=6)
            line.grid_columnconfigure(0, weight=1)
            label = tk.Label(line, text=f"{title} — not attached", bg="#f8fafc", fg="#52657d", anchor="w")
            label.grid(row=0, column=0, sticky="ew")
            self.document_labels = getattr(self, "document_labels", {})
            self.document_labels[key] = label
            ttk.Button(line, text="Upload", command=lambda k=key, t=title, i=images_only: self._choose_document(k, t, i)).grid(row=0, column=1, padx=8)

    def _brands(self):
        try:
            rows = self.connection.execute("SELECT brand_name FROM vehicle_brands ORDER BY brand_name").fetchall()
            return tuple(row[0] for row in rows)
        except sqlite3.OperationalError:
            return ()

    def _next_registration_id(self):
        row = self.connection.execute("SELECT COALESCE(MAX(id), 0) + 1 FROM vehicles").fetchone()
        return f"{self.vehicle_kind.upper()}-{row[0]:06d}"

    def _load_plate_codes(self, event=None):
        source = self.fields["plate_source"].get()
        try:
            rows = self.connection.execute(
                "SELECT DISTINCT plate_code FROM plate_codes WHERE plate_source = ? ORDER BY plate_code",
                (source,),
            ).fetchall()
            codes = tuple(row[0] for row in rows)
        except sqlite3.OperationalError:
            codes = ()
        if not codes:
            codes = FALLBACK_PLATE_CODES.get(source, ())
        combo = self.fields["plate_code"]
        combo.configure(values=codes)
        combo.set("")

    def _kind_changed(self):
        self.vehicle_kind = self.kind_var.get()
        self.fields["registration_id"].configure(state="normal")
        self.fields["registration_id"].delete(0, tk.END)
        self.fields["registration_id"].insert(0, self._next_registration_id())
        self.fields["registration_id"].configure(state="readonly")
        self.fields["seating_capacity"].delete(0, tk.END)
        self.fields["seating_capacity"].insert(0, "2" if self.vehicle_kind == "Bike" else "30")

    def _update_expiry(self, event=None):
        try:
            issue_date = date.fromisoformat(self.fields["mulkiya_issue_date"].get().strip())
        except ValueError:
            return
        expiry = self.fields["mulkiya_expiry_date"]
        expiry.delete(0, tk.END)
        expiry.insert(0, (issue_date + timedelta(days=364)).isoformat())

    def _choose_document(self, key, title, images_only=False):
        filetypes = [("Images", "*.jpg *.jpeg *.png *.webp")] if images_only else [
            ("Documents", "*.pdf *.jpg *.jpeg *.png"),
            ("All files", "*.*"),
        ]
        path = filedialog.askopenfilename(title=f"Select {title}", filetypes=filetypes)
        if not path:
            return
        self.documents[key] = path
        if key == "vehicle_photo":
            try:
                image = Image.open(path)
            except OSError as error:
                self.documents.pop(key, None)
                messagebox.showerror("Could not open photo", str(error), parent=self.frame)
                return
            image.thumbnail((360, 190))
            self.vehicle_photo = ImageTk.PhotoImage(image)
            self.preview_label.configure(image=self.vehicle_photo, text="")
        else:
            self.document_labels[key].configure(text=f"{title} — {Path(path).name}", fg="#16733c")

    def _value(self, name):
        return self.fields[name].get().strip()

    def _collect_values(self):
        values = {name: self._value(name) for name in (
            "plate_source", "plate_code", "plate_number", "brand", "model", "year",
            "colour", "engine_number", "chassis_number", "fuel_type", "engine_capacity_cc",
            "tank_capacity", "current_odometer", "seating_capacity", "transmission_type",
            "air_conditioning", "ownership_type", "status", "assigned_driver",
            "assigned_route", "department", "remarks", "mulkiya_issue_date",
            "mulkiya_expiry_date",
        )}
        values["vehicle_kind"] = self.vehicle_kind
        values.update(self.documents)
        return values

    def save(self):
        values = self._collect_values()
        required = ("plate_source", "plate_code", "plate_number", "brand", "model", "year",
                    "colour", "engine_number", "chassis_number", "fuel_type", "seating_capacity",
                    "ownership_type", "status", "mulkiya_issue_date", "mulkiya_expiry_date")
        missing = [field.replace("_", " ").title() for field in required if not values[field]]
        if missing:
            self.notebook.select(self.registration_tab if missing[0] in {
                "Plate Source", "Plate Code", "Plate Number", "Brand", "Model", "Year", "Colour"
            } else self.technical_tab)
            messagebox.showwarning("Missing information", "Complete required fields: " + ", ".join(missing), parent=self.frame)
            return
        if not values["plate_number"].isdigit() or len(values["plate_number"]) > 5:
            self.notebook.select(self.registration_tab)
            messagebox.showwarning("Invalid plate number", "Enter a plate number with up to five digits.", parent=self.frame)
            return
        try:
            issue = date.fromisoformat(values["mulkiya_issue_date"])
            expiry = date.fromisoformat(values["mulkiya_expiry_date"])
            if expiry <= issue:
                raise ValueError
            for name in ("engine_capacity_cc", "current_odometer", "seating_capacity"):
                if values[name] and (not values[name].isdigit() or int(values[name]) < 0):
                    raise ValueError
            if values["tank_capacity"]:
                tank_capacity = float(values["tank_capacity"])
                if not isfinite(tank_capacity) or tank_capacity < 0:
                    raise ValueError
        except ValueError:
            self.notebook.select(self.documents_tab)
            messagebox.showwarning("Invalid details", "Check the numeric fields and enter valid ISO dates (YYYY-MM-DD); expiry must be after issue date.", parent=self.frame)
            return
        try:
            registration_id = save_bike_bus(self.connection, values)
        except sqlite3.IntegrityError as error:
            messagebox.showerror("Could not save vehicle", f"A vehicle with this plate or registration ID already exists.\n{error}", parent=self.frame)
            return
        except sqlite3.Error as error:
            messagebox.showerror("Database error", str(error), parent=self.frame)
            return
        self.fields["registration_id"].configure(state="normal")
        self.fields["registration_id"].delete(0, tk.END)
        self.fields["registration_id"].insert(0, registration_id)
        self.fields["registration_id"].configure(state="readonly")
        self.status_label.configure(text=f"{registration_id} saved successfully")
        messagebox.showinfo("Saved", f"{self.vehicle_kind} registration {registration_id} saved.", parent=self.frame)

    def reset_form(self):
        for name, widget in self.fields.items():
            if name == "registration_id":
                widget.configure(state="normal")
                widget.delete(0, tk.END)
                widget.insert(0, self._next_registration_id())
                widget.configure(state="readonly")
            elif isinstance(widget, ttk.Combobox):
                widget.set("")
            else:
                widget.delete(0, tk.END)
        self.fields["year"].set(str(date.today().year))
        self.fields["fuel_type"].set("Petrol")
        self.fields["ownership_type"].set("Company Owned")
        self.fields["status"].set("Active")
        self.fields["air_conditioning"].set("No")
        self.fields["mulkiya_issue_date"].insert(0, date.today().isoformat())
        self.fields["mulkiya_expiry_date"].insert(0, (date.today() + timedelta(days=364)).isoformat())
        self.fields["seating_capacity"].insert(0, "2" if self.vehicle_kind == "Bike" else "30")
        self.documents.clear()
        for key, label in self.document_labels.items():
            label.configure(text=key.replace("_", " ").title() + " — not attached", fg="#52657d")
        self.preview_label.configure(image="", text="Vehicle photo preview")
        self.status_label.configure(text="")

    def new_form(self):
        self.reset_form()
        self.notebook.select(self.registration_tab)

    def open_insurance(self):
        self.connection.close()
        try:
            self.parent.grab_release()
        except tk.TclError:
            pass
        self.parent.destroy()
        self.controller.open_vehicleins_page()

    def close(self):
        self.connection.close()
        try:
            self.parent.grab_release()
        except tk.TclError:
            pass
        self.parent.destroy()
        self.controller.set_form_mode(False)
        self.controller.clear_content_area()
