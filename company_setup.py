import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import sqlite3
import re

from header import create_header

DB_PATH = r"D:\FTMS PRO\Ftms.db"
unsaved_changes=False

# ---------------- VALIDATIONS ----------------
def mark_unsaved(event=None):
    global unsaved_changes
    unsaved_changes=True

def validate_number(P):
    if P.isdigit() and len(P) <= 7:
        return True
    if P == "":
        return True
    return False

def validate_email(email):
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email)

# ---------------- PHONE TYPE ----------------

def update_code_list(event=None):
    if phone_type.get() == "Mobile":
        code_combo['values'] = ["050","052","054","055","056","058"]
    else:
        code_combo['values'] = ["02","03","04","06","07","09"]
    code_var.set("")

# ---------------- LOGO ----------------

def browse_logo():
    file_path = filedialog.askopenfilename(
        filetypes=[("JPG Files", "*.jpg *.jpeg")]
    )
    if file_path:
        logo_var.set(file_path)
    save_btn.config(state="active")

# ---------------- SAVE ----------------

def save_company():
    name = name_var.get().strip()
    email = email_var.get().strip()
    number = number_var.get().strip()
    code = code_var.get().strip()
    address = address_text.get("1.0", tk.END).strip()
    logo = logo_var.get()

    if not name:
        messagebox.showerror("Error", "Company Name required")
        return

    if not validate_email(email):
        messagebox.showerror("Error", "Invalid email format")
        return

    if not code or not number:
        messagebox.showerror("Error", "Phone Number Incomplete")
        return

    if len(number) != 7:
        messagebox.showerror("Error", "Phone must be 7 digits")
        return

    code_clean = code.lstrip("0")
    phone = "+971" + code_clean + number

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM company WHERE id = 1")
    row = cursor.fetchone()

    if row:
        cursor.execute("""
            UPDATE company
            SET name=?, address=?, email=?, phone=?, logo=?
            WHERE id=1
        """, (name, address, email, phone, logo))
    else:
        cursor.execute("""
            INSERT INTO company (id, name, address, email, phone, logo)
            VALUES (1, ?, ?, ?, ?, ?)
        """, (name, address, email, phone, logo))

    conn.commit()
    conn.close()

    messagebox.showinfo("Success", "Saved successfully")

# ---------------- LOAD ----------------

def load_company():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT name, address, email, phone, logo
        FROM company WHERE id = 1
    """)
    row = cursor.fetchone()
    conn.close()

    if row:
        name_var.set(row[0])
        address_text.insert("1.0", row[1])
        email_var.set(row[2])

        phone = row[3].replace("+971", "")

        if len(phone) == 9:
            code = "0" + phone[:2]
            number = phone[2:]
        else:
            code = "0" + phone[:1]
            number = phone[1:]

        code_var.set(code)
        number_var.set(number)
        logo_var.set(row[4])

# ---------------- UI ----------------

root = tk.Tk()
root.title("FTMS PRO")
root.geometry("750x500")

# HEADER
create_header(root)

frame = tk.Frame(root)
frame.pack(pady=20)
frame.grid_columnconfigure(0, minsize=150)
frame.grid_columnconfigure(1, minsize=300)

# Company Name
tk.Label(frame, text="Company Name", anchor="e", width=15).grid(row=0, column=0, padx=10, pady=5)
name_var = tk.StringVar()
tk.Entry(frame, textvariable=name_var, width=30).grid(row=0, column=1, padx=10, pady=5,sticky="w")


# Address
tk.Label(frame, text="Address",anchor="e",width=15).grid(row=1, column=0,padx=10, pady=5)
address_text = tk.Text(frame, width=30, height=2)
address_text.grid(row=1, column=1, padx=10, pady=5, sticky="w")

# Email
tk.Label(frame, text="Email", anchor="e", width=15).grid(row=2, column=0, padx=10, pady=5)
email_var = tk.StringVar()
tk.Entry(frame, textvariable=email_var, width=30).grid(row=2, column=1, padx=10, pady=5,sticky="w")

# Phone Type
tk.Label(frame, text="Phone Type", anchor="e", width=15).grid(row=4, column=0, padx=10, pady=5)
phone_type = ttk.Combobox(frame, values=["Mobile","Landline"], state="readonly")
phone_type.grid(row=4, column=1, padx=(10,5), pady=5, sticky="w")
phone_type.bind("<<ComboboxSelected>>", update_code_list)

# Phone
tk.Label(frame, text="Phone",anchor="e",width=15).grid(row=5, column=0, padx=10, pady=5)

phone_frame = tk.Frame(frame)
phone_frame.grid(row=5, column=1, sticky="w")

tk.Label(phone_frame, text="+971").pack(side="left")

code_var = tk.StringVar()
code_combo = ttk.Combobox(phone_frame, textvariable=code_var, width=6, state="readonly")
code_combo.pack(side="left", padx=5)

vcmd = (root.register(validate_number), '%P')

number_var = tk.StringVar()
tk.Entry(phone_frame, textvariable=number_var, width=15,
         validate="key", validatecommand=vcmd).pack(side="left")

# Logo
tk.Label(frame, text="Logo", anchor="e", width=15).grid(row=6, column=0, padx=10, pady=5)
logo_var = tk.StringVar()
tk.Entry(frame, textvariable=logo_var, width=35,state="readonly").grid(row=6, column=1, padx=10, pady=5, sticky="w")
tk.Button(frame, text="Browse LOGO", command=browse_logo).grid(row=9, column=1, padx=(10,5), pady=20,sticky="w")

# Save
save_btn=tk.Button(frame, text="Save", width=20,command=save_company, stat="disabled")
save_btn.grid(row=9, column=1, padx=(150,10), pady=20, sticky="w")

# Default setup
phone_type.set("Mobile")
update_code_list()
load_company()
root.mainloop()