import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import pandas as pd
from ui_components import create_header, create_page_title
from datetime import datetime
from tkinter import END
from edit_commercial import EditCommercial

class EditPage:

    def __init__(self, parent, controller):
        self.parent = parent
        self.controller = controller
        self.fields={}
        self.vehicle_map={}
        self.selected_category=None
        
    def open_vehicle_list(self):
        # =========================
        # TOP FRAME (Search + Category)
        # =========================
        self.main_frame =  tk.Frame(self.parent, bg="#d9f4ff")
        self.main_frame.pack(fill="both", expand=True)
        header_frame= tk.Frame(self.main_frame)
        category_frame = tk.Frame(self.main_frame, bg="#d9f4ff")
        
        category_frame.pack(fill="x", pady=1)
        top_frame = tk.Frame(self.main_frame,bg="#d9f4ff")
        top_frame.pack(fill="x", pady=0)
        label_guide=tk.Label(top_frame, text="Select Your Category for Edit",
                             font=("Arial",10,"bold"))
        label_guide.pack(anchor="w",padx=5, pady=2)
        button_frame=tk.Frame(top_frame,bg="#d9f4ff")
        button_frame.pack(anchor="w")
        two_wheeler_btn=tk.Button(button_frame, text="🛵Two Wheeler", 
                                  font=("Segoe UI",10),bg="#EAF3EB", relief="solid",
                                  padx=10, pady=8)
        two_wheeler_btn.pack(side="left",padx=15)
      
        commercial_btn=tk.Button(button_frame, text="🚚Commercial Fleet", 
                                 command=self.open_commercial, font=("Segoe UI",10),bg="#E5F0CE", relief="solid",
                                  padx=10, pady=8)
        commercial_btn.pack(side="left", padx=10)
        buses_btn=tk.Button(button_frame, text="  🚍  Busses  ", 
                                  font=("Segoe UI",10),bg="#B2F3B0", relief="solid",
                                  padx=10, pady=8)
        buses_btn.pack(side="left", padx=10)
        office_fleet_btn=tk.Button(button_frame, text="🚘Office Fleet ", 
                                   font=("Segoe UI",10),bg="#EEC09E", relief="solid",
                                  padx=10, pady=8)
        office_fleet_btn.pack(side="left", padx=10)
        
        close_btn=tk.Button(button_frame, text=" ❌ Exit ", 
                                   command=self.close_me, font=("Segoe UI",10),bg="#C29231", relief="solid",
                                  padx=10, pady=8)
        close_btn.pack(side="left", padx=10)
        
        welcome_frame = tk.Frame(button_frame, bg="#25282b", bd=2, relief="ridge")
        welcome_frame.pack(side="right", padx=20)
        tk.Label(welcome_frame, text="👨‍💼 Welcome Admin", font=("Arial", 12,"bold"),bg="#1f2937", fg="white", padx=20, pady=8).pack()
        welcome_msg = tk.Frame(button_frame, bg="#F5F5F5", bd=2, relief="solid")
        welcome_msg.pack(fill="x",padx=20, pady=10)
        
    def open_commercial(self):
        self.parent.grab_set()
        EditCommercial(self.parent, self)
        
    def close_me(self):
        confirm=messagebox.askyesno("FTMS PRO: Confirm Exit", "Are you sure you want to Close?")
        if confirm:
            self.parent.grab_release()
            self.controller.overlay.destroy()
            self.controller.set_form_mode(False)
            self.main_frame.pack_forget()
            self.controller.show_main_menu()