
import tkinter as tk
from tkinter import messagebox
import sqlite3

def vehicle_management(content_frame):
    # Clear existing content
    for widget in content_frame.winfo_children():
        widget.destroy()

    tk.Label(content_frame, text="Add Vehicle", font=("Arial", 18)).pack(pady=10)

    tk.Label(content_frame, text="Vehicle Number").pack()
    vehicle_number = tk.Entry(content_frame)
    vehicle_number.pack()

    tk.Label(content_frame, text="Brand").pack()
    brand = tk.Entry(content_frame)
    brand.pack()

    tk.Label(content_frame, text="Model").pack()
    model = tk.Entry(content_frame)
    model.pack()

    tk.Label(content_frame, text="Year").pack()
    year = tk.Entry(content_frame)
    year.pack()

    tk.Label(content_frame, text="Status").pack()
    status = tk.Entry(content_frame)
    status.insert(0, "Active")
    status.pack()

    def save_vehicle():
        try:
            conn = sqlite3.connect("ftms.db")
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO vehicles (vehicle_number, brand, model, year, status)
                VALUES (?, ?, ?, ?, ?)
            """, (
                vehicle_number.get(),
                brand.get(),
                model.get(),
                year.get(),
                status.get()
            ))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Vehicle Added Successfully")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    tk.Button(content_frame, text="Save Vehicle", command=save_vehicle).pack(pady=10)
