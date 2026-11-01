import re
import sqlite3
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

from config import DATABASE_PATH
from admin_password_page import AdminPasswordPage

MOBILE_CODES = ["050", "052", "054", "055", "056", "058"]
LANDLINE_CODES = ["02", "03", "04", "06", "07", "09"]


class CompanyProfilePage:

    def __init__(self, parent):
        self.frame = tk.Frame(parent, bg="white")
        self.frame.pack(fill="both", expand=True)
        form = tk.Frame(self.frame, bg="white")
        form.pack(pady=20)

        self.name_var = tk.StringVar()
        self.email_var = tk.StringVar()
        self.phone_type_var = tk.StringVar(value="Mobile")
        self.code_var = tk.StringVar()
        self.number_var = tk.StringVar()
        self.logo_var = tk.StringVar()

        tk.Label(form, text="Company Name", anchor="e", width=15, bg="white").grid(row=0, column=0, padx=10, pady=5)
        tk.Entry(form, textvariable=self.name_var, width=30).grid(row=0, column=1, padx=10, pady=5, sticky="w")

        tk.Label(form, text="Address", anchor="e", width=15, bg="white").grid(row=1, column=0, padx=10, pady=5)
        self.address_text = tk.Text(form, width=30, height=2)
        self.address_text.grid(row=1, column=1, padx=10, pady=5, sticky="w")

        tk.Label(form, text="Email", anchor="e", width=15, bg="white").grid(row=2, column=0, padx=10, pady=5)
        tk.Entry(form, textvariable=self.email_var, width=30).grid(row=2, column=1, padx=10, pady=5, sticky="w")

        tk.Label(form, text="Phone Type", anchor="e", width=15, bg="white").grid(row=3, column=0, padx=10, pady=5)
        type_combo = ttk.Combobox(form, textvariable=self.phone_type_var, values=["Mobile", "Landline"], state="readonly")
        type_combo.grid(row=3, column=1, padx=10, pady=5, sticky="w")
        type_combo.bind("<<ComboboxSelected>>", self.update_code_list)

        tk.Label(form, text="Phone", anchor="e", width=15, bg="white").grid(row=4, column=0, padx=10, pady=5)
        phone_frame = tk.Frame(form, bg="white")
        phone_frame.grid(row=4, column=1, sticky="w", padx=10)
        tk.Label(phone_frame, text="+971", bg="white").pack(side="left")
        self.code_combo = ttk.Combobox(phone_frame, textvariable=self.code_var, width=6, state="readonly")
        self.code_combo.pack(side="left", padx=5)
        vcmd = (form.register(self.validate_number), "%P")
        tk.Entry(phone_frame, textvariable=self.number_var, width=15,
                 validate="key", validatecommand=vcmd).pack(side="left")

        tk.Label(form, text="Logo", anchor="e", width=15, bg="white").grid(row=5, column=0, padx=10, pady=5)
        tk.Entry(form, textvariable=self.logo_var, width=35, state="readonly").grid(row=5, column=1, padx=10, pady=5, sticky="w")
        tk.Button(form, text="Browse LOGO", command=self.browse_logo).grid(row=6, column=1, padx=10, pady=15, sticky="w")
        tk.Button(form, text="Save", width=20, command=self.save_company).grid(row=6, column=1, padx=(150, 10), pady=15, sticky="w")

        self.update_code_list()
        self.load_company()

    @staticmethod
    def validate_number(value):
        return value == "" or (value.isdigit() and len(value) <= 7)

    def update_code_list(self, event=None):
        self.code_combo["values"] = MOBILE_CODES if self.phone_type_var.get() == "Mobile" else LANDLINE_CODES
        self.code_var.set("")

    def browse_logo(self):
        path = filedialog.askopenfilename(filetypes=[("JPG Files", "*.jpg *.jpeg")])
        if path:
            self.logo_var.set(path)

    def save_company(self):
        name = self.name_var.get().strip()
        email = self.email_var.get().strip()
        number = self.number_var.get().strip()
        code = self.code_var.get().strip()
        address = self.address_text.get("1.0", tk.END).strip()
        logo = self.logo_var.get()

        if not name:
            messagebox.showerror("Error", "Company Name required")
            return
        if not re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", email):
            messagebox.showerror("Error", "Invalid email format")
            return
        if not code or not number:
            messagebox.showerror("Error", "Phone Number Incomplete")
            return
        if len(number) != 7:
            messagebox.showerror("Error", "Phone must be 7 digits")
            return

        phone = "+971" + code.lstrip("0") + number
        with sqlite3.connect(DATABASE_PATH) as conn:
            if conn.execute("SELECT id FROM company WHERE id = 1").fetchone():
                conn.execute("UPDATE company SET name=?, address=?, email=?, phone=?, logo=? WHERE id=1",
                             (name, address, email, phone, logo))
            else:
                conn.execute("INSERT INTO company (id, name, address, email, phone, logo) VALUES (1, ?, ?, ?, ?, ?)",
                             (name, address, email, phone, logo))
        messagebox.showinfo("Success", "Saved successfully")

    def load_company(self):
        with sqlite3.connect(DATABASE_PATH) as conn:
            row = conn.execute("SELECT name, address, email, phone, logo FROM company WHERE id = 1").fetchone()
        if not row:
            return
        self.name_var.set(row[0] or "")
        self.address_text.insert("1.0", row[1] or "")
        self.email_var.set(row[2] or "")
        phone = (row[3] or "").replace("+971", "")
        if phone:
            code = "0" + phone[:2] if len(phone) == 9 else "0" + phone[:1]
            self.phone_type_var.set("Mobile" if code in MOBILE_CODES else "Landline")
            self.update_code_list()
            self.code_var.set(code)
            self.number_var.set(phone[len(code) - 1:])
        self.logo_var.set(row[4] or "")


class AdminSettingsPage:
    TABS = [("Company Profile", CompanyProfilePage),
            ("Set/Change Admin Password", AdminPasswordPage)]

    def __init__(self, parent):
        self.tab_buttons = []
        self.current = None

        tab_bar = tk.Frame(parent, bg="#1f2937", width=220)
        tab_bar.pack(side="left", fill="y")
        tab_bar.pack_propagate(False)
        self.body = tk.Frame(parent, bg="white")
        self.body.pack(side="left", fill="both", expand=True)

        for index, (text, _page) in enumerate(self.TABS):
            button = tk.Button(tab_bar, text=text, fg="white", bg="#374151", activebackground="#4b5563",
                               relief="flat", padx=10, pady=10, command=lambda i=index: self.show_tab(i))
            button.pack(fill="x", padx=10, pady=(10 if index == 0 else 5, 5))
            self.tab_buttons.append(button)
        self.show_tab(0)

    def show_tab(self, index):
        for widget in self.body.winfo_children():
            widget.destroy()
        for i, button in enumerate(self.tab_buttons):
            button.config(bg="#1c0bdf" if i == index else "#374151")
        self.TABS[index][1](self.body)
