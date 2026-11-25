import sqlite3
import tkinter as tk
from datetime import date, datetime, timedelta
from math import isfinite
from tkinter import filedialog, messagebox, ttk

from PIL import Image, ImageTk
from tkcalendar import DateEntry

from config import DATABASE_PATH


VEHICLE_KINDS = ("Bike", "Bus")
VEHICLE_ID_PREFIX = {"Bike": "BIK", "Bus": "BUS"}
PLATE_SOURCES = (
    "Abu Dhabi",
    "Ajman",
    "Dubai",
    "Fujairah",
    "Ras Al Khaymah",
    "Sharjah",
    "Um Al Quewain",
)
FUEL_TYPES = ("Petrol", "Diesel", "Electric", "Hybrid", "CNG", "Other")
TRANSMISSIONS = ("Manual", "Automatic", "CVT", "Other")
FALLBACK_PLATE_CODES = {
    "Abu Dhabi": ("AD", "1", "2", "3"),
    "Ajman": ("1", "2", "3"),
    "Dubai": tuple("ABCDEFGHIJKLMNOPQRSTUVWXYZ") + ("AA", "BB"),
    "Fujairah": ("1", "2", "3"),
    "Ras Al Khaymah": ("1", "2", "3"),
    "Sharjah": ("1", "2", "3"),
    "Um Al Quewain": ("1", "2", "3"),
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
        registration_id = f"{VEHICLE_ID_PREFIX[values['vehicle_kind']]}-{vehicle_id:06d}"
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
        self.connection_closed = False
        self.frame = tk.Frame(parent, bg="#eaf1fa")
        self.frame.pack(fill="both", expand=True)
        self.frame.bind("<Destroy>", self._on_destroy, add="+")
        self._build()

    def _build(self):
        header = tk.Frame(self.frame, bg="#102f59", padx=20, pady=9)
        header.pack(fill="x")
        self.breadcrumb_label = tk.Label(
            header,
            text=f"VEHICLE MANAGEMENT   ›   ADD NEW {self.vehicle_kind.upper()}",
            bg="#102f59",
            fg="#dbeafe",
            font=("Segoe UI", 9, "bold"),
        )
        self.breadcrumb_label.pack(anchor="w")
        title_row = tk.Frame(header, bg="#102f59")
        title_row.pack(fill="x", pady=(5, 0))
        self.vehicle_icon_label = tk.Label(
            title_row,
            text="🏍" if self.vehicle_kind == "Bike" else "🚌",
            bg="#102f59",
            fg="white",
            font=("Segoe UI", 24),
        )
        self.vehicle_icon_label.pack(side="left", padx=(0, 12))
        title_copy = tk.Frame(title_row, bg="#102f59")
        title_copy.pack(side="left", anchor="w")
        self.title_label = tk.Label(
            title_copy,
            text=f"{self.vehicle_kind} Registration",
            bg="#102f59",
            fg="white",
            font=("Segoe UI", 18, "bold"),
        )
        self.title_label.pack(anchor="w")
        self.subtitle_label = tk.Label(
            title_copy,
            text=f"Register and manage {self.vehicle_kind.lower()} vehicle details",
            bg="#102f59",
            fg="#dbeafe",
            font=("Segoe UI", 9),
        )
        self.subtitle_label.pack(anchor="w")
        ttk.Button(title_row, text="Close", command=self.close).pack(side="right", anchor="n")

        toolbar = tk.Frame(self.frame, bg="#f8fafc", padx=12, pady=5)
        toolbar.pack(fill="x")
        self.kind_var = tk.StringVar(value=self.vehicle_kind)
        self.kind_buttons = {}
        for kind in VEHICLE_KINDS:
            button = tk.Button(
                toolbar,
                text=f"  {kind}  ",
                command=lambda selected=kind: self._kind_changed(selected),
                bg="#0759b8" if kind == self.vehicle_kind else "#f8fafc",
                fg="white" if kind == self.vehicle_kind else "#102f59",
                activebackground="#0759b8",
                activeforeground="white",
                relief="flat",
                font=("Segoe UI", 10, "bold"),
                padx=8,
                pady=7,
            )
            button.pack(side="left", padx=3)
            self.kind_buttons[kind] = button
        self.nav_buttons = {}
        self.sections = {}
        nav = tk.Frame(toolbar, bg="#f8fafc")
        nav.pack(side="right")
        for title in ("Registration Details", "Technical Specifications",
                      "Operational Information", "Documents & Others"):
            button = tk.Button(
                nav,
                text=title,
                command=lambda target=title: self._focus_section(target),
                bg="#e5edf8",
                fg="#102f59",
                activebackground="#d4e4f8",
                relief="flat",
                font=("Segoe UI", 9, "bold"),
                padx=10,
                pady=7,
            )
            button.pack(side="left", padx=2)
            self.nav_buttons[title] = button

        content = tk.Frame(self.frame, bg="#eaf1fa")
        content.pack(fill="both", expand=True, padx=10)
        self.canvas = tk.Canvas(content, bg="#eaf1fa", highlightthickness=0)
        scrollbar = ttk.Scrollbar(content, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=scrollbar.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        self.content_frame = tk.Frame(self.canvas, bg="#eaf1fa", padx=6, pady=4)
        self.content_window = self.canvas.create_window((0, 0), window=self.content_frame, anchor="nw")
        self.content_frame.bind("<Configure>", self._update_scroll_region)
        self.canvas.bind("<Configure>", lambda event: self.canvas.itemconfigure(
            self.content_window, width=event.width
        ))
        self.content_frame.grid_columnconfigure((0, 1), weight=1, uniform="vehicle_sections")
        self._build_registration()
        self._build_technical()
        self._build_operations()
        self._build_documents()

        actions = tk.Frame(self.frame, bg="#eaf1fa", padx=14, pady=8)
        actions.pack(fill="x")
        self._action_button(actions, "Save", self.save, "#16a34a", "white")
        self._action_button(actions, "New", self.new_form, "#0866c6", "white")
        self._action_button(actions, "Reset", self.reset_form, "#64748b", "white")
        self._action_button(actions, "Open Insurance", self.open_insurance, "#f8fafc", "#102f59")
        self._action_button(actions, "Documents", lambda: self._focus_section("Documents & Others"), "#f8fafc", "#102f59")
        self._action_button(actions, "Close", self.close, "#fff5f5", "#b42318")
        self.status_label = tk.Label(actions, text="", bg="#eaf1fa", fg="#16733c")
        self.status_label.pack(side="left", padx=14)
        self._focus_section("Registration Details")

    def _action_button(self, parent, text, command, background, foreground):
        tk.Button(
            parent,
            text=text,
            command=command,
            bg=background,
            fg=foreground,
            activebackground=background,
            relief="solid",
            bd=1,
            font=("Segoe UI", 9, "bold"),
            padx=14,
            pady=7,
        ).pack(side="left", padx=4)

    def _update_scroll_region(self, event=None):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _focus_section(self, title):
        section = self.sections.get(title)
        if section is None:
            return
        self.content_frame.update_idletasks()
        height = max(self.content_frame.winfo_height(), 1)
        self.canvas.yview_moveto(max(0, min(1, section.winfo_y() / height)))
        for name, button in self.nav_buttons.items():
            active = name == title
            button.configure(
                bg="#0759b8" if active else "#e5edf8",
                fg="white" if active else "#102f59",
            )

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
            widget = ttk.Entry(parent)
            widget.insert(0, self._next_registration_id())
            widget.configure(state="readonly")
        else:
            widget = ttk.Entry(parent)
            if default:
                widget.insert(0, default)
        widget.grid(row=row, column=column * 2 + 1, sticky="ew", padx=(0, 12), pady=5)
        parent.grid_columnconfigure(column * 2 + 1, weight=1)
        self.fields[name] = widget
        return widget

    def _build_registration(self):
        info = self._section(self.content_frame, "Registration Information", 0, 0)
        photo = self._section(self.content_frame, "Vehicle Preview & Documents", 1, 0)
        self.sections["Registration Details"] = info
        info.grid_columnconfigure((1, 3), weight=1)
        self._field(info, "Vehicle ID *", "registration_id", 0, 0)
        self._field(info, "Brand *", "brand", 0, 1, self._brands())
        self._field(info, "Plate Source *", "plate_source", 1, 0, PLATE_SOURCES, True)
        self._field(info, "Model *", "model", 1, 1, ())
        self._field(info, "Plate Code *", "plate_code", 2, 0, ("A", "B", "C", "D", "E", "F", "G", "H", "I", "J"), True)
        current_year = date.today().year
        self._field(info, "Manufacturing Year *", "year", 2, 1,
                    tuple(str(year) for year in range(current_year, 1989, -1)), True, str(current_year))
        self._field(info, "Plate Number *", "plate_number", 3, 0)
        self._field(info, "Colour *", "colour", 3, 1,
                    ("Black", "Blue", "Green", "Grey", "Red", "White", "Other"))
        self.plate_indicator = tk.Label(
            info,
            text="○",
            bg="#f8fafc",
            fg="#94a3b8",
            font=("Segoe UI", 11, "bold"),
        )
        self.plate_indicator.grid(row=3, column=4, padx=(0, 6))
        self.fields["brand"].bind("<<ComboboxSelected>>", self._load_models)
        preview = tk.Label(photo, text="Vehicle photo preview", bg="#e6edf7", fg="#60758f",
                           height=8, font=("Segoe UI", 11))
        preview.grid(row=0, column=0, rowspan=5, sticky="nsew", padx=4, pady=5)
        photo.grid_columnconfigure(0, weight=3)
        photo.grid_columnconfigure(1, weight=2)
        photo.grid_rowconfigure(0, weight=1)
        self.preview_label = preview
        self.document_labels = {}
        self.document_titles = {}
        for row, (key, title, images_only) in enumerate((
            ("vehicle_photo", "Vehicle Photo", True),
            ("mulkiya_front", "Mulkiya (Front)", True),
            ("mulkiya_back", "Mulkiya (Back)", True),
            ("insurance_document", "Insurance", False),
            ("other_document", "Other Document", False),
        )):
            self._document_row(photo, row, key, title, images_only)
        self.fields["plate_source"].bind("<<ComboboxSelected>>", self._load_plate_codes)
        self.fields["plate_source"].bind("<<ComboboxSelected>>", self._update_plate_indicator, add="+")
        self.fields["plate_code"].bind("<<ComboboxSelected>>", self._update_plate_indicator)
        self.fields["plate_number"].bind("<KeyRelease>", self._update_plate_indicator)

    def _build_technical(self):
        section = self._section(self.content_frame, "Technical Specifications", 0, 1)
        self.sections["Technical Specifications"] = section
        section.grid_columnconfigure((1, 3), weight=1)
        self._field(section, "Engine Number *", "engine_number", 0, 0)
        self._field(section, "Tank Capacity (L)", "tank_capacity", 0, 1)
        self._field(section, "Chassis Number *", "chassis_number", 1, 0)
        self._field(section, "Current Odometer (km) *", "current_odometer", 1, 1)
        self._field(section, "Fuel Type *", "fuel_type", 2, 0, FUEL_TYPES, True,
                    "Petrol" if self.vehicle_kind == "Bike" else "Diesel")
        self._field(section, "Seating Capacity *", "seating_capacity", 2, 1,
                    default="2" if self.vehicle_kind == "Bike" else "30")
        self._field(section, "Engine Capacity (CC)", "engine_capacity_cc", 3, 0)
        self._field(section, "Transmission Type", "transmission_type", 3, 1,
                    TRANSMISSIONS, True, "Manual" if self.vehicle_kind == "Bike" else "Automatic")
        self._field(section, "Air Conditioning", "air_conditioning", 4, 1,
                    ("Yes", "No"), True, "No" if self.vehicle_kind == "Bike" else "Yes")

    def _build_operations(self):
        section = self._section(self.content_frame, "Operational Information", 1, 1)
        self.sections["Operational Information"] = section
        section.grid_columnconfigure((1, 3), weight=1)
        self._field(section, "Ownership Type *", "ownership_type", 0, 0,
                    ("Company Owned", "Rented In", "Leased"), True, "Company Owned")
        self._field(section, "Assigned Route", "assigned_route", 0, 1, self._routes())
        self._field(section, "Vehicle Status *", "status", 1, 0,
                    ("Active", "Under Repair", "Inactive"), True, "Active")
        self._field(section, "Department *", "department", 1, 1, self._departments())
        self._field(section, "Assigned Driver", "assigned_driver", 2, 0, self._drivers())
        self._field(section, "Remarks", "remarks", 3, 0)

    def _build_documents(self):
        dates = self._section(self.content_frame, "Mulkiya (Registration Card)", 0, 2)
        dates.grid(columnspan=2, sticky="ew")
        dates.grid_columnconfigure((1, 3), weight=1)
        self.sections["Documents & Others"] = dates
        self._date_field(dates, "Mulkiya Issue Date *", "mulkiya_issue_date", 0, 0, date.today())
        self._date_field(dates, "Mulkiya Expiry Date *", "mulkiya_expiry_date", 0, 1,
                         date.today() + timedelta(days=364))
        self.expiry_notice = tk.Label(dates, text="", bg="#e1f4e7", fg="#18703a",
                                      font=("Segoe UI", 9, "bold"), padx=12, pady=7)
        self.expiry_notice.grid(row=0, column=4, padx=10, sticky="e")
        self.fields["mulkiya_issue_date"].bind("<FocusOut>", self._update_expiry)
        self.fields["mulkiya_expiry_date"].bind("<FocusOut>", self._update_expiry_notice)
        self._update_expiry_notice()

    def _date_field(self, parent, label, name, row, column, initial_date):
        tk.Label(parent, text=label, bg="#f8fafc", fg="#18365d",
                 font=("Segoe UI", 9)).grid(row=row, column=column * 2, sticky="w", padx=(4, 8), pady=7)
        widget = DateEntry(parent, date_pattern="dd-mm-yyyy", width=17)
        widget.set_date(initial_date)
        widget.grid(row=row, column=column * 2 + 1, sticky="ew", padx=(0, 12), pady=5)
        self.fields[name] = widget
        return widget

    def _document_row(self, parent, row, key, title, images_only):
        line = tk.Frame(parent, bg="#f8fafc")
        line.grid(row=row, column=1, sticky="ew", padx=(8, 2), pady=4)
        line.grid_columnconfigure(0, weight=1)
        label = tk.Label(line, text=f"{title}   ○", bg="#f8fafc", fg="#18365d",
                         font=("Segoe UI", 9, "bold"), anchor="w")
        label.grid(row=0, column=0, sticky="ew")
        self.document_labels[key] = label
        self.document_titles[key] = title
        ttk.Button(
            line,
            text="Upload",
            command=lambda k=key, t=title, i=images_only: self._choose_document(k, t, i),
        ).grid(row=0, column=1, padx=(4, 0))

    def _brands(self):
        try:
            rows = self.connection.execute(
                "SELECT id, brand_name FROM vehicle_brands ORDER BY brand_name"
            ).fetchall()
            self.brand_ids = {name: brand_id for brand_id, name in rows}
            return tuple(self.brand_ids)
        except sqlite3.OperationalError:
            self.brand_ids = {}
            return ()

    def _load_models(self, event=None):
        brand_id = self.brand_ids.get(self.fields["brand"].get())
        models = ()
        if brand_id is not None:
            try:
                rows = self.connection.execute(
                    "SELECT model_name FROM vehicle_models WHERE brand_id = ? ORDER BY model_name",
                    (brand_id,),
                ).fetchall()
                models = tuple(row[0] for row in rows)
            except sqlite3.OperationalError:
                models = ()
        self.fields["model"].configure(values=models)
        self.fields["model"].set("")

    def _drivers(self):
        try:
            rows = self.connection.execute(
                """
                SELECT employee_id, name FROM employees
                WHERE lower(role) LIKE '%driver%' AND lower(status) = 'active'
                ORDER BY name
                """
            ).fetchall()
            return tuple(f"DRV-{employee_id:04d} - {name}" for employee_id, name in rows)
        except sqlite3.OperationalError:
            return ()

    def _routes(self):
        return ()

    def _departments(self):
        return ()

    def _next_registration_id(self):
        row = self.connection.execute("SELECT COALESCE(MAX(id), 0) + 1 FROM vehicles").fetchone()
        return f"{VEHICLE_ID_PREFIX[self.vehicle_kind]}-{row[0]:06d}"

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

    def _update_plate_indicator(self, event=None):
        plate_number = self.fields["plate_number"].get().strip()
        valid = plate_number.isdigit() and len(plate_number) <= 5
        self.plate_indicator.configure(
            text="✓" if valid else "○",
            fg="#16803c" if valid else "#94a3b8",
        )

    def _kind_changed(self, vehicle_kind):
        self.vehicle_kind = vehicle_kind
        self.kind_var.set(vehicle_kind)
        self.breadcrumb_label.configure(text=f"VEHICLE MANAGEMENT   ›   ADD NEW {vehicle_kind.upper()}")
        self.title_label.configure(text=f"{vehicle_kind} Registration")
        self.subtitle_label.configure(text=f"Register and manage {vehicle_kind.lower()} vehicle details")
        self.vehicle_icon_label.configure(text="🏍" if vehicle_kind == "Bike" else "🚌")
        for kind, button in self.kind_buttons.items():
            active = kind == vehicle_kind
            button.configure(bg="#0759b8" if active else "#f8fafc",
                             fg="white" if active else "#102f59")
        self.fields["registration_id"].configure(state="normal")
        self.fields["registration_id"].delete(0, tk.END)
        self.fields["registration_id"].insert(0, self._next_registration_id())
        self.fields["registration_id"].configure(state="readonly")
        self.fields["seating_capacity"].delete(0, tk.END)
        self.fields["seating_capacity"].insert(0, "2" if vehicle_kind == "Bike" else "30")
        self.fields["fuel_type"].set("Petrol" if vehicle_kind == "Bike" else "Diesel")
        self.fields["transmission_type"].set(
            "Manual" if vehicle_kind == "Bike" else "Automatic"
        )
        self.fields["air_conditioning"].set("No" if vehicle_kind == "Bike" else "Yes")

    def _update_expiry(self, event=None):
        try:
            issue_date = self.fields["mulkiya_issue_date"].get_date()
        except ValueError:
            return
        self.fields["mulkiya_expiry_date"].set_date(issue_date + timedelta(days=364))
        self._update_expiry_notice()

    def _update_expiry_notice(self, event=None):
        try:
            expiry = self.fields["mulkiya_expiry_date"].get_date()
        except ValueError:
            self.expiry_notice.configure(text="Select an expiry date", bg="#fef3c7", fg="#92400e")
            return
        days_remaining = (expiry - date.today()).days
        if days_remaining < 0:
            self.expiry_notice.configure(
                text=f"Expired {abs(days_remaining)} days ago",
                bg="#fee2e2",
                fg="#b42318",
            )
        else:
            self.expiry_notice.configure(
                text=f"Expiry in {days_remaining} days",
                bg="#e1f4e7",
                fg="#18703a",
            )

    def _choose_document(self, key, title, images_only=False):
        filetypes = [("Images", "*.jpg *.jpeg *.png *.webp")] if images_only else [
            ("Documents", "*.pdf *.jpg *.jpeg *.png"),
            ("All files", "*.*"),
        ]
        path = filedialog.askopenfilename(title=f"Select {title}", filetypes=filetypes)
        if not path:
            return
        if key == "vehicle_photo":
            try:
                with Image.open(path) as source:
                    image = source.copy()
            except OSError as error:
                messagebox.showerror("Could not open photo", str(error), parent=self.frame)
                return
            image.thumbnail((360, 190))
            self.vehicle_photo = ImageTk.PhotoImage(image)
            self.preview_label.configure(image=self.vehicle_photo, text="")
            self.documents[key] = path
        else:
            self.documents[key] = path
        self.document_labels[key].configure(text=f"{title}   ✓", fg="#16733c")

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
        values["mulkiya_issue_date"] = self.fields["mulkiya_issue_date"].get_date().isoformat()
        values["mulkiya_expiry_date"] = self.fields["mulkiya_expiry_date"].get_date().isoformat()
        values["vehicle_kind"] = self.vehicle_kind
        values.update(self.documents)
        return values

    def save(self):
        try:
            values = self._collect_values()
        except ValueError:
            self._focus_section("Documents & Others")
            messagebox.showwarning(
                "Invalid registration dates",
                "Choose valid mulkiya issue and expiry dates.",
                parent=self.frame,
            )
            return
        required = ("plate_source", "plate_code", "plate_number", "brand", "model", "year",
                    "colour", "engine_number", "chassis_number", "fuel_type", "current_odometer",
                    "seating_capacity", "ownership_type", "status", "department",
                    "mulkiya_issue_date", "mulkiya_expiry_date")
        missing = [field.replace("_", " ").title() for field in required if not values[field]]
        if missing:
            registration_fields = {
                "Plate Source", "Plate Code", "Plate Number", "Brand", "Model", "Year", "Colour"
            }
            self._focus_section(
                "Registration Details" if missing[0] in registration_fields
                else "Operational Information" if missing[0] in {"Department"}
                else "Technical Specifications"
            )
            messagebox.showwarning("Missing information", "Complete required fields: " + ", ".join(missing), parent=self.frame)
            return
        if not values["plate_number"].isdigit() or len(values["plate_number"]) > 5:
            self._focus_section("Registration Details")
            messagebox.showwarning("Invalid plate number", "Enter a plate number with up to five digits.", parent=self.frame)
            return
        try:
            issue = date.fromisoformat(values["mulkiya_issue_date"])
            expiry = date.fromisoformat(values["mulkiya_expiry_date"])
            if expiry <= issue:
                raise ValueError
        except ValueError:
            self._focus_section("Documents & Others")
            messagebox.showwarning(
                "Invalid registration dates",
                "Enter valid dates (YYYY-MM-DD) and make sure expiry is after issue date.",
                parent=self.frame,
            )
            return
        try:
            for name in ("engine_capacity_cc", "current_odometer", "seating_capacity"):
                if values[name] and (not values[name].isdigit() or int(values[name]) < 0):
                    raise ValueError
            if values["tank_capacity"]:
                tank_capacity = float(values["tank_capacity"])
                if not isfinite(tank_capacity) or tank_capacity < 0:
                    raise ValueError
        except ValueError:
            self._focus_section("Technical Specifications")
            messagebox.showwarning(
                "Invalid technical details",
                "Enter non-negative whole numbers for engine capacity, odometer and seating; tank capacity must be a non-negative number.",
                parent=self.frame,
            )
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
            elif name == "mulkiya_issue_date":
                widget.set_date(date.today())
            elif name == "mulkiya_expiry_date":
                widget.set_date(date.today() + timedelta(days=364))
            elif isinstance(widget, ttk.Combobox):
                widget.set("")
            else:
                widget.delete(0, tk.END)
        self.fields["year"].set(str(date.today().year))
        self.fields["fuel_type"].set("Petrol" if self.vehicle_kind == "Bike" else "Diesel")
        self.fields["ownership_type"].set("Company Owned")
        self.fields["status"].set("Active")
        self.fields["transmission_type"].set(
            "Manual" if self.vehicle_kind == "Bike" else "Automatic"
        )
        self.fields["air_conditioning"].set("No" if self.vehicle_kind == "Bike" else "Yes")
        self.fields["seating_capacity"].insert(0, "2" if self.vehicle_kind == "Bike" else "30")
        self.documents.clear()
        for key, label in self.document_labels.items():
            label.configure(text=f"{self.document_titles[key]}   ○", fg="#18365d")
        self.preview_label.configure(image="", text="Vehicle photo preview")
        self._update_plate_indicator()
        self._update_expiry_notice()
        self.status_label.configure(text="")

    def new_form(self):
        self.reset_form()
        self._focus_section("Registration Details")

    def open_insurance(self):
        self._close_connection()
        self.controller.open_vehicleins_page()

    def close(self):
        self._close_connection()
        self.frame.destroy()
        self.controller.set_form_mode(False)
        self.controller.show_vehicle()

    def _on_destroy(self, event):
        if event.widget is self.frame:
            self._close_connection()

    def _close_connection(self):
        if not self.connection_closed:
            self.connection.close()
            self.connection_closed = True
