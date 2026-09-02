
import tkinter as tk 
from tkinter import ttk 
from tkinter import filedialog 
import sqlite3 
from tkcalendar import dateentry
from tkinter import messagebox 
from PIL import Image, ImageTk 
from tkcalendar import Calendar
from datetime import datetime
import os, shutil 
from ui_components import create_header, create_page_title 
import re 
from UTILS.eidvalidator_utils import EmiratesIDValidator
from UTILS.phone_utils import PhoneValidator
 
class EmployeeForm: 
 
    def __init__(self, parent, controller): 
        self.parent=parent 
        self.controller=controller 
        self.license_categories = {
        "CAT1": {"title": "Motorcycles",    "desc": "Two or Three-wheel vehicles"},
        "CAT2": {"title": "Light Vehicles", "desc": "Cars, SUVs, Pickups up to 3.5 tons"},
        "CAT3": {"title": "Commercial Vehicles", "desc": "Commercial Trucks (3–5 Tonnes)"},
        "CAT4": {"title": "Heavy Trucks", "desc": "3.5 to 7.5 tonnes, Lorries, Tippers, and Trailers."},
        "CAT5": {"title": "Passenger Bus", "desc": "Medium Type Bus upto 24 Seats Passenger Bus"},
        "CAT6": {"title": "Heavy Buses", "desc": "More than 26 passengers up to 50 Seats"},
        "CAT7": {"title": "Light Equiptment", "desc": "Light Forklifts, Light Shovels,Bobcats, Tow Tractors / Tuggers"},
        "CAT8": {"title": "Heavy Equiptment", "desc": "Heavy Forklifts,Reach Stackers, Heavy Mechanical Equipments"}}
         
        #MAIN CONTAINER
        self.frame=tk.Frame(parent, bg="white")
        self.frame.grid(row=0, column=0, sticky="nsew")
        parent.grid_rowconfigure(0, weight=1)
        parent.grid_columnconfigure(0, weight=1)
        self.resetting_form=False
        self.dob_var = tk.StringVar()
        self.category_mode = "SET"
        
        #HEADER
        create_header(self.frame)
        #FORM CREATING SPACE
        self.center_frame=tk.Frame(self.frame, bg="#1e3a5f")
        self.center_frame.grid(row=1, column=0, sticky="nsew")
        self.frame.grid_rowconfigure(1, weight=1)
        self.center_frame.grid_columnconfigure(0, weight=1)
        self.frame.grid_columnconfigure(0, weight=1)
        self.center_frame.grid_rowconfigure(1, weight=1)
     
        
        # PAGE TITLE (STANDARD)
        self.form_frame = tk.Frame(self.center_frame, bg="#1e3a5f")
        self.form_frame.grid(row=1, column=0, sticky="nsew")
        create_page_title(self.center_frame, "Add New Staff Details")  
        
        self.center_frame.grid_rowconfigure(1,weight=1)
        self.center_frame.grid_columnconfigure(0, weight=1)
        
        self.form_frame.grid_rowconfigure(0, weight=1)
        self.form_frame.grid_rowconfigure(1, weight=0)
        self.form_frame.columnconfigure(0, weight=1)
        self.form_frame.columnconfigure(1, weight=1)
        
        self.create_widgets()

    def create_widgets(self):
        #1.  MAIN CONTAINER
        self.main_container = tk.Frame(self.form_frame, bg="#f5f5f5")
        self.main_container.grid(row=0, column=0, columnspan=2, pady=5, sticky="nsew")

        # STEP 2: CONFIGURE GRID
        self.form_frame.grid_rowconfigure(0, weight=1)
        self.form_frame.grid_columnconfigure(0, weight=1)

        self.main_container.grid_rowconfigure(0, weight=1)
        self.main_container.grid_columnconfigure(0, weight=1)

        # STEP 3: NOW CREATE CONTENT FRAME
        # 1️⃣ CREATE
        self.content_frame = tk.Frame(self.main_container, bg="#f5f5f5")
        self.content_frame.grid(row=0, column=0, sticky="nsew")
                
        # CONTENT FRAME GRID STRUCTURE
        self.content_frame.grid_rowconfigure(0, weight=0)  # top 3 panels
        self.content_frame.grid_rowconfigure(1, weight=0)  # emergency + reference
        self.content_frame.grid_rowconfigure(2, weight=0)  # remarks
        self.content_frame.grid_rowconfigure(3, weight=1)  # documents (expand)
        self.content_frame.grid_rowconfigure(4, weight=0)  # buttons
        self.content_frame.grid_columnconfigure(0, weight=1)
        
        self.top_frame = tk.Frame(self.content_frame, bg="#f5f5f5")
        self.top_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        self.mid_frame = tk.Frame(self.content_frame, bg="#f5f5f5")
        self.mid_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)

        self.mid_frame.grid_columnconfigure(0, weight=1)
        self.mid_frame.grid_columnconfigure(1, weight=1)

        self.emergency_frame = tk.Frame(self.mid_frame, bg="white")
        self.emergency_frame.grid(row=0, column=0, padx=5, sticky="nsew")

        self.reference_frame = tk.Frame(self.mid_frame, bg="white")
        self.reference_frame.grid(row=0, column=1, padx=5, sticky="nsew")
        
        self.docs_frame = tk.Frame(self.content_frame, bg="white")
        self.docs_frame.grid(row=3, column=0, sticky="nsew", padx=5, pady=5)
        # ==========================
        # PERSONAL FRAME/ WORK FRAME/ STATUS FRAME
        # ==========================
        
        self.content_frame.grid_rowconfigure(0, weight=1)
        self.filler_frame = tk.Frame(self.content_frame, bg="#f5f5f5")
        self.filler_frame.grid(row=1, column=0, sticky="nsew")
        
        for i in range(3):
            self.top_frame.grid_columnconfigure(i, weight=1, uniform="group1")
