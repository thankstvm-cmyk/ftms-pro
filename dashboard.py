import sqlite3
import tkinter as tk
from datetime import date, datetime, timedelta
from tkinter import ttk

from angel.angelchat import AngelChat
from angel.ftmsangel import Angel
from company_manager import get_company_details, show_company_logo
from config import DATABASE_PATH
from dashboard_summary import DashboardSummary
from vehicle_report import VehicleReportPage


class Dashboard(ttk.Frame):
    """The original FleetPro dashboard layout, enhanced with read-only live intelligence."""

    def __init__(self, parent):
        super().__init__(parent, padding=0)
        self.pack(fill="both", expand=True)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)  # HEADER
        self.grid_rowconfigure(1, weight=3)  # STATISTICS
        self.grid_rowconfigure(2, weight=2)  # RECENT ACTIVITIES
        self.grid_rowconfigure(3, weight=0)  # FOOTER
        self.summary = DashboardSummary()
        self.vehicle = self.summary.get_vehicle_summary()
        self._refresh_job = None
        self.angel_chat = None

        self.create_header()
        self.statistics()
        self.recent_activities()
        self.footer()
        self.dashboard_menu = tk.Menu(self, tearoff=0)
        self.dashboard_menu.add_command(label="Activate Angel", command=self.open_angel)
        self.bind_all("<Button-3>", self.show_dashboard_menu)
        self.angel = Angel(self, DATABASE_PATH)  # FTMS Smart Angel stays available as before.
        self.update_datetime()
        self.refresh_dashboard()

    # ========================================================== HEADER (original layout)
    def create_header(self):
        self.header_frame = ttk.LabelFrame(self)
        self.header_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=2)
        self.header_frame.columnconfigure(0, weight=2)
        self.header_frame.columnconfigure(1, weight=4)
        self.header_frame.columnconfigure(2, weight=4)
        self.header_frame.columnconfigure(3, weight=3)
        self.header_frame.columnconfigure(4, weight=2)

        company_name, _logo_path = get_company_details()
        self.logo_frame = ttk.LabelFrame(self.header_frame)
        self.logo_frame.grid(row=0, column=0, padx=5, pady=0, sticky="nsew")
        self.logo_canvas = tk.Canvas(self.logo_frame, width=100, height=60, highlightthickness=0)
        self.logo_canvas.pack(fill="both", expand=True)
        show_company_logo(self.logo_canvas, 100, 60)

        self.company_frame = ttk.LabelFrame(self.header_frame)
        self.company_frame.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")
        ttk.Label(self.company_frame, text=company_name, font=("Calibri", 12, "bold")).pack(anchor="w")
        ttk.Label(self.company_frame, text="Dubai").pack(anchor="w")

        self.title_frame = ttk.LabelFrame(self.header_frame)
        self.title_frame.grid(row=0, column=2, padx=5, pady=5, sticky="nsew")
        ttk.Label(self.title_frame, text="LOGISTICS DASHBOARD", font=("Calibri", 16, "bold")).pack(expand=True)

        self.system_frame = ttk.LabelFrame(self.header_frame)
        self.system_frame.grid(row=0, column=3, sticky="nsew", padx=5, pady=5)
        self.date_lbl = ttk.Label(self.system_frame, font=("Calibri", 10))
        self.date_lbl.pack(anchor="w", padx=10, pady=(5, 0))
        self.time_lbl = ttk.Label(self.system_frame, font=("Calibri", 10))
        self.time_lbl.pack(anchor="w", padx=10)
        ttk.Label(self.system_frame, text="User :Admin", font=("Calibri", 10)).pack(anchor="w", padx=10, pady=(0, 5))

        self.refresh_frame = ttk.LabelFrame(self.header_frame)
        self.refresh_frame.grid(row=0, column=4, sticky="nsew", padx=5, pady=5)
        ttk.Button(self.refresh_frame, text="Refresh", command=self.refresh_dashboard).pack(expand=True, fill="x", padx=5, pady=5)

    # ========================================================== STATISTICS (original four cards)
    def statistics(self):
        self.statistics_frame = ttk.Frame(self)
        self.statistics_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        for column in range(4):
            self.statistics_frame.columnconfigure(column, weight=1)
        self.statistics_frame.rowconfigure(0, weight=1)

        self.operational_card = ttk.LabelFrame(self.statistics_frame, text="Operational Summary")
        self.fleet_card = ttk.LabelFrame(self.statistics_frame, text="Fleet Details")
        self.route_card = ttk.LabelFrame(self.statistics_frame, text="Route Summary")
        self.maintenance_card = ttk.LabelFrame(self.statistics_frame, text="Maintenance Statistics")
        for column, card in enumerate((self.operational_card, self.fleet_card, self.route_card, self.maintenance_card)):
            card.grid(row=0, column=column, sticky="nsew", padx=5, pady=5)

    def clear_frame(self, frame):
        for widget in frame.winfo_children():
            widget.destroy()

    def line(self, parent, text, colour="black", command=None, bold=False):
        label = tk.Label(parent, text=text, fg=colour, cursor="hand2" if command else "",
                         font=("Calibri", 10, "bold" if bold else "normal"), anchor="w", justify="left", wraplength=240)
        label.pack(anchor="w", padx=10, pady=3)
        if command:
            label.bind("<Button-1>", lambda _event, action=command: action())
        return label

    def populate_statistics(self, data):
        # Operational Summary — same card, live operational status and alerts.
        self.clear_frame(self.operational_card)
        self.line(self.operational_card, "Live Operational Status", bold=True)
        self.line(self.operational_card, f"Active Vehicles : {data['active']}  (View)", "blue",
                  lambda: self.open_status_report("Active"), True)
        self.line(self.operational_card, f"Under Repair : {data['repair']}  (View)",
                  "red" if data["repair"] else "green", lambda: self.open_status_report("Under Repair"))
        self.line(self.operational_card, f"Fleet Availability : {data['availability']}%")
        if data["open_breakdowns"] or data["open_accidents"]:
            self.line(self.operational_card,
                      f"ALERT: {data['open_breakdowns']} breakdown(s), {data['open_accidents']} accident(s) open",
                      "red", self.open_incident_report, True)
        else:
            self.line(self.operational_card, "No open incident records", "green")

        # Fleet Details — same original content, supplied by the current database.
        self.clear_frame(self.fleet_card)
        self.line(self.fleet_card, "Fleet Details", bold=True)
        self.line(self.fleet_card, f"ðŸšš Total Vehicles : {data['total']}  (View)", "blue",
                  lambda: self.open_vehicle_report("ALL"), True)
        largest_name, largest_count = self.vehicle["largest_fleet"]
        largest_text = f"{largest_name:g} Ton Vehicles" if isinstance(largest_name, (int, float)) else f"{largest_name} Ton Vehicles"
        self.line(self.fleet_card, f"Largest Category : {largest_text} ({largest_count})")
        for name, count in self.vehicle["fleet_summary"]:
            self.create_dashboard_link(self.fleet_card, f"{name:g} Ton Vehicles", count,
                                       lambda _event, ton=name: self.open_vehicle_report(ton))
        self.line(self.fleet_card, "View Complete Fleet Details...", "blue", lambda: self.open_vehicle_report("ALL"))

        # Route Summary — retains the original frame and provides currently available live dispatch signals.
        self.clear_frame(self.route_card)
        self.line(self.route_card, "Route Summary", bold=True)
        self.line(self.route_card, f"Active Delivery Team : {data['active_drivers']}")
        self.line(self.route_card, f"Total Drivers : {data['drivers']}")
        self.line(self.route_card, f"Today's Fuel Entries : {data['today_fuel']}")
        self.line(self.route_card, f"Today's Odometer Entries : {data['today_odometer']}")
        self.line(self.route_card, "Decision: assign only active, compliant vehicles to dispatch.", "#1e3a5f")

        # Maintenance Statistics — retains its original frame and focuses the manager on risk.
        self.clear_frame(self.maintenance_card)
        self.line(self.maintenance_card, "Maintenance Statistics", bold=True)
        self.line(self.maintenance_card, f"Total Available Vehicles : {data['active']}", "blue",
                  lambda: self.open_status_report("Active"))
        self.line(self.maintenance_card, f"Registration Expired : {data['doc_expired']}  (View)",
                  "red" if data["doc_expired"] else "green",
                  lambda: self.open_date_report(date(1900, 1, 1), data["today"] - timedelta(days=1), "Expired registrations"))
        self.line(self.maintenance_card, f"Registration Due in 30 Days : {data['doc_due']}  (View)",
                  "#cc7a00" if data["doc_due"] else "green",
                  lambda: self.open_date_report(data["today"], data["end_30"], "Registrations due within 30 days"))
        self.line(self.maintenance_card, f"Insurance Due / Expired : {data['insurance_due'] + data['insurance_expired']}",
                  "red" if data["insurance_expired"] else ("#cc7a00" if data["insurance_due"] else "green"),
                  self.open_insurance_notice)
        recommendation = "Prioritise repair release before the next dispatch." if data["repair"] else "Fleet maintenance status is stable."
        self.line(self.maintenance_card, recommendation, "#1e3a5f")

    # ========================================================== RECENT ACTIVITIES (original frame)
    def recent_activities(self):
        self.activities_frame = ttk.LabelFrame(self, text="Recent Activities")
        self.activities_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=5)

    def populate_recent_activities(self, data):
        self.clear_frame(self.activities_frame)
        alerts = []
        if data["doc_expired"]:
            alerts.append((f"CRITICAL • {data['doc_expired']} vehicle registration(s) have expired — review immediately.", "red",
                           lambda: self.open_date_report(date(1900, 1, 1), data["today"] - timedelta(days=1), "Expired registrations")))
        if data["insurance_expired"]:
            alerts.append((f"CRITICAL • {data['insurance_expired']} insurance policy/policies have expired.", "red", self.open_insurance_notice))
        if data["doc_due"] or data["insurance_due"]:
            alerts.append((f"ACTION • {data['doc_due'] + data['insurance_due']} compliance item(s) need renewal planning within 30 days.", "#cc7a00",
                           lambda: self.open_date_report(data["today"], data["end_30"], "30-day compliance horizon")))
        if data["repair"]:
            alerts.append((f"OPERATIONS • {data['repair']} vehicle(s) are under repair; confirm replacement capacity before dispatch.", "#cc7a00",
                           lambda: self.open_status_report("Under Repair")))
        if not alerts:
            alerts.append(("CLEAR • No immediate compliance or maintenance alerts. Fleet is ready for planned operations.", "green",
                           lambda: self.open_vehicle_report("ALL")))
        for text, colour, command in alerts[:3]:
            self.line(self.activities_frame, text + "  View report ›", colour, command, colour == "red")
        self.line(self.activities_frame,
                  f"Smart Angel recommendation: {data['availability']}% fleet availability. "
                  "Use right-click → Activate Angel for guidance on the selected FTMS module.", "#1e3a5f")

    # ========================================================== LIVE DATA (read-only)
    def get_live_data(self):
        today = date.today()
        end_30 = today + timedelta(days=30)
        with sqlite3.connect(DATABASE_PATH) as conn:
            cursor = conn.cursor()
            def count(sql, parameters=()):
                cursor.execute(sql, parameters)
                return cursor.fetchone()[0]
            total = count("SELECT COUNT(*) FROM vehicles")
            active = count("SELECT COUNT(*) FROM vehicles WHERE LOWER(COALESCE(status, '')) = 'active'")
            repair = count("SELECT COUNT(*) FROM vehicles WHERE LOWER(COALESCE(status, '')) LIKE '%repair%'")
            drivers = count("SELECT COUNT(*) FROM employees")
            active_drivers = count("SELECT COUNT(*) FROM employees WHERE LOWER(COALESCE(status, '')) = 'active'")
            today_fuel = count("SELECT COUNT(*) FROM fuel_entries WHERE DATE(date) = DATE(?)", (today.isoformat(),))
            today_odometer = count("SELECT COUNT(*) FROM odometer_entries WHERE DATE(date) = DATE(?)", (today.isoformat(),))
            doc_expired = count("SELECT COUNT(*) FROM vehicles WHERE DATE(mulkiya_expiry_date) < DATE(?)", (today.isoformat(),))
            doc_due = count("SELECT COUNT(*) FROM vehicles WHERE DATE(mulkiya_expiry_date) BETWEEN DATE(?) AND DATE(?)", (today.isoformat(), end_30.isoformat()))
            insurance_expired = count("SELECT COUNT(*) FROM vehicle_insurance WHERE DATE(expiry_date) < DATE(?)", (today.isoformat(),))
            insurance_due = count("SELECT COUNT(*) FROM vehicle_insurance WHERE DATE(expiry_date) BETWEEN DATE(?) AND DATE(?)", (today.isoformat(), end_30.isoformat()))
            open_breakdowns = count("SELECT COUNT(*) FROM breakdowns WHERE LOWER(COALESCE(status, 'open')) NOT IN ('closed', 'resolved', 'completed')")
            open_accidents = count("SELECT COUNT(*) FROM accidents WHERE LOWER(COALESCE(status, 'open')) NOT IN ('closed', 'resolved', 'completed')")
        return {"today": today, "end_30": end_30, "total": total, "active": active, "repair": repair,
                "availability": round(active / total * 100, 1) if total else 0, "drivers": drivers,
                "active_drivers": active_drivers, "today_fuel": today_fuel, "today_odometer": today_odometer,
                "doc_expired": doc_expired, "doc_due": doc_due, "insurance_expired": insurance_expired,
                "insurance_due": insurance_due, "open_breakdowns": open_breakdowns, "open_accidents": open_accidents}

    def refresh_dashboard(self):
        self.vehicle = self.summary.get_vehicle_summary()
        data = self.get_live_data()
        self.populate_statistics(data)
        self.populate_recent_activities(data)
        if self._refresh_job:
            self.after_cancel(self._refresh_job)
        self._refresh_job = self.after(60000, self.refresh_dashboard)

    # ========================================================== DRILL-DOWNS
    def create_dashboard_link(self, parent, title, value, callback):
        frame = tk.Frame(parent)
        frame.pack(anchor="w", padx=10, pady=2)
        tk.Label(frame, text=f"{title} :", width=15, anchor="w", font=("Calibri", 10)).grid(row=0, column=1, padx=(5, 5))
        link = tk.Label(frame, text=str(value), fg="blue", cursor="hand2", font=("Calibri", 10, "underline"))
        link.grid(row=0, column=2, sticky="w")
        link.bind("<Button-1>", callback)
        return link

    def open_vehicle_report(self, filter_value):
        report_window = tk.Toplevel(self)
        report_window.state("zoomed")
        report_window.transient(self)
        report_window.grab_set()
        report_window.focus_set()
        VehicleReportPage(report_window, self, filter_value)

    def open_status_report(self, status):
        report_window = tk.Toplevel(self)
        report_window.state("zoomed")
        report_window.transient(self)
        report_window.grab_set()
        page = VehicleReportPage(report_window, self, "ALL")
        criteria = [{"field": "status", "operator": "=", "value": status, "logic": ""}]
        page.load_data(criteria_list=criteria)
        page.update_count(page.build_where_clause(criteria))

    def open_date_report(self, start, end, title):
        report_window = tk.Toplevel(self)
        report_window.state("zoomed")
        report_window.transient(self)
        report_window.grab_set()
        page = VehicleReportPage(report_window, self, "ALL")
        page.field_var.set("mulkiya expiry date")
        page.load_data(date_range=("mulkiya_expiry_date", start.isoformat(), end.isoformat(), title))
        page.update_date_filter_summary(title)

    def open_incident_report(self):
        self.open_status_report("Under Repair")

    def open_insurance_notice(self):
        self.open_vehicle_report("ALL")

    # ========================================================== ORIGINAL ANGEL / FOOTER SUPPORT
    def footer(self):
        self.footer_frame = ttk.Frame(self)
        self.footer_frame.grid(row=3, column=0, sticky="ew", padx=10, pady=(0, 10))

    def update_datetime(self):
        now = datetime.now()
        self.date_lbl.config(text=f"Date : {now.strftime('%d-%b-%Y')}")
        self.time_lbl.config(text=f"Time : {now.strftime('%I:%M:%S %p')}")
        self.after(1000, self.update_datetime)

    def open_angel(self):
        if self.angel_chat is None or not self.angel_chat.winfo_exists():
            self.angel_chat = AngelChat(self.winfo_toplevel(), self.angel)
        else:
            self.angel_chat.lift()
            self.angel_chat.focus_force()

    def show_dashboard_menu(self, event):
        self.dashboard_menu.post(event.x_root, event.y_root)


if __name__ == "__main__":
    root = tk.Tk()
    root.title("FTMS FleetPro - Logistics Dashboard")
    root.geometry("1550x900")
    Dashboard(root)
    root.mainloop()
