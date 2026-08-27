import tkinter as tk
from PIL import Image, ImageTk
import sqlite3

DB_PATH = r"D:\FTMS PRO\Ftms.db"

def create_header(parent):

    header_frame = tk.Frame(parent, bg="#1e3a5f", height=100)
    header_frame.pack(fill="x")

    # 3 columns layout
    header_frame.grid_columnconfigure(0, weight=1)  # Left (logo)
    header_frame.grid_columnconfigure(1, weight=2)  # Center (text)
    header_frame.grid_columnconfigure(2, weight=1)  # Right (empty balance)

    # LEFT → Logo
    logo_label = tk.Label(header_frame, text="LOGO", bg="#1e3a5f", fg="white")
    logo_label.grid(row=0, column=0, padx=10)

    # CENTER → All Text
    text_frame = tk.Frame(header_frame, bg="#1e3a5f")
    text_frame.grid(row=0, column=1)

    title = tk.Label(
        text_frame,
        text="FIT FRESH LLC",
        font=("Arial", 16, "bold"),
        bg="#1e3a5f",
        fg="white"
    )
    title.pack()

    details = tk.Label(
        text_frame,
        text="AWEER, RAS AL KHOR | +97148604033 | fitfresh@uae.com",
        font=("Arial", 10),
        bg="#1e3a5f",
        fg="white"
    )
    details.pack()

    # RIGHT → Empty (for balance)
    empty = tk.Label(header_frame, bg="#1e3a5f")
    empty.grid(row=0, column=2)

    return header_frame