# ============================ PERSONAL FRAME =======================================================================
        self.personal_frame = tk.Frame(self.top_frame, bg="white", bd=1, relief="solid")
        self.personal_frame.grid(row=0, column=0, padx=5, sticky="nsew")           
        self.personal_frame.grid_columnconfigure(0, weight=1)
        self.personal_frame.grid_columnconfigure(1, weight=1)
        tk.Label(self.personal_frame,
        text="Personal Information", bg="#1e3a5f", fg="white", font=("Calibri", 11, "bold"),
        anchor="center",padx=10).grid(row=0, column=0, columnspan=2, sticky="ew")
        
#WIDGETS INSIDE PERSONAL FRAME
        
        # EMPLOYEE NUMBER (Row 1)
        tk.Label(self.personal_frame,text="EMP No:", bg="white"
        ).grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.emp_no_var = tk.StringVar()
        tk.Entry(self.personal_frame, textvariable=self.emp_no_var,state="readonly",
            readonlybackground="#f0f0f0" ).grid(row=1, column=1, sticky="ew", padx=5, pady=5)
        
    #.....................NAME ...................................................................................
        tk.Label(self.personal_frame,
        text="Name *", bg="white").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.name_var = tk.StringVar()
        self.name = tk.Entry(self.personal_frame)
        self.name.grid(row=2, column=1, sticky="ew", padx=5, pady=5)
        self.name.bind("<KeyPress>", self.handle_name_input)
        
    #...................DATE OF BIRTH ENTRY........................................................................
        self.dob_var = tk.StringVar()
        tk.Label(self.personal_frame,text="Date of Birth (DD-MM-YYYY)", bg="white").grid(row=3, column=0, sticky="w", padx=(5,0), pady=5)
        self.dob_entry = tk.Entry(self.personal_frame)
        self.dob_entry.grid(row=3, column=1, sticky="ew", padx=5, pady=5)
        self.dob_entry.insert(0, "__-__-____")
        
        
    #.................                    ..........................................................................
        self.cal_btn = tk.Button(self.personal_frame, text="📅", width=3, command=self.open_calendar)
        self.cal_btn.grid(row=3, column=2)
        self.dob_entry.icursor(0)
        self.dob_entry.bind("<KeyRelease>", self.handle_dob_key)
        self.dob_entry.bind("<FocusOut>",lambda e: (messagebox.showwarning("DOB Issue", self.validate_dob_full())
        if self.validate_dob_full() != "OK" else None))

    #......................EID ....................................................................................
        
        tk.Label(self.personal_frame, text="Emirates ID *", bg="white").grid(row=4, column=0, sticky="w", padx=5, pady=5)
        self.eid_var = tk.StringVar()
        # ✅ STORE ENTRY FIRST
        self.eid_entry = tk.Entry(self.personal_frame, textvariable=self.eid_var)
        self.eid_entry.grid(row=4, column=1, sticky="ew", padx=5, pady=5)
        self.eid_entry.insert(0, "784-XXXX-XXXXXXX-X")
        self.eid_entry.bind("<KeyPress>", self.handle_eid_key)
        self.eid_entry.bind("<FocusOut>", lambda e: self.validate_eid())
        
    #------------------- MOBILE NUMBER-------------------------------------------------------------------------------
        tk.Label(self.personal_frame, text="Contact Mobile Number*", bg="white").grid(row=5, column=0, sticky="w", padx=5, pady=5)
        self.mobile_var = tk.StringVar()
        # ✅ STORE ENTRY FIRST
        vcmd = (self.personal_frame.register(self.validate_mobile_input), "%P")
        self.mobile_entry = tk.Entry(self.personal_frame, textvariable=self.mobile_var, validate="key",
        validatecommand=vcmd)                           
        self.mobile_entry.grid(row=5, column=1, sticky="ew", padx=5, pady=5)
        self.mobile_entry.bind("<FocusOut>", self.on_mobile_focus_out)
        self.mobile_status = tk.Label(self.personal_frame,text="", bg="white",font=("Calibri", 9))
        self.mobile_status.grid(row=6, column=1, sticky="w", padx=5)
