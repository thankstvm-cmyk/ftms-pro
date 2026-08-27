import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import sqlite3
from datetime import date, datetime, timedelta
from tkinter import messagebox
from PIL import Image, ImageTk
from tkcalendar import DateEntry
import os, shutil
from vehicle_insurance import InsurancePage
from ui_components import create_header, create_page_title
import re

class AddVehicleWindow:

    def __init__(self, parent, controller):
        self.parent=parent
        self.controller=controller
        self.image_path=None
        self.mulkiya_front_path=None
        self.mulkiya_back_path=None
        #MAIN CONTAINER
        self.frame=tk.Frame(parent, bg="white")
        self.frame.grid(row=0, column=0, sticky="nsew")
        parent.grid_rowconfigure(0, weight=1)
        parent.grid_columnconfigure(0, weight=1)
        self.resetting_form=False
        
        #HEADER
        create_header(self.frame)
        #FORM CREATING SPACE
        self.center_frame=tk.Frame(self.frame, bg="#1e3a5f")
        self.center_frame.grid(row=1, column=0, sticky="nsew", padx=50, pady=2)
        self.center_frame.grid_rowconfigure(1, weight=1)
        self.center_frame.grid_columnconfigure(0, weight=1)
        self.frame.grid_rowconfigure(1, weight=1)
        self.frame.grid_columnconfigure(0, weight=1)
        
        # PAGE TITLE (STANDARD)
        create_page_title(self.center_frame, "Add New Vehicle Details")                              
        
        self.form_frame=tk.Frame(self.center_frame, bg="#1e3a5f", padx=30, pady=2)
        self.form_frame.grid(row=1, column=0, sticky="nsew", pady=2)
        
        self.center_frame.grid_rowconfigure(1,weight=1)
        self.center_frame.grid_columnconfigure(0, weight=1)
        
        self.form_frame.columnconfigure(0, weight=1)
        self.form_frame.columnconfigure(1, weight=2)
        
        self.form_frame=tk.Frame(self.center_frame, bg="#1e3a5f", padx=30, pady=3)
        self.form_frame.grid(row=1, column=0, sticky="nsew", pady=3)
          
        #DATABASE
        self.conn=sqlite3.connect("D:/FTMS PRO/ftms.db")
        self.cursor=self.conn.cursor()
        self.create_widgets()
        

    def validate_plate_number(self, value):
        if value.isdigit() and len(value)<=5:
            return True
        else:
            return False
    
    def validate_number(self, value):
        if value.isdigit():
            return True
        else:
            return False
        
    def validate_odometer(self, value):
        if value=="":
            return True
        if  value.isdigit() and len(value)<=6:
            return True
        else:
            return False
        
    def on_engine_change(self, event=None):
        engine = self.engine_entry.get().upper()
        self.engine_entry.delete(0, tk.END)
        self.engine_entry.insert(0, engine)
        
        
    def validate_engine_no(self, engine):
        if engine=="":
            messagebox.showwarning("FTMS PRO: Error"," Engine No. cannot be empty")
            return False
        if len(engine)<6 or len(engine)>20:
            messagebox.showwarning("FTMS PRO: Error"," Engine No. must be between 5 and 20 characters")
            return False
        if not re.match("^[A-Z; a-z; 0-9]+$", engine):
            messagebox.showinfo("FTMS PRO:", "Engine Number must contains only letters and numbers")
            return False
        return True
    
    def validate_engine_live(self, value):
        if value=="":
            self.lbl_engine_error.config(text="")
            return True
        if len(value)<6:
            self.lbl_engine_error.config(text="Minimum 6 Alpha Numeric characters required")
            return True
        if len(value)>20:
            self.lbl_engine_error.config(text="Maximum 20 characters allowed")
            return False
        if not value.isalnum():
            self.lbl_engine_error.config(text="Only letters and numbers allowed")
            return False
        if not any (c.isalpha() for c in value) or not any (c.isdigit() for c in value):
            self.lbl_engine_error.config(text="Must contain both letters and numbers")
            return False
        self.lbl_engine_error.config(text="")
        return True

    def create_widgets(self):
        #1.  MAIN CONTAINER
        self.main_container=tk.Frame(self.form_frame, bg="#f5f5f5")
        self.main_container.grid(row=0, column=0, pady=5, sticky="nsew")
        self.form_frame.grid_rowconfigure(0, weight=1)
        self.form_frame.grid_columnconfigure(0, weight=1)
        self.main_container.grid_rowconfigure(0, weight=1)
        self.main_container.grid_columnconfigure(0, weight=1)

        # ==========================
        # VEHICLE INFORMATION FRAME
        # ==========================
        
        #2. TOP FRAME (FORM AREA)
        top_frame=tk.Frame(self.main_container)
        top_frame.grid(row=0, column=0,sticky="nsew", pady=(0.5))
        top_frame.grid_rowconfigure(0, weight=1)
        top_frame.grid_columnconfigure(0, weight=3)
        top_frame.grid_columnconfigure(1, weight=2)
        top_frame.grid_rowconfigure(1, weight=1)
        
        # BUTTON FRAME FOR COMMAND BUTTONS 
        self.button_frame=tk.Frame(self.main_container)
        self.button_frame.grid(row=1, column=0, sticky="ew", pady=5)
        self.button_frame.grid_columnconfigure(0, weight=1)
        self.button_frame.grid_columnconfigure(1, weight=1)
        self.button_frame.grid_columnconfigure(2, weight=1)
        self.button_frame.grid_columnconfigure(3, weight=1)
        self.button_frame.grid_columnconfigure(4, weight=1)
        
        # ARRANGING BUTTONS EQUAL DISTANCE
        # COMMAND BUTTONS : SAVE, CLOSE, OPEN INSURANCE PAGE, SAVE IMAGES
        self.save_btn=tk.Button(self.button_frame, text="SAVE", command=self.save_vehicle, height=2)
        self.save_btn.grid(row=0, column=0, padx=5, sticky="ew")
        
        self.new_btn=tk.Button(self.button_frame, text="NEW VEHICLE",command=self.new_vehicle,height=2)
        self.new_btn.grid(row=0, column=1, padx=5, sticky="ew")
        self.new_btn.config(state="disabled")
        
        self.close_btn=tk.Button(self.button_frame, text="CLOSE", command=self.form_close, height=2)
        self.close_btn.grid(row=0, column=2, padx=5, sticky="ew")
        
        self.ins_btn=tk.Button(self.button_frame, text="OPEN INSURANCE PAGE", command=self.open_insurance_page, height=2)
        self.ins_btn.grid(row=0, column=3, padx=5, sticky="ew")
        
        self.image_btn=tk.Button(self.button_frame, text="SAVE IMAGES", command=self.save_images, height=2)
        self.image_btn.grid(row=0, column=4, padx=5, sticky="ew")
        
        self.main_container.grid_rowconfigure(0, weight=1)
        self.main_container.grid_columnconfigure(1, weight=0)
        self.main_container.grid_rowconfigure(1, weight=0)
        self.left_frame=tk.Frame(top_frame)
        self.left_frame.grid(row=0, column=0, padx=10, pady=4, sticky="nsew")
        
        self.left_frame.grid_columnconfigure(0, weight=1) #for label
        self.left_frame.grid_columnconfigure(1, weight=3) #for Entry
        self.left_frame.grid_columnconfigure(2, weight=1) #for label
        self.left_frame.grid_columnconfigure(3, weight=3) #for Entry
    
        
        #5. BUTTON AREA 
        button_frame=tk.Frame(self.main_container)
        button_frame.grid(row=1, column=0, sticky="ew", pady=5)
        
        vcmd = (self.frame.register(self.validate_plate_number),'%P')
        vcmd_number = (self.frame.register(self.validate_number), '%P')
        vcmd_odometer= (self.frame.register(self.validate_odometer),'%P')
        vcmd_engine = (self.frame.register(self.validate_engine_live), '%P')
        vcmd_vin = (self.frame.register(self.is_valid_vin),'%P')
        
        self.tank_capacity_var=tk.StringVar()
        self.tank_capacity=ttk.Entry(self.left_frame, width=25, textvariable=self.tank_capacity_var)
        self.tank_capacity.grid(row=3, column=3, padx=40)
        
        #INPUT SECTION STARTS FROM HERE------>
        # LEFT COLUMN
        ttk.Label(self.left_frame, text="Plate Source").grid(row=0, column=0, padx=10, pady=8, sticky="w")
        self.plate_source = ttk.Combobox(self.left_frame, values=["Dubai", "Abu Dhabi", "Fujairah","Ras Al Khaymah","Um Al Quewain",
                                                                 "Sharjah", "Ajman"],state="readonly")
        self.plate_source.grid(row=0, column=1, padx=10, pady=8, sticky="ew")
        
        self.plate_source.bind("<<ComboboxSelected>>",self.update_plate_codes)
        ttk.Label(self.left_frame, text="Plate Code").grid(row=1, column=0, padx=10, pady=8, sticky="w")
        self.plate_code = ttk.Combobox(self.left_frame,values=[], state="readonly")
        self.plate_code.grid(row=1, column=1, padx=10, sticky="ew")
        
        ttk.Label(self.left_frame, text="Plate Number").grid(row=2, column=0, padx=10, pady=8, sticky="w")
        self.plate_number_entry = tk.Entry(self.left_frame, validate="key",  validatecommand=vcmd)
        self.plate_number_entry.grid(row=2, column=1, padx=10, pady=8, sticky="ew")

        ttk.Label(self.left_frame, text="Brand").grid(row=3, column=0, padx=10, pady=8, sticky="w")
        self.brand_combo = ttk.Combobox(self.left_frame, values=[], state="readonly")
        self.brand_combo.grid(row=3, column=1, padx=10, sticky="ew")
        self.brand_combo.bind("<<ComboboxSelected>>",self.load_models)
        self.load_brands()

        ttk.Label(self.left_frame, text="Model").grid(row=4, column=0, padx=10, pady=8, sticky="w")
        self.model_combo = ttk.Combobox(self.left_frame, values=[],  state="readonly")
        self.model_combo.grid(row=4, column=1, padx=10, sticky="ew")

        ttk.Label(self.left_frame, text="Year").grid(row=5, column=0, padx=10, pady=8, sticky="w")
        current_year=datetime.now().year
        years=list(range(current_year,1994,-1))
        self.year_combo=ttk.Combobox(self.left_frame,values=years, state="readonly")
        self.year_combo.grid(row=5,column=1,padx=10, sticky="ew")
        self.year_combo.set(current_year)
        self.year_combo.bind("<<ComboboxSelected>>", self.set_mulkiya_date_range)

        ttk.Label(self.left_frame, text="Vehicle Type").grid(row=6, column=0, padx=10, pady=8, sticky="w")
        self.chiller_combo = ttk.Combobox(self.left_frame,
                                         values=["Chiller", "Non-Chiller", "Freezer"],
                                         state="readonly")
        self.chiller_combo.grid(row=6, column=1, padx=10, sticky="ew")
        self.chiller_combo.bind("<<ComboboxSelected>>", self.chiller_changed)
        
        ttk.Label(self.left_frame, text="Chassis No. (VIN)").grid(row=7, column=0,padx=10, pady=8, sticky="w")
        self.chassis_entry = ttk.Entry(self.left_frame)
        self.chassis_entry.grid(row=7, column=1, padx=10, pady=8, sticky="ew")
        self.chassis_entry.bind("<KeyRelease>",self.on_vin_change)
        self.chassis_entry.bind("<FocusOut>",self.clear_vin_message)
        
        self.lbl_vin_msg = tk.Label(self.left_frame, text="", fg="red", font=("Arial",8))
        self.lbl_vin_msg.grid(row=10, column=1, padx=10, sticky="w")
        
        self.engine_var = tk.StringVar()
        vcmd_engine=(self.left_frame.register(self.validate_engine_live),'%P')
        ttk.Label(self.left_frame, text="Engine No.").grid(row=8,  column=0,padx=10, pady=8, sticky="w")
        self.engine_entry = tk.Entry(self.left_frame, textvariable=self.engine_var,                 
                                     validate="key", validatecommand=vcmd_engine)
        self.engine_entry.grid(row=8, column=1, padx=10, pady=8, sticky="ew")
        self.engine_entry.bind("<KeyRelease>", self.on_engine_change)
        self.lbl_engine_error = tk.Label(self.left_frame, text="", fg="red", font=("Arial", 8))
        self.lbl_engine_error.grid(row=10, column=1, padx=40, sticky="w")
        
        
        tk.Label(self.left_frame, text="Mulkiya Issue Date").grid(row=9, column=0, padx=10, pady=5, sticky="w")
        self.mulkiya_issue_date_entry=DateEntry(self.left_frame, width=15, date_pattern='yyyy-mm-dd')
        self.mulkiya_issue_date_entry.grid(row=9, column=1, padx=10, pady=8, sticky="ew")
        self.mulkiya_issue_date_entry.bind("<<DateEntrySelected>>", self.calculate_expiry)
        
        ttk.Label(self.left_frame, text="Body Type",anchor="w").grid(row=0, column=2, padx=10, pady=8, sticky="ew")
        self.body_type_combo = ttk.Combobox(self.left_frame,
                                      values=["Open", "Closed","Flat Bed"],
                                      state="readonly")
        self.body_type_combo.grid(row=0, column=3, padx=10, pady=8, sticky="ew")

        ttk.Label(self.left_frame, text="Load Capacity (TON)",anchor="w").grid(row=1, column=2, padx=10, pady=8, sticky="ew")
        self.ton_capacity_combo = ttk.Combobox(self.left_frame, values=
                                                               ['1 - Ton/ Pickup',
                                                                '1.5 - Ton',
                                                                '3 - Light Truck',
                                                                '5 - Medium Truck',
                                                                '7 - Cargo Truck',
                                                                '10 - Heavy Truck', 
                                                                '12 - Heavy Cargo', 
                                                                '15 - Large Cargo', 
                                                                '20 - Trailer',
                                                                '25 - Heavy Trailer',
                                                                '30 - Articulated Truck',
                                                                '40 - Semi Trailer'], 
                                                                state="readonly")
        self.ton_capacity_combo.grid(row=1, column=3, padx=10, pady=8, sticky="ew")
        self.ton_capacity_combo.bind("<<ComboboxSelected>>", self.on_ton_change)
        
        # RIGHT COLUMN
        ttk.Label(self.left_frame, text="Fuel Type", width=18, anchor="w" ).grid(row=2, column=2, padx=10, pady=8, sticky="ew")
        self.fuel_type_combo = ttk.Combobox(self.left_frame,
                                      values=["Petrol", "Diesel","Electric", "Hybrid", "CNG","Other"],
                                      state="readonly")
        self.fuel_type_combo.grid(row=2, column=3, padx=10, pady=8, sticky="ew")
        self.fuel_type_combo.set("Petrol")

        ttk.Label(self.left_frame, text="Tank Capacity - in Ltrs.", width=18, anchor="w").grid(row=3, column=2, padx=10, pady=8, sticky="ew")
        self.tank_capacity = ttk.Entry(self.left_frame, validate='key', validatecommand=vcmd_number)
        self.tank_capacity.grid(row=3, column=3, padx=10, pady=8, sticky="ew")
        self.ton_capacity_combo.bind("<<ComboboxSelected>>",self.on_ton_change)
        
        ttk.Label(self.left_frame, text="Current Odometer", width=18,anchor="w").grid(row=4, column=2, padx=10, pady=8, sticky="ew")
        self.current_odometer = ttk.Entry(self.left_frame,  validate='key', validatecommand=vcmd_odometer)
        self.current_odometer.grid(row=4, column=3, padx=10, pady=8, sticky="ew")

        ttk.Label(self.left_frame, text="Tail Lift", anchor="w").grid(row=5, column=2, padx=10, pady=8, sticky="ew")
        self.tail_lift = ttk.Combobox(self.left_frame,
                                      values=["Yes", "No"],
                                      width=15,state="readonly")
        self.tail_lift.grid(row=5, column=3, padx=10, sticky="ew", pady=8)

        ttk.Label(self.left_frame, text="Status", width=18, anchor="w").grid(row=6, column=2, padx=10, pady=8, sticky="ew")
        self.status_combo = ttk.Combobox(self.left_frame,
                                   values=["Active", "Under Repair","Rented-Out", "Rented-In"],
                                   state="readonly")
        self.status_combo.grid(row=6, column=3, padx=10, sticky="ew", pady=8)
        self.status_combo.set("Active")
        
        ttk.Label(self.left_frame, text="Ownership Type",width=18, anchor="w").grid(row=7, column=2, padx=10, pady=8, sticky="ew")
        self.ownership_type_combo = ttk.Combobox(self.left_frame, values=["Company Owned", "Rented In", "Leased"],
                                                 state="readonly")
        self.ownership_type_combo.grid(row=7,column=3, padx=10, sticky="ew", pady=8)
        self.ownership_type_combo.set("Company Owned")
        
        tk.Label(self.left_frame, text="Mulkiya Expiry Date").grid(row=8, column=2, padx=10, pady=5, sticky="e")
        self.mulkiya_expiry_date=tk.Entry(self.left_frame)
        self.mulkiya_expiry_date.grid(row=8, column=3,padx=10, sticky="ew", pady=8)
        self.mulkiya_expiry_date.config(state="readonly")
        
        self.comboboxes=[
            self.brand_combo, self.model_combo, self.chiller_combo, self.body_type_combo, self.status_combo]
        
        #SET FOCUS TO THE FIRST WIDGET WHEN FORM LOADS
        self.plate_source.focus()
        self.set_mulkiya_date_range()
        
        def validate_comboboxes(self):
            for combo in self.comboboxes:
                if not combo.get():
                    messagebox.showerror("Selection Required", "Please Select a Suitable item from the Drop Down List")
                    combo.focus_set()
                    return False
                return True

        # =========================
        # DOCUMENTS FRAME
        # =========================
        documents_frame = ttk.LabelFrame(top_frame, text="Vehicle Documents")
        documents_frame.grid(row=0, column=1, padx=10, pady=3, sticky="nsew")
        inner_frame=tk.Frame(documents_frame)
        inner_frame.pack(anchor="n", pady=2)
        
        # COMMON FUNCTION (CREATE BOX)
        def create_doc_box(parent, text):
            frame=tk.Frame(parent, width=210, height=100, relief="solid", bd=1, bg="#f9f9f9")
            frame.pack(pady=5)
            frame.pack_propagate(False)
            label=tk.Label(frame, text=text)
            label.pack(expand=True)
            return frame, label
        

        # =========================
        # VEHICLE IMAGE
        # =========================
        self.vehicle_img_frame, self.vehicle_img_label=create_doc_box(
            inner_frame, "Vehicle Image")
        ttk.Button(inner_frame, text="Upload Vehicle Image",
                command=self.upload_vehicle_image).pack(pady=3)

        # =========================
        # MULKIYA FRONT
        # =========================
        self.mulkiya_front_frame, self.mulkiya_front_label=create_doc_box(
            inner_frame, "Mulkiya Front")
        ttk.Button(inner_frame, text="Upload Mulkiya Front",
                command=self.upload_mulkiya_front).pack(pady=3)

        # =========================
        # MULKIYA BACK
        # =========================
        self.mulkiya_back_frame, self.mulkiya_back_label=create_doc_box(
            inner_frame, "Mulkiya Back")

        ttk.Button(inner_frame, text="Upload Mulkiya Back",
                command=self.upload_mulkiya_back).pack(pady=3)
        
    # CHECKING TON CAPACITY >=3 SETTING DIESEL AS FULE
    def auto_set_fuel(self, event=None):
        try:
            selected=self.ton_capacity_combo.get()
            if selected:
                capacity, _ = self.extract_capacity(selected)
                if capacity>=3:
                    self.fuel_type_combo.set("Diesel")
                else:
                    self.fuel_type_combo.set("Petrol")
        except Exception as e:
            messagebox.showwarning("FTMS PRO: Error:",str(e))
            
    def on_ton_change(self, event=None):
        self.auto_set_fuel()
        self.update_tank_capacity(event)
        self.ton_capacity_combo.config(state="disabled")
        self.current_odometer.focus()
            
    def calculate_expiry(self, event=None):
        issue = self.mulkiya_issue_date_entry.get_date()
        expiry=issue+timedelta(days=364)
        self.mulkiya_expiry_date.config(state="normal")
        self.mulkiya_expiry_date.delete(0, tk.END)
        self.mulkiya_expiry_date.insert(0, expiry.strftime("%Y-%m-%d"))
        self.mulkiya_expiry_date.config(state="readonly")
        messagebox.showinfo("FTMS PRO: INFO !", f"Vehicle Mulkiya will be Expire on {expiry.strftime('%Y-%m-%d')}")
        self.mulkiya_issue_date_entry.config(state='disabled')
        self.year_combo.config(state="disabled")
        
    def update_tank_capacity(self, event=None):
        if self.resetting_form:
            return
        selected=self.ton_capacity_combo.get().strip()
        if not selected:
            self.tank_capacity.config(state="normal")
            self.tank_capacity.delete(0,"end")
            self.tank_capacity.config(state="disabled")
            return 
        ton = float(selected.split()[0])
        tank_map={
            1: 80,
            1.5: 100,
            3: 120,
            5: 150,
            7: 200,
            10: 300,
            12: 400,
            15: 500,
            20: 650,
            25: 800,
            30: 1000,
            40: 1500}
        value=tank_map.get(ton,"")
        self.tank_capacity.config(state="normal") 
        self.tank_capacity.delete(0, "end")
        self.tank_capacity.insert(0, str(value))
        self.tank_capacity.config(state='disabled')
        
    #OPENING INSURANCE PAGE
    def open_insurance_page(self):
        self.controller.open_vehicleins_page()
        self.frame.destroy()
    
    # USER DEFINED FUNCTIONS
    def new_vehicle(self):
        self.resetting_form=True
        self.plate_source.set("")
        self.plate_code.set("")
        self.plate_number_entry.config(validate="none")
        self.plate_number_entry.delete(0, "end")
        self.ton_capacity_combo.set("")      
        self.fuel_type_combo.set("")
        self.tank_capacity.config(validate="none")
        self.tank_capacity.config(state="normal")
        self.tank_capacity.delete(0, "end")
        self.tank_capacity.insert(0,"")
        self.tank_capacity.config(state="disabled")
        self.current_odometer.delete(0, "end")
        self.brand_combo.set("")
        self.model_combo.set("")
        self.body_type_combo.set("")
        self.chiller_combo.set("")
        self.tail_lift.set("")
        self.status_combo.set("")
        self.chassis_entry.delete(0,"end")
        self.engine_entry.delete(0, "end")
        self.ownership_type_combo.set("")
        self.save_btn.config(state="normal")
        self.ton_capacity_combo.config(state="normal")
        self.body_type_combo.config(state="normal")
        self.tank_capacity.config(validate="key")
        self.plate_number_entry.config(validate='key')
        self.mulkiya_expiry_date.delete(0, "end")
        self.year_combo.config(state="normal")
        current_year =date.today().year
        self.year_combo.set(current_year)
        self.plate_number_entry
        self.plate_source.focus()
        self.mulkiya_issue_date_entry.config(state="normal")
        self.resetting_form=False
        
        
    def save_vehicle(self):
        try:
            plate_source=self.plate_source.get()
            plate_code=self.plate_code.get()
            plate_number = self.plate_number_entry.get()
            brand = self.brand_combo.get()
            model = self.model_combo.get()
            year = self.year_combo.get()
            
            # CHECKING IF THE THERE IS VALUE, ACCEPT IT OR STORE 0
            ton_capacity_raw=self.ton_capacity_combo.get()
            ton_capacity= float(ton_capacity_raw.split(" - ")[0]) 
            ton_capacity, vehicle_category = self.extract_capacity(ton_capacity_raw)
            if ton_capacity is None:
                messagebox.showerror("FTMS PRO Error:","Invalid Load Capacity")
                return
            fuel_type=self.fuel_type_combo.get()
            current_odometer_raw=self.current_odometer.get()
            vehicle_category=ton_capacity_raw.split("-")[1] if ton_capacity_raw else ""
            current_odometer=int(current_odometer_raw) if current_odometer_raw else 0
            body_type = self.body_type_combo.get()
            vehicle_type=self.chiller_combo.get()
            tail_lift=self.tail_lift.get()
            tank_capacity=self.tank_capacity.get()
            image_path=self.image_path
            status=self.status_combo.get()
            chassis_no = self.chassis_entry.get()
            engine_no = self.engine_entry.get()
            ownership_type = self.ownership_type_combo.get()
            mulkiya_front_path=self.mulkiya_front_path
            mulkiya_back_path=self.mulkiya_back_path
            seating_capacity=3
            mulkiya_issue_date = self.mulkiya_issue_date_entry.get()
            mulkiya_expiry_date = self.mulkiya_expiry_date.get()
            now=datetime.now().strftime("%d-%b-%Y")
            
            
            #CHECKING WHETHER ANY EMPTY DATA FIELD ?
            if(plate_source=="" or plate_code=="" 
            or plate_number=="" or brand=="" 
            or model=="" or year=="" 
            or ton_capacity=="" or body_type==""
            or vehicle_type=="" or tail_lift=="" 
            or vehicle_category=="" or tank_capacity=="" 
            or current_odometer=="" or fuel_type==""
            or chassis_no=="" or engine_no==""
            or ownership_type=="" or mulkiya_issue_date=="" 
            or mulkiya_expiry_date==""):
                    messagebox.showwarning("FTMS PRO: Missing Data", "Please fill all required data fields before Saving")
                    return
                
            #IF NOT CHASSIS AND ENGINE NOS NOT VALID
            if not self.validate_chassis_no(chassis_no):
                self.chassis_entry.focus()
                return
            if not self.validate_engine_no(engine_no):
                self.engine_entry.focus()
                return
            
            self.cursor.execute("""
                INSERT INTO vehicles (
                plate_source,
                plate_code,
                plate_number,
                brand,
                model,
                year,
                ton_capacity,
                fuel_type,
                body_type,
                vehicle_type,
                tail_lift,
                vehicle_category,
                tank_capacity,
                current_odometer,
                image_path,
                status,
                chassis_no,
                engine_no,
                ownership_type,
                mulkiya_issue_date,
                mulkiya_expiry_date,
                mulkiya_front_path,
                mulkiya_back_path,
                seating_capacity,
                created_at,
                updated_at
                ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                """, (
                plate_source,
                plate_code,
                plate_number,
                brand,
                model,
                year,
                ton_capacity,
                fuel_type,
                body_type,
                vehicle_type,
                tail_lift,
                vehicle_category,
                tank_capacity,
                current_odometer,
                image_path,
                status,
                chassis_no,
                engine_no,
                ownership_type,
                mulkiya_issue_date,
                mulkiya_expiry_date,
                mulkiya_front_path,
                mulkiya_back_path,
                seating_capacity,
                now,
                now
                ))
            self.conn.commit()
            messagebox.showinfo("FTMS PRO: INFORMATION ", "Data Saved Succesfully")
            self.save_btn.config(state="disabled")
            self.new_btn.config(state="active")
            
        except sqlite3.IntegrityError:
            messagebox.showerror("FTMS PRO: Duplicate Vehicle", "This vehicle plate already exists. Check your Data")
        except Exception as e:
            messagebox.showerror("FTMS PRO: Data Error:", str(e))
    
    def form_close(self):
        sure=messagebox.askyesno("FTMS PRO:","Are you sure you want to Exit?")
        if sure:
            self.parent.grab_release()
            self.parent.destroy()
            self.controller.set_form_mode(False)
            self.controller.clear_content_area()
        
        
    def chiller_changed(self, event):
        vehicle_type=self.chiller_combo.get()
        if vehicle_type=='Chiller' or vehicle_type=="Freezer":
            self.body_type_combo.set('Closed')
            self.body_type_combo.config(state="disabled")
        elif vehicle_type=='Non-Chiller':
            self.body_type_combo.config(state='Enabled')
    
    def upload_vehicle_image(self):
        file_path=filedialog.askopenfilename(title="FTMS - Select Your Vehicle Image", filetypes=[("Image Files", "*.jpg *.jpeg"),("JPEG Files", "*.jpg")])
        if file_path:
            self.image_path=file_path
            self.vehicle_photo=self.resize_image(file_path)
            self.vehicle_img_label.config(image=self.vehicle_photo)
            self.vehicle_img_label.image=self.vehicle_photo
            
    def resize_image(self, path, width=200, height=100):
        img=Image.open(path)
        img.thumbnail((width, height))
        return ImageTk.PhotoImage(img)
            
    #UPDATED CODE FOR SAVING, UPLOAD CODE
    def upload_mulkiya_front(self):
        file_path=filedialog.askopenfilename(title="Select Mulkiya Front Image", filetypes=[("Image Files", "*.jpg *.jpeg"),("JPEG Files", "*.jpg")])
        if file_path:
            self.mulkiya_front_path=file_path
            self.mulkiya_front_photo = self.resize_image(file_path)
            self.mulkiya_front_label.config(image=self.mulkiya_front_photo)
            self.mulkiya_front_label.imaage=self.mulkiya_front_photo


    def upload_mulkiya_back(self):
        file_path=filedialog.askopenfilename(title="Select Mulkiya Back Image", filetypes=[("Image Files", "*.jpg *.jpeg"),("JPEG Files", "*.jpg")])
        if file_path:
            self.mulkiya_back_path=file_path
            self.mulkiya_back_photo = self.resize_image(file_path)
            self.mulkiya_back_label.config(image=self.mulkiya_back_photo)
            self.mulkiya_back_label.imaage=self.mulkiya_back_photo
            
    def save_images(self):
        # ✅ Get plate number
        plate_number = self.plate_number_entry.get().strip()
        if not plate_number:
            messagebox.showwarning("FTMS PRO: Warning", "Plate number is required")
            return
        if not any([ getattr(self,"image_path", None),
            getattr(self,"mulkiya_front_path", None),
            getattr(self,"mulkiya_back_path", None) ]):
            messagebox.showwarning("FTMS PRO: Warning", "No Images uploaded to Save")
            return
        
        # ✅ Clean folder name
        plate_number = plate_number.replace(" ", "_")

        # ✅ Folder path
        base_folder = "FTMS_DATA/VEHICLE_DOCS"
        vehicle_folder = os.path.join(base_folder, plate_number)

        # ✅ Create folder
        os.makedirs(vehicle_folder, exist_ok=True)

        try:
            # 🚗 Vehicle Image
            if hasattr(self, "image_path"):
                ext = os.path.splitext(self.image_path)[1]
                shutil.copy(self.image_path,
                        os.path.join(vehicle_folder, "vehicle" + ext))

            # 📄 Mulkiya Front
            if hasattr(self, "mulkiya_front_path"):
                ext = os.path.splitext(self.mulkiya_front_path)[1]
                shutil.copy(self.mulkiya_front_path,
                        os.path.join(vehicle_folder, "mulkiya_front" + ext))

            # 📄 Mulkiya Back
            if hasattr(self, "mulkiya_back_path"):
                ext = os.path.splitext(self.mulkiya_back_path)[1]
                shutil.copy(self.mulkiya_back_path,
                        os.path.join(vehicle_folder, "mulkiya_back" + ext))

                # ✅ Success message
                messagebox.showinfo("FTMS PRO:Success", "Images saved successfully")

        except Exception as e:
            messagebox.showerror("FTMS PRO: Error", f"Error saving images:\n{e}")
            
    def load_brands(self):
        self.cursor.execute("SELECT id, brand_name FROM vehicle_brands ORDER BY brand_name")
        brands = self.cursor.fetchall()

        self.brand_dict = {brand_name: brand_id for brand_id, brand_name in brands}
        self.brand_combo['values'] = list(self.brand_dict.keys())


    def load_models(self, event=None):
        selected_brand = self.brand_combo.get()

        if selected_brand:
            brand_id = self.brand_dict[selected_brand]

            self.cursor.execute(
                "SELECT id, model_name FROM vehicle_models WHERE brand_id = ? ORDER BY model_name",
                (brand_id,)
            )
            models = self.cursor.fetchall()

            self.model_dict = {model_name: model_id for model_id, model_name in models}
            self.model_combo['values'] = list(self.model_dict.keys())
            self.model_combo.set('')

    def load_plate_codes(self, plate_source):
        conn=sqlite3.connect("ftms.db")
        cursor=conn.cursor()
        cursor.execute("SELECT DISTINCT plate_code FROM plate_codes WHERE plate_source=?",(plate_source,))
        rows=cursor.fetchall()
        codes=[row[0] for row in rows]
        self.plate_code['values']=codes
        conn.close()
        
    def set_mulkiya_date_range(self, event=None):
        if not self.year_combo.get():
            return
        year=int(self.year_combo.get())
        today = date.today()
        self.mulkiya_issue_date_entry.config(
            mindate=date(year, 1,1),
            maxdate = today)
        self.mulkiya_issue_date_entry.set_date(date(year, 1,1))
        
    def extract_capacity(self, text):
        if not text:
            return 0, ""
        try:
            parts = text.split("-")
            capacity = float(parts[0].strip())
            category = parts[1].strip() if len(parts)>1 else ""
            return capacity, category
        except:
            return None, None
    
    def is_valid_vin(self, vin):
        vin = vin.upper().strip()
        if vin =="":
            return True
        if not re.fullmatch(r"[A-Z0-9]{17}", vin):
           return False
        if any(c in vin for c in "IOQ"):
           return False
        return True
    
    def is_valid_vin(self, vin):
        digit_count = sum(c.isdigit() for c in vin)
        letter_count = sum(c.isalpha() for c in vin)
        if len(vin)!=17:
            return False, "VIN Must be 17 letters & numbers. \nExample: JTHBN1EF2G5001234"
        elif any(c in vin for c in "IOQ"):
            return False, "VIN cannot contain I, O, Q"
        elif digit_count<10:
            return False, "Vin must contain minimum 10 digits"
        elif letter_count<5:
            return False, "Vin must contain minimum 5 letters"
        return True, "Valid VIN"
        
    def clear_vin_message(self, event=None):
        self.lbl_vin_msg.config(text="")

    def on_vin_change(self, event):
        #✅ Valid VIN"
        vin = self.chassis_entry.get().upper()
        if len(vin)>17:
            vin = vin[:17]
        self.chassis_entry.delete(0, tk.END)
        self.chassis_entry.insert(0, vin)
        valid, message = self.is_valid_vin(vin)
        letters = sum(c.isalpha() for c in vin)
        digits = sum(c.isdigit() for c in vin)
        total = len(vin)
        if vin=="":
            self.lbl_vin_msg.config(text="")
        elif valid:
            self.lbl_vin_msg.config(text=f"{message}\n|Letters :{letters} Digits :{digits} Total :{total}", fg="blue")
        else:
            self.lbl_vin_msg.config(text=f"{message}\n:Letters :{letters} Digits :{digits} Total :{total}", fg="blue")        
    
    def validate_chassis_no(self, chassis):
        digit_count = sum(c.isdigit() for c in chassis)
        letter_count = sum(c.isalpha() for c in chassis)
        chassis_no = self.chassis_entry.get().strip().upper()
        if chassis=="":
            messagebox.showwarning("FTMS Error:","Chassis NO. (VIN) cannot be empty")
            return False
            self.chassis_entry.focus()
        if not re.match("^[A-HJ-NPR-Z0-9]+$",chassis):
            messagebox.showwarning("FTMS Error:",
                                   "VIN can contain only capital letters and numbers. \nLetters I,O and Q are not allowed")
            return False
        if len(chassis)!=17:
            messagebox.showwarning("FTMS Error:","VIN must be exactly 17 characters")
            return False
        elif letter_count<5:
            messagebox.showwarning("FTMS Error:","VIN must contain minimum 5 alphabets")
            return False
        elif digit_count<10:
                messagebox.showwarning("FTMS Error:", "VIN must contain at least 10 digits")
                return False
        return True

    def update_plate_codes(self, event):
        plate_source = self.plate_source.get()
        self.load_plate_codes(plate_source)
            