#---------------------.NATIONALITY .............................................................................
        tk.Label(self.personal_frame,text="Nationality", bg="white").grid(row=6, column=0, sticky="w", padx=5, pady=5)
        self.nationality_var = tk.StringVar()
        self.nationality_combo = ttk.Combobox(self.personal_frame, textvariable=self.nationality_var,
        values=["Indian", "Pakistani", "Nepali", "Bangladeshi", "Sri Lankan", "Other"],
        state="readonly")
        self.nationality_combo.grid(row=6, column=1, sticky="ew", padx=5, pady=5)
# ======================== WORK FRAME ================================================================================

        self.work_frame = tk.Frame(self.top_frame, bg="white", bd=1, relief="solid")
        self.work_frame.grid(row=0, column=1, padx=5, sticky="nsew")
        self.work_frame.grid_columnconfigure(0, weight=1)
        self.work_frame.grid_columnconfigure(1, weight=1)
        tk.Label(
        self.work_frame,
        text="Work Information",bg="#1e3a5f",fg="white",font=("Calibri", 11, "bold"),anchor="center",
        padx=10).grid(row=0, column=0, columnspan=2, sticky="ew")
        
    #..........................................JOINING DATE ---------------------------------------------------
        self.jdt_var = tk.StringVar()
        tk.Label(self.work_frame,text="Joining Date (DD-MM-YYYY)", bg="white").grid(row=2, column=0, sticky="w", padx=(5,0), pady=5)
        self.jdt_entry = tk.Entry(self.work_frame, textvariable=self.jdt_var)
        self.jdt_entry.grid(row=2, column=1, sticky="ew", padx=5, pady=5)
        self.jdt_entry.insert(0, "DD-MM-YYYY")
        self.jdt_entry.icursor(0)
        self.jdt_entry.config(fg="grey")
        
        self.jdt_entry.bind("<KeyRelease>", self.handle_jdt_key)
        self.jdt_entry.bind("<FocusOut>", self.on_jdt_focus_out)
        self.jdt_btn = tk.Button(self.work_frame, text="📅", width=3, command=self.open_calandar)
        self.jdt_btn.grid(row=2, column=2)
       
        
        
    #....................................... Role / Designation-------------------------------------------------
        
        tk.Label(self.work_frame,text="Role/Designation:", bg="white").grid(row=3, column=0, sticky="w", padx=5, pady=5)
        self.emp_role = tk.StringVar()
        self.role_combo = ttk.Combobox(
            self.work_frame,
            textvariable=self.emp_role,
            values=["Driver", "Salesman(Delivery Boy)", "Supervisor","Manager"],
            state="readonly")
        self.role_combo.grid(row=3, column=1, sticky="ew", padx=5, pady=5)
        self.role_combo.bind("<<ComboboxSelected>>", self.on_role_change)
        self.license_frame = tk.Frame(self.work_frame, bg="white")
        self.license_frame.grid(row=4, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
        self.license_frame.grid_remove()
        # Prepare variables
        # License Frame (hidden initially)
        # Title
        tk.Label(
            self.license_frame,
            text="Driving License Categories",
            bg="#e6f2ff",
            font=("Calibri", 10, "bold")
        ).grid(row=0, column=0, sticky="ew", pady=3)

        # Prepare variables
        self.license_vars = {}
        self.license_checkboxes = {}
        row = 1  # Start from 1 (important)
   
        for code, data in self.license_categories.items():
            var = tk.IntVar()
            self.license_vars[code] = var

            chk = tk.Checkbutton(
                self.license_frame,
                text=f"{code} - {data['title']}",
                variable=var,
                command=lambda c=code: self.on_category_selected(c),
                bg="white",
                anchor="w")
            chk.grid(row=row, column=0, sticky="w", padx=10)

            # ✅ THIS LINE IS MANDATORY
            self.license_checkboxes[code] = chk
            row += 1
        
        self.set_btn = tk.Button(self.license_frame,text="SET",bg="#1e3a5f",fg="white",command=self.toggle_category_mode)
        self.set_btn.grid(row=row, column=0, pady=5, sticky="ew")
      
        
# ========================= STATUS FRAME =============================================================================
        self.status_frame = tk.Frame(self.top_frame, bg="white", bd=1, relief="solid")
        self.status_frame.grid(row=0, column=2, padx=5, sticky="nsew")
        self.status_frame.grid_columnconfigure(0, weight=1)
        self.status_frame.grid_columnconfigure(1, weight=1)
        tk.Label(
        self.status_frame,text="Status & Control",bg="#1e3a5f",
        fg="white", font=("Calibri", 11, "bold"), anchor="center",padx=10).grid(row=0, column=0, columnspan=2, sticky="ew")
#-------------------STATUS----------------------------------------------------------------------------------------------
        tk.Label(self.status_frame,text="Employee Status:", bg="white").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.emp_status = tk.StringVar()
        self.empstatus_combo = ttk.Combobox(self.status_frame,
            textvariable=self.emp_status,
            values=["Active", "Inactive/Absconding", "Resigned","Terminated", "On Leave"],
            state="readonly")
        self.empstatus_combo.grid(row=1, column=1, sticky="ew", padx=5, pady=5)
        self.empstatus_combo.bind("<<ComboboxSelected>>", self.on_status_change)
       
#-------------------------- AVAILABILITY---------------------------------------------------------------------------
        tk.Label(self.status_frame,text="Employee Availability:", bg="white").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.availability_var = tk.StringVar()
        self.availability_var.set("Available")
        self.avail_combo = ttk.Combobox(self.status_frame,textvariable=self.availability_var,
            values=["Available", "Not Available"], state="readonly")
        self.avail_combo.grid(row=2, column=1, sticky="ew", padx=5, pady=5)
        
#------------------------ EXIT DATE -------------------------------------------------------------------------------

        self.exit_dt = tk.StringVar()
        tk.Label(self.status_frame,text="Exit Date (DD-MM-YYYY)", bg="white").grid(row=3, column=0, sticky="w", padx=(5,0), pady=5)
        self.exit_entry = tk.Entry(self.status_frame, textvariable=self.exit_dt)
        self.exit_entry.grid(row=3, column=1, sticky="ew", padx=5, pady=5)
        self.exit_entry.insert(0, "DD-MM-YYYY")
        self.exit_entry.icursor(0)
        self.exit_entry.config(state="disabled")
        self.empstatus_combo.bind("<<ComboboxSelected>>", self.on_status_change)
        

# ========================================================================================================
        # COMMON UIs
# ========================================================================================================
      # BUTTON FRAME FOR COMMAND BUTTONS 
        self.button_frame = tk.Frame(self.content_frame)
        self.button_frame.grid(row=4, column=0, sticky="ew", pady=5)

        # Configure columns
        for i in range(5):
            self.button_frame.grid_columnconfigure(i, weight=1)

        # MESSAGE LABEL (BOTTOM)
        self.message_var = tk.StringVar()
        self.message_label = tk.Label(
            self.content_frame,
            textvariable=self.message_var,
            bg="#f0f0f0",
            fg="black",
            font=("Calibri", 10, "bold"),
            anchor="center",
            relief="solid",
            bd=1,
            height=2
        )
        self.message_label.grid(row=5, column=0, sticky="ew", padx=5, pady=(0,10))

        # COMMAND BUTTONS
        self.save_btn = tk.Button(self.button_frame, text="SAVE", command=self.save_vehicle, height=2)
        self.save_btn.grid(row=0, column=0, padx=5, sticky="ew")

        self.new_btn = tk.Button(self.button_frame, text="NEW EMPLOYEE", command=self.new_vehicle, height=2)
        self.new_btn.grid(row=0, column=1, padx=5, sticky="ew")
        self.new_btn.config(state="normal")

        self.close_btn = tk.Button(self.button_frame, text="CLOSE", command=self.form_close, height=2)
        self.close_btn.grid(row=0, column=2, padx=5, sticky="ew")
        
        self.initialize_form_state()
     #.--------------------------------OPERATION FUNCTIONS ----------------------------------------..............----
     
    # USER DEFINED FUNCTIONS 
    def new_vehicle(self): 
        self.reset_form_fields()
        self.set_form_editable(True)
        self.new_btn.config(state="disabled")
        self.save_btn.config(state="normal")
        self.show_message('Ready. Enter new employee details and click "SAVE".', "info")
        self.name.focus_set()

    def initialize_form_state(self):
        self.reset_form_fields()
        self.set_form_editable(False)
        self.save_btn.config(state="disabled")
        self.new_btn.config(state="normal")
        self.show_message('Please click on the "NEW" button to record new employee details.', "info")

    def set_form_editable(self, editable):
        entry_state = "normal" if editable else "disabled"
        combo_state = "readonly" if editable else "disabled"
        status = self.emp_status.get().strip()

        for widget in [self.name, self.dob_entry, self.eid_entry, self.mobile_entry, self.jdt_entry]:
            widget.config(state=entry_state)

        for widget in [self.role_combo, self.nationality_combo, self.empstatus_combo, self.avail_combo]:
            widget.config(state=combo_state)

        self.cal_btn.config(state=entry_state)
        self.jdt_btn.config(state=entry_state)

        for checkbox in self.license_checkboxes.values():
            checkbox.config(state=entry_state)
        self.set_btn.config(state=entry_state)

        if editable and status in ["Resigned", "Terminated"]:
            self.exit_entry.config(state="normal")
        else:
            self.exit_entry.config(state="disabled")

    def reset_form_fields(self):
        self.emp_no_var.set("")
        self.name.delete(0, tk.END)
        self.dob_entry.config(state="normal")
        self.dob_entry.delete(0, tk.END)
        self.dob_entry.insert(0, "__-__-____")

        self.eid_entry.config(state="normal")
        self.eid_entry.delete(0, tk.END)
        self.eid_entry.insert(0, "784-XXXX-XXXXXXX-X")
        self.eid_entry.icursor(9)

        self.mobile_var.set("")
        self.mobile_entry.config(fg="black")
        self.mobile_status.config(text="", fg="black")

        self.nationality_var.set("")
        self.emp_role.set("")
        self.jdt_var.set("")
        self.jdt_entry.config(state="normal")
        self.jdt_entry.delete(0, tk.END)
        self.jdt_entry.insert(0, "DD-MM-YYYY")
        self.jdt_entry.config(fg="grey")

        self.emp_status.set("")
        self.availability_var.set("Available")
        self.exit_dt.set("")
        self.exit_entry.config(state="normal")
        self.exit_entry.delete(0, tk.END)
        self.exit_entry.insert(0, "DD-MM-YYYY")
        self.exit_entry.config(state="disabled")

        for var in self.license_vars.values():
            var.set(0)
        for checkbox in self.license_checkboxes.values():
            checkbox.grid()
            checkbox.config(state="normal", bg="white")
        self.set_btn.config(text="SET", bg="#1e3a5f")
        self.category_mode = "SET"
        self.license_frame.grid_remove()
         
    def save_vehicle(self): 
        name = self.name.get().strip()
        eid = self.eid_entry.get().strip()
        role = self.emp_role.get().strip()
        status = self.emp_status.get().strip()
        availability = self.availability_var.get().strip()
        nationality = self.nationality_var.get().strip()
        dob = self.dob_entry.get().strip()
        mobile = self.mobile_var.get().strip()
        join_date = self.jdt_var.get().strip()
        exit_date = self.exit_dt.get().strip()

        if not name:
            self.show_message("Employee name is required.", "warning")
            self.name.focus_set()
            return
        if not eid or "X" in eid:
            self.show_message("Enter a complete Emirates ID.", "warning")
            self.eid_entry.focus_set()
            return
        if not EmiratesIDValidator.is_valid_format(eid):
            self.show_message("Invalid Emirates ID format. Use 784-YYYY-XXXXXXX-X.", "error")
            self.eid_entry.focus_set()
            return
        if not role:
            self.show_message("Role/Designation is required.", "warning")
            self.role_combo.focus_set()
            return
        if not status:
            self.show_message("Employee status is required.", "warning")
            self.empstatus_combo.focus_set()
            return
        if not availability:
            self.show_message("Employee availability is required.", "warning")
            self.avail_combo.focus_set()
            return

        if dob and dob != "__-__-____":
            try:
                datetime.strptime(dob, "%d-%m-%Y")
            except ValueError:
                self.show_message("Date of Birth must be in DD-MM-YYYY format.", "error")
                self.dob_entry.focus_set()
                return

        if join_date and join_date != "DD-MM-YYYY":
            if not self.validate_joining_date():
                self.show_message("Joining date is invalid.", "error")
                return
        else:
            join_date = ""

        if status in ["Resigned", "Terminated"]:
            if not exit_date or exit_date == "DD-MM-YYYY":
                self.show_message("Exit date is required for selected status.", "warning")
                self.exit_entry.focus_set()
                return
        if exit_date and exit_date != "DD-MM-YYYY":
            try:
                datetime.strptime(exit_date, "%d-%m-%Y")
            except ValueError:
                self.show_message("Exit date must be in DD-MM-YYYY format.", "error")
                self.exit_entry.focus_set()
                return
        else:
            exit_date = ""

        if mobile:
            mobile_result = PhoneValidator.process_uae_number(mobile)
            if not mobile_result["valid"]:
                self.show_message(f"Invalid mobile number: {mobile_result['error']}", "error")
                self.mobile_entry.focus_set()
                return
            mobile = mobile_result["formatted"]

        db_path = self.get_database_path()

        try:
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT employee_id FROM employees WHERE TRIM(eid)=?", (eid,))
                duplicate_row = cursor.fetchone()
                if duplicate_row:
                    self.show_message("Emirates ID already exists for another employee.", "error")
                    self.eid_entry.focus_set()
                    return

                cursor.execute("""
                    INSERT INTO employees (
                        name, role, eid, nationality, dob, mobile, status,
                        availability, join_date, exit_date
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    name, role, eid, nationality, dob, mobile, status,
                    availability, join_date, exit_date
                ))

                employee_id = cursor.lastrowid
                self.emp_no_var.set(str(employee_id))
                self.save_employee_documents(conn, employee_id, name)
                conn.commit()

            self.show_message("Employee record saved successfully.", "success")
            self.set_form_editable(False)
            self.save_btn.config(state="disabled")
            self.new_btn.config(state="normal")
            self.show_message('Employee saved. Click "NEW" to record another employee.', "success")
        except sqlite3.Error as error:
            self.show_message(f"Failed to save employee: {error}", "error")
        except Exception as error:
            self.show_message(f"Unable to save employee documents: {error}", "error")
     
    def form_close(self): 
        sure=messagebox.askyesno("FTMS PRO:","Are you sure you want to Exit?") 
        if sure: 
            self.parent.grab_release() 
            self.parent.destroy() 
            self.controller.set_form_mode(False) 
            self.controller.clear_content_area() 
            
    #==================================== HELPER FUNCTIONS ===========================================================
    def open_calendar(self):
        top = tk.Toplevel(self.parent)
        top.title("Select Date of Birth")

        cal = Calendar(
            top,
            selectmode="day",
            date_pattern="dd-mm-yyyy"
        )
        cal.pack(padx=10, pady=10)

        def set_date():
            selected_date = cal.get_date()
            self.dob_entry.delete(0, tk.END)
            self.dob_entry.insert(0, selected_date)
            top.destroy()
            # ✅ Trigger validation immediately
            result = self.validate_dob_full()
            if result != "OK":
                messagebox.showwarning("DOB Issue", result)
        # ✅ Button must be OUTSIDE function
        tk.Button(top, text="OK", command=set_date).pack(pady=5)
        

    
    
    def dob_keypress(self, event):
        value = self.dob_var.get()
        #REMOVING SPACE AND CHARACTERS
        digits = ''.join(filter(str.isdigit, value))
        #LIMIT TO 8 DIGITS (DDMMYYYY)
        digits = digits[:8]
        if len(digits) >=5:
            formatted = f"{digits[:2]}-{digits[2:4]}-{digits[4:]}"
        elif len(digits) >= 3:
            formatted = f"{digits[:2]}-{digits[2:]}"
        else:
            formatted = digits
        self.dob_var.set(formatted)
        self.dob_entry.icursor(len(formatted))
        
    
    def validate_dob(self):
        dob = self.dob_entry.get()
        try:
            dob_date = datetime.strptime(dob, "%d-%m-%Y")
            return True
        except:
            return False
        
    def check_age(self):
        dob = self.dob_entry.get()
        try:
            dob_date = datetime.strptime(dob, "%d-%m-%Y")
            today = datetime.today()

            age = today.year - dob_date.year - (
                (today.month, today.day) < (dob_date.month, dob_date.day)
            )

            if age < 18 or age > 60:
                return False
            return True
        except:
            return False
        
    def validate_dob_full(self):
        if not self.validate_dob():
            self.dob_entry.focus_set()
            return "Invalid Date Format"
        if not self.check_age():
            self.dob_entry.focus_set()
            self.dob_entry.icursor(tk.END)
            return "Age must be between 18 and 60"
    #-------------- GETTING YEAR TO THE EID ENTRY---------------------------------------------------
        self.dob_var.set(self.dob_entry.get())
        year = self.dob_var.get().split("-")[2]
        current_eid = self.eid_entry.get()
        # ✅ MASKED FORMAT
        eid_mask = f"784-{year}-XXXXXXX-X"
        self.eid_entry.delete(0, tk.END)
        self.eid_entry.insert(0, eid_mask)
        
        if not current_eid.startswith(f"784-{year}-"):
            self.eid_entry.delete(0, tk.END)
            self.eid_entry.insert(0, f"784-{year}-")
            self.eid_entry.icursor(len(current_eid))
 
        # ✅ SET CURSOR TO FIRST X
        self.eid_entry.focus_set()
        self.eid_entry.icursor(9)
        return "OK"    
 
    def handle_dob_key(self,event):
        value = self.dob_entry.get()

        digits = ''.join(filter(str.isdigit, value))
        digits = digits[:8]

        if len(digits) >= 5:
            formatted = f"{digits[:2]}-{digits[2:4]}-{digits[4:]}"
        elif len(digits) >= 3:
            formatted = f"{digits[:2]}-{digits[2:]}"
        else:
            formatted = digits

        self.dob_entry.delete(0, tk.END)
        self.dob_entry.insert(0, formatted)
       
    def clear_placeholder(self, event):
        if self.dob_var.get()=="DD-MM-YYYY":
            self.dob_var.set("")
            
    def validate_eid(self):
        eid = self.eid_entry.get().strip()
        # Ignore empty or partially auto-filled
        if eid == "" or eid.startswith("784-") and len(eid) < 18:
            return
        if not EmiratesIDValidator.is_valid_format(eid):
            messagebox.showwarning("FTMS PRO","Invalid EID. Correct format:784-YYYY-XXXXXXX-X")
            
    def handle_eid_key(self, event):

        entry = self.eid_entry
        text = list(entry.get())
        
        if len(text) < 18:
            template = list("784-0000-XXXXXXX-X")
            for i in range(len(text)):
                template[i] = text[i]
            text = template
        EDITABLE_POS = [9,10,11,12,13,14,15,17]

        pos = entry.index(tk.INSERT)

        # 🔒 LOCK PREFIX + YEAR
        if pos < 9:
            entry.icursor(9)
            return "break"

        # Allow TAB
        if event.keysym == "Tab":
            return

        # -------------------------
        # 🔙 BACKSPACE
        # -------------------------
        if event.keysym == "BackSpace":

            prev_positions = [p for p in EDITABLE_POS if p < pos]
            if not prev_positions:
                return "break"

            prev_pos = prev_positions[-1]
            text[prev_pos] = "X"   
            text[16] = "-"         

            entry.delete(0, tk.END)
            entry.insert(0, "".join(text))
            entry.icursor(prev_pos)

            return "break"

        # -------------------------
        # ⌦ DELETE
        # -------------------------
        if event.keysym == "Delete":

            if pos not in EDITABLE_POS:
                return "break"

            text[pos] = "X"

            entry.delete(0, tk.END)
            entry.insert(0, "".join(text))
            entry.icursor(pos)

            return "break"

        # -------------------------
        # 🔢 ONLY DIGITS
        # -------------------------
        if not event.char.isdigit():
            return "break"

        # -------------------------
        # 🔒 LIMIT TO 8 DIGITS
        # -------------------------
        filled_digits = sum(1 for i in EDITABLE_POS if i < len(text) and text[i].isdigit())

        if filled_digits >= 8 and pos not in EDITABLE_POS:
            return "break"

        # -------------------------
        # ✍️ INSERT DIGIT
        # -------------------------
        if pos not in EDITABLE_POS:
            next_positions = [p for p in EDITABLE_POS if p > pos]
            if not next_positions:
                return "break"
            pos = next_positions[0]

        text[pos] = event.char

        entry.delete(0, tk.END)
        entry.insert(0, "".join(text))

        # -------------------------
        # ➡ MOVE CURSOR (SKIP DASH at 16)
        # -------------------------
        next_positions = [p for p in EDITABLE_POS if p > pos]

        if next_positions:
            next_pos = next_positions[0]
        else:
            return "break"

        entry.icursor(next_pos)

        return "break"
    
# HELPER CONTROLLER NAME FIELD          
    def handle_name_input(self, event):
        entry = self.name
        # Allow control/navigation keys
        if event.keysym in ("BackSpace", "Left", "Right", "Tab", "Delete"):
            return

        # 🚫 Block non-alphabet (no digits, no symbols)
        if not (event.char.isalpha() or event.char == " "):
            return "break"

        # ✅ Convert to uppercase AFTER key is inserted
        entry.after(1, lambda: self._to_upper(entry))

    def _to_upper(self, entry):
        pos = entry.index(tk.INSERT)
        text = entry.get().upper()
        entry.delete(0, tk.END)
        entry.insert(0, text)
        entry.icursor(pos)
        
    #-----------------------------------------------------------------------------------------------------------------
    #IF ROLE = DRIVER?
    def on_role_change(self, event):
        role = self.emp_role.get()

        if role == "Driver":
            # SHOW LICENSE FRAME
            self.license_frame.grid(row=4, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
        else:
            # HIDE LICENSE FRAME
            self.license_frame.grid_remove()
    #---------------- SHOWING DIFFERENT TYPES OF MESSAGES AS PER THE SITUATION----........-------------------------------
    
    def show_message(self, text, msg_type="info"):
        message_type = str(msg_type).strip().lower()
        colors = {
            "success": ("#d4edda", "#155724"),
            "error": ("#f8d7da", "#721c24"),
            "warning": ("#fff3cd", "#856404"),
            "info": ("#d1ecf1", "#0c5460")
        }
        bg, fg = colors.get(message_type, colors["info"])
        self.message_label.config(bg = bg, fg=fg)
        self.message_var.set(text)

    def get_database_path(self):
        preferred_path = "D:/FTMS PRO/ftms.db"
        if os.path.exists(preferred_path):
            return preferred_path
        return os.path.join(os.path.dirname(__file__), "ftms.db")

    def get_employee_documents(self):
        doc_map = {
            "Driving License Front": ["driving_license_front_path", "license_front_path", "dl_front_path"],
            "Driving License Back": ["driving_license_back_path", "license_back_path", "dl_back_path"],
            "Emirates ID Front": ["emirates_id_front_path", "eid_front_path"],
            "Emirates ID Back": ["emirates_id_back_path", "eid_back_path"]
        }

        selected_docs = {}
        for label, attributes in doc_map.items():
            path = ""
            for attribute in attributes:
                value = getattr(self, attribute, "")
                if value:
                    path = value
                    break
            selected_docs[label] = path

        if hasattr(self, "document_paths") and isinstance(self.document_paths, dict):
            for label in selected_docs.keys():
                selected_docs[label] = self.document_paths.get(label, selected_docs[label])

        return selected_docs

    def validate_document_file(self, file_path):
        if not file_path:
            return None
        allowed_types = {".jpg", ".jpeg", ".png", ".pdf"}
        extension = os.path.splitext(file_path)[1].lower()
        if extension not in allowed_types:
            return "Unsupported file type. Use JPG, JPEG, PNG, or PDF."
        max_file_size = 5 * 1024 * 1024
        if os.path.getsize(file_path) > max_file_size:
            return "File size must be 5MB or less."
        return None

    def save_employee_documents(self, conn, employee_id, employee_name):
        selected_docs = self.get_employee_documents()
        if not any(selected_docs.values()):
            return

        safe_employee_name = re.sub(r'[\\/:*?"<>|]+', "_", employee_name).strip()
        if not safe_employee_name:
            safe_employee_name = f"employee_{employee_id}"

        base_folder = "D:/FTMS PRO/employee_documents"
        employee_folder = os.path.join(base_folder, safe_employee_name)
        os.makedirs(employee_folder, exist_ok=True)

        cursor = conn.cursor()
        for label, source_path in selected_docs.items():
            if not source_path:
                continue

            validation_message = self.validate_document_file(source_path)
            if validation_message:
                raise ValueError(f"{label}: {validation_message}")

            extension = os.path.splitext(source_path)[1]
            target_path = os.path.join(employee_folder, f"{label}{extension}")
            shutil.copy2(source_path, target_path)

            cursor.execute(
                "INSERT INTO employee_documents (emp_id, doc_type, file_path) VALUES (?, ?, ?)",
                (employee_id, label, target_path)
            )
    
    def on_category_selected(self, code):
        data = self.license_categories[code]
        self.message = f"{code}: {data['title']} - {data['desc']}"
        self.show_message(self.message, "INFO")
        
    
    def toggle_category_mode(self):
        # =======================
        # SET MODE
        # =======================
        if self.category_mode == "SET":
            for code, var in self.license_vars.items():
                chk = self.license_checkboxes[code]
                if var.get() == 0:
                    chk.grid_remove()  # hide unselected
                else:
                    chk.config(state="disabled", bg="#d4edda")  # lock + highlight
            # Change button to EDIT
            self.set_btn.config(text="EDIT", bg="#ffc107")
            self.category_mode = "EDIT"

        # =======================
        # EDIT MODE
        # =======================
        else:
            for code, chk in self.license_checkboxes.items():
                chk.grid()  # show all
                chk.config(state="normal", bg="white")
            # Change button back to SET
            self.set_btn.config(text="SET", bg="#1e3a5f")
            self.category_mode = "SET"
            
    def on_mobile_focus_out(self, event=None):

        raw = self.mobile_var.get().strip()
        # If empty → clear everything
        if raw == "":
            self.mobile_status.config(text="", fg="black")
            self.mobile_entry.config(fg="black")
            return
        result = PhoneValidator.process_uae_number(raw)
        
        if result["valid"]:
            formatted = result["formatted"]
            # Only update if different (prevents unnecessary trigger)
            if self.mobile_var.get() != formatted:
                self.mobile_var.set(formatted)
        else:
            # ❌ Error feedback
            self.mobile_entry.config(fg="red")
            self.mobile_status.config(
                text=f"✖ {result['error']}",
                fg="red")
                
    def validate_mobile_input(self, value):
        if value == "":
            return True
        # Allow only digits and +
        if not all(c.isdigit() or c == "+" for c in value):
            return False
        # Optional: limit length
        digits = value.replace("+", "")
        if len(digits) > 12:
            return False
        return True
    
    
    def handle_jdt_key(self, event):
        value = self.jdt_var.get()
        # Remove everything except digits
        digits = "".join(filter(str.isdigit, value))
        # Limit to 8 digits (DDMMYYYY)
        digits = digits[:8]

        # Format as DD-MM-YYYY
        formatted = ""
        if len(digits) >= 2:
            formatted += digits[:2] + "-"
        else:
            formatted += digits

        if len(digits) >= 4:
            formatted += digits[2:4] + "-"
        elif len(digits) > 2:
            formatted += digits[2:]

        if len(digits) > 4:
            formatted += digits[4:]
            
        if len(self.jdt_var.get()) == 10:
            self.validate_joining_date()

        # Update without triggering infinite loop
        self.jdt_entry.delete(0, tk.END)
        self.jdt_entry.insert(0, formatted)
        
    def validate_joining_date(self):
        date_str = self.jdt_var.get()
        try:
            # Format check
            if len(date_str) != 10:
                raise ValueError("Invalid format")

            entered_date = datetime.strptime(date_str, "%d-%m-%Y").date()
            today = datetime.today().date()

            # 🚫 Future date check
            if entered_date > today:
                messagebox.showerror(
                    "Invalid Date",
                    "Joining date cannot be in the future"
                )
                self.jdt_entry.focus()
                return False
            return True

        except ValueError:
            messagebox.showerror("Invalid Date","Enter valid date in DD-MM-YYYY format")
        self.jdt_entry.focus()
        return False
    
    def on_jdt_focus_out(self, event):
        valid = self.validate_joining_date()
        if not valid:
            # allow user to stay but DO NOT trap
            self.jdt_entry.after(10, lambda: self.jdt_entry.focus_set())
        
    
    def open_calandar(self):
        top = tk.Toplevel(self.parent)
        top.title("Select Date of Joining")
        
        today = datetime.today().date()
        top.grab_set()  # modal window
        today = datetime.today()
        cal = Calendar(top,selectmode='day', date_pattern='dd-mm-yyyy',maxdate=today)
        cal.pack(padx=10, pady=10)

        def select_date():
            selected = cal.get_date()
            self.jdt_var.set(selected)
            self.jdt_entry.config(bg="white")  # reset error color
            top.destroy()

        tk.Button(top, text="Select", command=select_date).pack(pady=5)
        
    def on_status_change(self, event):
        status = self.empstatus_combo.get()
        if status == "Active":
            self.avail_combo.set("Available")
            self.avail_combo.config(state="readonly")
            self.exit_entry.config(state="disabled")

        elif status in ["Resigned", "Terminated"]:
            self.availability_var.set("Not Available")
            self.avail_combo.config(state="disabled")
            self.exit_entry.delete(0, tk.END)
            # Insert today's date in proper format
            self.exit_entry.config(state="normal")
            self.exit_entry.insert(0, datetime.today().strftime("%d-%m-%Y"))
         

        else:
            # For any other non-active status
            self.availability_var.set("Not Available")
            self.avail_combo.config(state="disabled")
            self.exit_entry.config(state="disabled")
            