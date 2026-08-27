import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import pandas as pd
from ui_components import create_header, create_page_title
from tkinter import LabelFrame
from datetime import datetime, date, timedelta
from tkinter import filedialog
from convert_pdf import ConvertPdf
import os
from tkcalendar import DateEntry

class VehicleReportPage:
    def __init__(self, parent, controller, filter_value="All Vehicles"):
        self.parent = parent
        self.controller = controller
        self.dashboard_filter = filter_value
        self.criteria_count=0
        self.brand_list=sorted(["TOYOTA","NISSAN", "MITSUBISHI", "ISUZU", "HYUNDAI", "KIA", "ASHOK LEYLAND", "TATA"])
        self.selected_brand=None
        self.cleared=False
        self.advanced_filtermode=False
        self.advanced_var=0
        self.criteria_list=[]
        self.criteria_set=set()
        self.criteria_boxes=[]
        self.result_labels = []
        self.plate_list=[]
        self._busy=False
        self.active_date_filter = None
        result_boxes = []
        titles = ["CRITERIA OUTPUT:", "MATCHING RECORDS:", "OUT OF: ", "MODE: "]
        self.conn = sqlite3.connect("ftms.db")
        
        self.numeric_fmap={          "year" : "year", 
                        "mulkiya issue date": "mulkiya_issue_date",
                       "mulkiya expiry date": "mulkiya_expiry_date",
                              "ton capacity": "ton_capacity",
                                  "odometer": "current_odometer"}
        
        # FIELD MAPPING. What HEADING is What FIELD?
        self.field_mapping={"vehicle number":"plate_source || '-' || plate_code || '-' || plate_number",
                                     "brand": "brand", 
                                     "model": "model", 
                                      "year": "year",
                              "ton capacity": "ton_capacity",
                                 "fuel type": "fuel_type",
                                 "body type": "body_type", 
                              "vehicle type": "vehicle_type",
                                 "tail lift": "tail_lift", 
                                  "odometer": "current_odometer",
                                    "status": "status",
                                "chassis no": "chassis_no",
                                 "engine no": "engine_no",
                            "ownership type": "ownership_type",
                        "mulkiya issue date": "mulkiya_issue_date",
                       "mulkiya expiry date": "mulkiya_expiry_date"}
                        
        columns=("vehicle number", "brand", "model", "year", "ton capacity", "body type", 
                 "vehicle type", "fuel type", "tail lift", "odometer", "status", "chassis no", 
                 "engine no", "ownership type", "mulkiya issue date", "mulkiya expiry date")
        self.column_map = {col:idx for idx, col in enumerate(columns)} # CREATING COLUMN MAP eg:- Plate Number = 0, 1, 2,
        
        #MAIN CONTAINER
        self.frame=tk.Frame(parent, bg="white")
        self.frame.grid(row=0, column=0, sticky="nsew") 
        self.frame.grid_rowconfigure(0, weight=0) #HEADER SPACE
        self.frame.grid_rowconfigure(1, weight=0) #TITLE
        self.frame.grid_rowconfigure(2, weight=0) #BUTTONS
        self.frame.grid_rowconfigure(3, weight=0) #ADVANCED FRAME
        self.frame.grid_rowconfigure(4, weight=0) #CRITERIA FRAME
        self.frame.grid_rowconfigure(5, weight=1) #SORT FRAME
        parent.grid_rowconfigure(0, weight=1)
        parent.grid_columnconfigure(0, weight=1)
        self.resetting_form=False
        #HEADER
        create_header(self.frame)
        #FORM CREATING SPACE
        self.center_frame=tk.Frame(self.frame, bg="#1e3a5f")
        self.center_frame.grid(row=1, column=0, sticky="nsew", padx=0, pady=1)
        self.center_frame.grid_rowconfigure(1, weight=1)
        self.center_frame.grid_columnconfigure(0, weight=1)
        
        # PAGE TITLE (STANDARD)
        create_page_title(self.center_frame, "Vehicles' Report")
        
        # ================= BUTTONS ====================================================================
        btn_frame = tk.Frame(self.frame, bg="white")
        btn_frame.grid(row=2, column=0, sticky="ew", pady=1)
        for i in range (6):
            btn_frame.grid_columnconfigure(i, weight=0)
           
        btn_style={"height":2, "font":("Segoe UI", 9, "bold")}
        
        tk.Button(btn_frame, text="Print Report", command=self.print_report, width=25, bg="#cfcfcf", fg="black", 
                  **btn_style).grid(row=0, column=0, padx=4, pady=3)
        
        tk.Button(btn_frame, text="Export As PDF", width=25, command=self.export_vehicle_pdf,
                  bg="#cfcfcf", fg="black", **btn_style).grid(
                      row=0, column=1, padx=4, pady=3)

        tk.Button(btn_frame, text="Close Report", width=25, command=self.close_report,
                  bg="#cfcfcf", fg="black", **btn_style).grid(
                      row=0, column=2, padx=2, pady=3)
        #FILTER COMBO BOX LABEL
        tk.Label(btn_frame, text="Report Filter:",  width=25,font=("Segoe UI", 12, 
                                                  "bold"), bg="white").grid(row=0, column=3,padx=0, pady=3)
                  
        #SORTING BY CUSTOM FIELD
        self.sort_frame=tk.Frame(self.frame, bg="#bac8e7", bd=1, relief="sunken",
                                 highlightbackground="#007807", highlightthickness=1)
        self.sort_frame.grid(row=4, column=0, columnspan=5, padx=2, pady=0, sticky="ew")
        tk.Label(self.sort_frame, text="SORT By:").grid(row=0, column=0, padx=2, pady=0)
        
        self.sort_var=tk.StringVar()
        self.sort_comb=ttk.Combobox(self.sort_frame, textvariable=self.sort_var, state="readonly", width=18)
        self.sort_comb.grid(row=0, column=1, padx=5)
        self.sort_comb['values'] = ("Brand", "Model", "Year", "Ton Capacity", 
                                      "Fuel Type", "Body Type","Vehicle Type", "Tail Lift", 
                                      "Odometer","Mulkiya Issue Date", "Mulkiya Expiry Date","Status")
        self.sort_comb.set("Select Field for Sorting")
        self.sort_order = tk.StringVar(value="ASC")
        self.sort_comb.bind("<<ComboboxSelected>>",lambda e: self.sort_treeview())
        self.sort_order.trace("w", lambda *args: self.sort_treeview())
        
        tk.Radiobutton(self.sort_frame,text="ASCENDING ⬆️", variable=self.sort_order, 
                       value="ASC", bg="#cfcfcf", fg="black").grid(row=0, column=2, padx=5)
        tk.Radiobutton(self.sort_frame,text="DESCENDING ⬇️", variable=self.sort_order, 
                       value="DESC", bg="#cfcfcf", fg="black").grid(row=0, column=3, padx=5)
      
        
        self.filter_var=tk.StringVar()
        self.filter_combo=ttk.Combobox(btn_frame, textvariable=self.filter_var, state="readonly", width=10)
        self.filter_combo['values']=("All Vehicles",
                                    "1 - Ton / Pickup",
                                    "1.5 - Ton",
                                    "3 - Light Truck",
                                    "5 - Medium Truck",
                                    "7 - Cargo Truck",
                                    "10 - Heavy Truck",
                                    "12 - Heavy Cargo",
                                    "15 - Large Cargo",
                                    "20 - Trailer",
                                    "25 - Heavy Trailer",
                                    "30 - Articulated Truck"
                                    "40 - Semi Trailer")
        self.filter_combo.current(0) # set default = All Vehicles
        self.filter_combo.grid(row=0, column=4, padx=5, sticky="w")
        self.filter_combo.bind("<<ComboboxSelected>>", self.apply_filter)
        
        #ADVANCED FILTER CHECK BUTTON
        self.advanced_var=tk.IntVar()
        self.advanced_chk=tk.Checkbutton(btn_frame,text="Advanced Filter", variable=self.advanced_var,
                                         command=self.toggle_filter_mode,font=("Segoe UI",10,"bold")).grid(row=0, column=5, padx=2)
                  
        self.adv_frame=tk.Frame(self.frame, bg="white", bd=1, relief="solid")
        self.adv_frame.grid(row=3, column=0, sticky="nsew", padx=0, pady=1)
        
        # COLUMNS LEFT FRAME           :              RIGHT FRAME
        self.adv_frame.grid_columnconfigure(0, weight=3) # TO EXPAND 
        # CRITERIA DISPLAY
        self.adv_frame.grid_columnconfigure(1, weight=2) # TO EXPAND 
        
        #ROWS
        self.adv_frame.grid_rowconfigure(0, weight=0) #for CONTROLS
        self.adv_frame.grid_rowconfigure(1, weight=1) #for CRITERIA DISPLAY
        
        title_label=tk.Label(self.adv_frame, text="Advanced  Filter", font=("Segoe UI", 10, "bold"), bg="white")
        title_label.place(relx=0.5, y=5, anchor="center")
        self.frame.grid_columnconfigure(0, weight=1)
        
        # BED ROOM FOR FIELD, OPERATOR & VALUE BOX (VALUE): adv_frame hall devided into thre rooms
        self.left_frame=tk.Frame(self.adv_frame, bg="white")
        #BED ROOM FOR THREE COMMAND BUTTONS
        self.left_frame.grid(row=0, column=0, sticky="w", pady=0)
        
        self.right_frame=tk.Frame(self.adv_frame, bg="white")
        self.right_frame.grid(row=0, column=1, sticky="e")
        self.right_frame.grid_columnconfigure(0, weight=0)
        self.right_frame.grid_columnconfigure(1, weight=0)
        self.right_frame.grid_columnconfigure(2, weight=0)
        self.right_frame.grid_columnconfigure(3, weight=0)
        self.right_frame.grid_columnconfigure(4, weight=0)
        self.right_frame.grid_columnconfigure(5, weight=0)
        self.right_frame.grid_columnconfigure(6, weight=0)
        self.right_frame.grid_columnconfigure(7, weight=1)
        
        
        #CRITERIA 3  FIXED BED ROOM (DISPLAY AREA)
        self.criteria_frame=tk.Frame(self.adv_frame, bg="white", bd=1, relief="solid")
        self.criteria_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=2, pady=0)
        
        #LEFT SIDE           : CRITETIA BOXES
        self.criteria_left = tk.Frame(self.criteria_frame, bg="#86c9f3")
        self.criteria_left.grid(row=0, column=0, sticky="nsew")
        
        
        #RIGHT SIDE CRITETIA : INFO SUMMARY
        self.criteria_right = tk.Frame(self.criteria_frame, bg="#8be3dd")
        self.criteria_right.grid(row=0, column=1, sticky="nsew", padx=5)
        self.criteria_right.grid_rowconfigure(0, weight=1)
        
        self.criteria_frame.grid_columnconfigure(0, weight=2)
        self.criteria_frame.grid_columnconfigure(1, weight=3)
        self.criteria_right.grid_columnconfigure(2, weight=1)
        self.criteria_right.grid_columnconfigure(3, weight=1)
        self.criteria_frame.rowconfigure(0, weight=1)
        
        for i in range(3):
            box=tk.Frame(self.criteria_left, bg="white", bd=1, relief="sunken", height=30)
            box.grid(row=0, column=i, sticky="nsew", padx=2, pady=1)
            self.criteria_left.grid_columnconfigure(i, weight=1)
            self.criteria_boxes.append(box)
 
        #THREE COLUMNS CREATING FOR THREE CRITERIA MESSAGES |BOX [i=0] |BOX[i=1] | BOX[i=2]
        for i in range(4):
            frame=tk.Frame(self.criteria_right, bg="white", bd=1, relief="sunken")
            frame.grid(row=0, column=i, sticky="nsew", padx=1)
            self.criteria_right.grid_columnconfigure(i, weight=1)
            
            title_label = tk.Label(frame, text=titles[i], bg="white", font=("Segoe UI", 10), 
                                  anchor="center", wraplength=150) #prevents more stretching
            title_label.pack(fill="x", pady=(2,0))
            #MAKE VALUE CENTER
            value_label = tk.Label(frame, text="", bg="white", font=("Segoe UI", 10,"bold"), 
                                   anchor="center", wraplength=150)
            value_label.pack(expand=True)
            self.result_labels.append(value_label)
        
        
        #WIDGETS INSIDE THE ADVANCED FILTER FRAME
        #COMBO FIELD LABEL
        tk.Label(self.left_frame, text="Field:", bg="white", 
                 font=("Segoe UI", 10,"bold")).grid(row=0, column=0, padx=5, pady=1, sticky="e")
        #FIELD COMBO WIDGET
        self.field_var = tk.StringVar()
        self.field_combo = ttk.Combobox(
        self.left_frame,
        textvariable=self.field_var,
        state="readonly",
        width=20)
        
        self.field_combo['values'] = ("vehicle number", "brand", "model", "year", "ton capacity", 
                                      "fuel type", "body type","vehicle type", "tail lift", 
                                      "odometer", "mulkiya issue date", "mulkiya expiry date",
                                      "status","chassis no", "engine no", "ownership type")
        self.field_combo.grid(row=0, column=1, padx=5, pady=1, sticky="w")
        self.field_combo.bind("<<ComboboxSelected>>", self.on_field_change)
        
        
        #Operator Label
        tk.Label(self.left_frame, text="Operator", bg="white", font=
                 ("Segoe UI", 10, "bold")).grid(row=0, column=2, padx=2, pady=1, sticky="e")

        # Operator
        self.op_var = tk.StringVar()
        self.op_combo = ttk.Combobox(
            self.left_frame,
            textvariable=self.op_var,
            state="readonly",
            width=10
        )
        self.op_combo['values'] = ("=", "!=","<", ">", "<=", ">=", "Contains", "Starts With")
        self.op_combo.grid(row=0, column=3, padx=2, pady=2, sticky="w")
        self.op_combo.current(0)
        
        #Value Label
        tk.Label(self.left_frame, text="Value", bg="white", font=
                 ("Segoe UI", 10, "bold")).grid(row=0, column=4, padx=2, pady=1, sticky="e")

        # Value Box 
        self.value_box = ttk.Combobox(self.left_frame, width=22)
        self.value_box.grid(row=0, column=5, padx=2, pady=1, sticky="ew")
        self.value_box.bind("<<ComboboxSelected>>",self.on_value_selected)
        self.value_box.bind("<Key>", self.clear_on_type,add="+")

        # Date fields use a calendar, not a list of historical database values.
        self.date_picker = DateEntry(
            self.left_frame, width=19, date_pattern="yyyy-mm-dd",
            state="readonly", background="#1e3a5f", foreground="white",
            borderwidth=1
        )
        self.date_picker.bind("<<DateEntrySelected>>", self.on_date_selected)

        # Intelligent expiry windows stay close to the date input and use the
        # same compact report-filter styling.
        self.date_filter_frame = tk.Frame(self.left_frame, bg="white")
        self.date_filter_frame.grid(row=1, column=0, columnspan=6, padx=5, pady=(3, 1), sticky="w")
        tk.Label(self.date_filter_frame, text="Expiry intelligence:", bg="white",
                 font=("Segoe UI", 9, "bold")).grid(row=0, column=0, padx=(0, 4))
        quick_style = {"bg": "#cfcfcf", "fg": "black", "font": ("Segoe UI", 8), "relief": "raised"}
        for column, (label, key) in enumerate((
            ("Expired", "expired"), ("Today", "today"),
            ("Next 7 Days", "next_7"), ("Next 30 Days", "next_30"),
            ("Custom Range", "custom"),
        ), start=1):
            tk.Button(self.date_filter_frame, text=label,
                      command=lambda value=key: self.apply_date_quick_filter(value),
                      **quick_style).grid(row=0, column=column, padx=2)

        self.custom_range_frame = tk.Frame(self.date_filter_frame, bg="white")
        tk.Label(self.custom_range_frame, text="From", bg="white", font=("Segoe UI", 8)).grid(row=0, column=0, padx=(6, 2))
        self.range_start_picker = DateEntry(self.custom_range_frame, width=11, date_pattern="yyyy-mm-dd", state="readonly")
        self.range_start_picker.grid(row=0, column=1, padx=2)
        tk.Label(self.custom_range_frame, text="To", bg="white", font=("Segoe UI", 8)).grid(row=0, column=2, padx=(4, 2))
        self.range_end_picker = DateEntry(self.custom_range_frame, width=11, date_pattern="yyyy-mm-dd", state="readonly")
        self.range_end_picker.grid(row=0, column=3, padx=2)
        tk.Button(self.custom_range_frame, text="Apply", command=self.apply_custom_date_range,
                  **quick_style).grid(row=0, column=4, padx=(3, 0))
        self.date_filter_frame.grid_remove()
        
        #RADIO BUTTON FOR QUERY AND/OR
       
        self.logic_var = tk.StringVar(value="AND")
        tk.Radiobutton(self.right_frame,text="And", variable=self.logic_var,value="AND")\
            .grid(row=0, column=1, padx=2, sticky="w")
        tk.Radiobutton(self.right_frame, text="OR", variable=self.logic_var, value="OR")\
            .grid(row=0, column=2, padx=2, sticky="w")
            
        # Add Criteria (+)
        self.add_btn = tk.Button(
            self.right_frame, text="Add Criteria", width=12,command=self.add_criteria,
            bg="#cfcfcf", fg="black", font=("Segoe UI", 10)
        )
        self.add_btn.grid(row=0, column=3, padx=2, pady=1)
        
        # Delete Criteria (-)
        self.delete_btn = tk.Button(
            self.right_frame, text="Delete Criteria", width=12, command=self.delete_criteria,
            bg="#cfcfcf", fg="black", font=("Segoe UI", 10)
        )
        self.delete_btn.grid(row=0, column=4, padx=2, pady=1)
        
        # SEARCH BUTTON
        self.search_btn = tk.Button(
            self.right_frame, text="SEARCH", width=12, command=self.search_button_click,
            bg="#cfcfcf", fg="black", font=("Segoe UI", 10)
        )
        self.search_btn.grid(row=0, column=5, padx=2, pady=1)
        
        # CLEAR SEARCH BUTTON
        self.clear_searchbtn=tk.Button(
            self.right_frame, text="Clear Search", width=12,command=self.clear_search,
            bg="#cfcfcf", fg="black", font=("Segoe UI", 10)
        ) 
        self.clear_searchbtn.grid(row=0, column=6,padx=2, pady=1)
        
        self.disable_advanced_filter()
        self.field_combo.focus()
        
        # ================= TABLE =================================================================
        
        table_frame = tk.Frame(self.frame, bg="white", bd=2, relief="solid")
        
        #border
        table_frame.grid(row=5, column=0, sticky="nsew", padx=0, pady=0)
        
        #PARENT EXPANSION
        self.frame.grid_rowconfigure(5, weight=1) # UPTO 5 ROWS
        
        #INNER CONTAINER
        container=tk.Frame(table_frame)
        container.grid(row=0, column=0, sticky="nsew", padx=0, pady=1)
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        
        #DEFINE COLUMNS
        style=ttk.Style()
        style.configure("Treeview", rowheight=20)
        style.theme_use("default")
        
        self.tree=ttk.Treeview(container, columns=columns, show="headings")
        self.tree.grid(row=0, column=0, sticky="nsew")
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center", stretch=True)

        #SCROLL BARS INSIDE CONTAINERS
        style.configure("Vertical.TScrolbar", gripcount=0, background="#4a6fa5", 
                        darkcolour="#4a6fa5", bordercolor="#e0e0e0", arrowcolor="white")
        y_scroll=ttk.Scrollbar(container, orient="vertical", command=self.tree.yview)
        x_scroll=ttk.Scrollbar(container, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)
        y_scroll.grid(row=0, column=1, sticky="ns")
        x_scroll.grid(row=1, column=0, sticky="ew")
        
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        if filter_value == "ALL":
            self.load_data()
        else:
            self.filter_var.set(str(filter_value))
            self.load_data(str(filter_value))
        
    # ================= DIFFERENT FUNCTIONS & DUTIES  ===//        ADD CRITERIA   //===============
    
    def add_criteria(self):
            #STORING VALUES BY REMOVING SPACE, converting to lower case
            field = self.field_var.get().strip()
            operator = self.op_var.get().strip()
            value = (self.date_picker.get_date().strftime("%Y-%m-%d")
                     if self.is_date_field() else self.value_box.get().strip())
            compare_key = (field, operator, value)
            #NORMALIZING VALUES RECEIVED
            n_field = self.normalize(field)
            n_operator = self.normalize(operator)
            n_value = self.normalize(value)
            
            #CHECKING IF ALL THE REQUIRED FIELDS/OPERATOR/VALUE ARE VALID-------------------------?            
            if not field or "select" in n_field:
                messagebox.showwarning("FTMS PRO: WARNING", "Please Select a valid field")
                return
            if not operator or "select" in n_operator:
                messagebox.showwarning("FTMS PRO: WARNING", "Please Select a valid operator")
                return
            if not value or "type" in n_value or "select" in n_value:
                messagebox.showwarning("FTMS PRO: WARNING", "Please Enter/Select a proper value")
                return
            
            #--------------------NUMERIC FIELD VALIDATION------------------------------------------
            numeric_fields = ["year", "ton capacity", "odometer", "mulkiya issue date", 
                              "mulkiya expiry date"]
            if not value.strip():
                messagebox.showwarning("FTMS PRO: WARNING", "Please enter a value")
                return
            if  n_value in ["none", "null"]:
                messagebox.showwarning("FTMS PRO: WARNING", "Invalid value entered")
                return
            
            #CHECKING CRITERIA COUNT REACHED: 3
            if len(self.criteria_list)>=3:
                messagebox.showwarning("FTMS PRO: WARNING", "Maximum three Criterias are allowed")
                self.add_btn.config(state="disabled")
                return
            #CHECKING COMPARISION FOR DUPLICATE
            if compare_key in self.criteria_set:
                messagebox.showwarning("FTMS PRO: WARNING", "Duplicate Criteria not allowed")
                return
            if self.logic_var.get()=="AND":
                for c in self.criteria_list:
                    if c.get("field")==field:
                        messagebox.showwarning("FTMS PRO: WARNING", 
                                               f"'{field}' cannot be used multiple times with AND condition")
                        return 
            self.criteria_set.add(compare_key)
            index=len(self.criteria_list)
            logic="" if index==0 else self.logic_var.get() # STORING RADIO BUTTON VALUE if not the first time
            box=self.criteria_boxes[index]
            # INCREMENT HAPPENING EACH TIME WHEN APPEND and STORING three criteria text 
            self.criteria_list.append({"field": field,
                                        "operator":operator,
                                        "value": value,
                                        "logic": logic,
                                        "compare_text": compare_key
                                        }) 
            #STORING THE CRITERIA FOR DISPLAY 
            criteria_text= f"{logic} {field} {operator} {value}".strip()
            #SETTING AS LABEL FOR DISPLAY
            label=tk.Label(box, text= criteria_text, bg="white", anchor="w")
            #SHOWING LABEL
            label.grid(row=0, column=0)
            #SHOWING THE CRITERIA BOX
            box.grid()
            self.delete_btn.config(state="normal")
            self.search_btn.config(state="active")
            self.search_btn.focus()
   #====================================== DELETE CRITERIA ========================================
   
    def delete_criteria(self):
        if not self.criteria_list:
            if self.delete_btn["state"]=="normal":
                messagebox.showwarning("FTMS PRO: WARNING", "No Criteria to Remove")
                self.delete_btn.config(state="disabled")
            return
        index = len(self.criteria_list)-1
        removed=self.criteria_list.pop()
        key=removed.get("compare_key") or removed.get("compare_text")
        # REMOVING FROM LIST
        if key:
            self.criteria_set.discard(key)
        box=self.criteria_boxes[index]
        #CLEARING THE CONTENT ONLY ONE BY ONE
        for w in box.winfo_children():
            w.destroy()
            #REMOVING FROM LIST
        box.grid_remove()
        self.add_btn.config(state="normal")
        if not self.criteria_list:
            self.delete_btn.config(state="disabled")
            
    #=================================== NORMALIZE=================================================
   
    def normalize(self, text):
        return str(text).strip().lower()
    
    #YEAR SETTING IN THE VALUE BOX FOR SEARCHING YEAR OF VEHICLE===================================
    def set_year_mode(self):
        current_year=datetime.now().year
        years=[str(y) for y in range(current_year-20, current_year+1)]
        self.value_box['values']=years
        self.cleared=False
        
    #CLEARING SEARCH===============================================================================
    
    def clear_search(self):
        self.delete_criteria()
        for box in self.criteria_boxes:
            for widget in box.winfo_children():
                widget.destroy()
        self.criteria_set.clear()
        for box in self.criteria_boxes:
            box.grid_remove()
        self.load_data() # ALL DATA WILL BE DISPLAYED WITHOUT CRITERIA
        # RESETTING INPUT WIDGETS
        self.field_var.set("Select Field")
        self.op_var.set("=")
        self.value_box.delete(0, "end")
        self.active_date_filter = None
        self.hide_date_controls()
        self.result_labels[3].config(text="")
        self.search_btn.config(state="disabled")
        
    #IF THE USER SELECTED STATUS: DIFFERENT STATUS=================================================
    
    def set_status_values(self):
        status_values=("Active", "Under Repair", "Sold Out", "Scrap", "Rented-Out", "Rented-In")
        self.value_box['values']=status_values
        self.value_box.current(0)
    
    # 1. APPLYING FILTER===========================================================================
    
    def apply_filter(self, event=None):
        selected=self.filter_var.get()
        self.disable_advanced_filter()
        self.active_date_filter = None
        if selected=="All Vehicles":
            self.load_data()
        else:
            self.load_data(filter_value=selected)
            
    
    # REPORT FILTER WORKS BASED ON FILTER TON CAPACITY VEHICLES====================================
    
    def load_data(self,filter_value=None, criteria_list=None, date_range=None):
        
        try:
            conn = sqlite3.connect("D:/FTMS PRO/ftms.db")
            cursor = conn.cursor()
            self.tree.delete(*self.tree.get_children())
            conditions = []
            parameters = []

            # BASE QUERY
            query = """
            SELECT plate_source || '-' || plate_code || '-' || plate_number,
                brand, model, year, ton_capacity, body_type, vehicle_type, fuel_type, tail_lift, 
                current_odometer, status, chassis_no, engine_no, ownership_type, mulkiya_issue_date,
                mulkiya_expiry_date FROM vehicles """
            # A calendar range takes priority while preserving the current report
            # layout and table.  The upper bound is inclusive for operational use.
            if date_range:
                column, start, end, _label = date_range
                if column not in ("mulkiya_issue_date", "mulkiya_expiry_date"):
                    raise ValueError("Unsupported date field")
                conditions.append(f"DATE({column}) BETWEEN DATE(?) AND DATE(?)")
                parameters.extend((start, end))

            if criteria_list:
                criteria_clause = self.build_where_clause(criteria_list)
                if criteria_clause:
                    conditions.append(f"({criteria_clause})")

            if filter_value and filter_value != "All Vehicles":
                ton = float(filter_value.split("-")[0].strip())
                conditions.append("ton_capacity = ?")
                parameters.append(ton)

            if conditions:
                query += " WHERE " + " AND ".join(conditions)
            cursor.execute(query, parameters)
            rows = cursor.fetchall()
            # CLEAR OLD DATA
            for row in rows:
                self.tree.insert("", "end", values=row)
        except Exception as e:
            messagebox.showerror("FTMS PRO: Error", str(e))
        conn.close()
        
    #===========================================CLEAR ON TYPING ===================================
        
    def clear_on_type(self, event):
        if not self.cleared:
            self.value_box.delete(0, tk.END)
            self.cleared=True

    #PLATE NUMBER AUTO SUGGESTION FUNCTION IN ADVANCED FILTER======================================
    
    def filter_plate(self, event):
        typed=self.value_box.get()
        if typed=="":
            self.value_box['values']=self.plate_list
            return
        filtered=[]
        for plate in self.plate_list:
            if typed.lower() in plate.lower():
                filtered.append(plate)
            self.value_box['values']=filtered
            
    def get_distinct_values(self, column):
        query= f"SELECT DISTINCT {column} FROM vehicles ORDER BY {column}"
        self.cursor.execute(query)
        return [row[0] for row in self.cursor.fetchall() if row[0] is not None]
    
    #====================== ON FIELD CHANGE========================================================
            
    def on_field_change(self, event):
        self.search_btn.config(state="active")
        selected_field=self.field_combo.get().strip().lower()
        #GET Data Base Column name
        db_field=self.field_mapping.get(selected_field)
        self.update_operator(selected_field)
        self.cleared=False
        #RESETTING
        self.value_box.set("")
        self.value_box['values']=[]
        self.value_box.unbind("<KeyRelease")
        self.value_box.config(state="normal")
        self.value_box.focus()
        #IF THE USER IS SELECTING PLATE NUMBER?
        if selected_field=="vehicle number":
            self.hide_date_controls()
            self.value_box.grid()
            self.value_box.config(state="normal")
            query = """ 
            SELECT DISTINCT plate_source || '-' || plate_code || '-' || 
            plate_number FROM vehicles """
            cursor = self.conn.cursor()
            cursor.execute(query)
            numbers = [row[0] for row in cursor.fetchall()]
            self.field_combo.config(state="normal")
            self.set_dropdown(numbers, "Select / Type Vehicle Number")
            self.value_box.set("Type Plate Source/Number:")
            self.value_box.bind("<KeyRelease>", self.filter_plate)
            
        #IF THE USER IS SELECTING BRAND?
        elif selected_field=="brand":
            self.hide_date_controls()
            brands=self.get_distinct_values(db_field)
            self.set_dropdown(brands,"Select Brands")
            
        #IF THE USER IS SELECTING MODEL?
        elif selected_field=="model":
           self.hide_date_controls()
           models=self.get_distinct_values(db_field)
           self.set_dropdown(models,"Select Models")
           
        #IF THE USER IS SELECTING TON CAPACITY
        elif selected_field=="ton Capacity":
           self.hide_date_controls()
           tons=self.get_distinct_values(db_field)
           self.set_dropdown(tons,"Select Ton Capacity")
           
        elif selected_field=="year":
            self.hide_date_controls()
            year=self.get_distinct_values(db_field)
            self.set_dropdown(year, "Select Year")
            
        elif selected_field=="mulkiya issue date":
            self.show_date_controls()
            
        elif selected_field=="mulkiya expiry date":
            self.show_date_controls()
            
        elif selected_field=="status":
            self.hide_date_controls()
            status=self.get_distinct_values(db_field)
            self.set_dropdown(status,"Select Status")
            
        elif selected_field=="odometer":
            self.hide_date_controls()
            self.value_box.grid()
            self.value_box.config(state="normal")
            self.value_box.set("Type the Odometer Value:")
            self.cleared=False
            self.value_box.bind("<KeyPress>", self.clear_on_type, add="+")
            self.value_box.bind("<KeyPress>", self.validate_odometer, add="+")
        # FOUR IN ONE: TAIL LIFT/ FUEL TYPE/ BODY TYPE/VEHICLE TYPE
        elif db_field:
            self.hide_date_controls()
            values = self.get_distinct_values(db_field)
            self.set_dropdown(values, f"SELECT {selected_field}")
        else:
            self.hide_date_controls()
            self.cleared=False
            self.value_box.grid()
            self.value_box.config(values=[]) 
            
    #=========================== SET DROP DOWN ====================================================
        
    def set_dropdown(self, values, text):
        self.value_box.grid()
        self.value_box.config(state="readonly")
        self.value_box['values']=values
        self.value_box.set(text)

    # ======================== DATE PICKER / INTELLIGENT WINDOWS ================================
    def is_date_field(self):
        return self.field_var.get().strip().lower() in (
            "mulkiya issue date", "mulkiya expiry date"
        )

    def show_date_controls(self):
        self.value_box.grid_remove()
        self.date_picker.grid(row=0, column=5, padx=2, pady=1, sticky="ew")
        self.date_filter_frame.grid()
        self.custom_range_frame.grid_remove()

    def hide_date_controls(self):
        self.date_picker.grid_remove()
        self.date_filter_frame.grid_remove()
        self.custom_range_frame.grid_remove()
        self.value_box.grid()

    def on_date_selected(self, _event=None):
        # Keep the calendar value available to the existing Add Criteria flow.
        self.value_box.set(self.date_picker.get_date().strftime("%Y-%m-%d"))

    def selected_date_column(self):
        return self.field_mapping.get(self.field_var.get().strip().lower())

    def apply_date_quick_filter(self, filter_key):
        if not self.is_date_field():
            messagebox.showinfo("FTMS PRO: Date Filter", "Select Mulkiya Issue Date or Mulkiya Expiry Date first.")
            return
        if filter_key == "custom":
            self.custom_range_frame.grid(row=0, column=6, padx=(4, 0))
            return

        today = date.today()
        if filter_key == "expired":
            start, end, label = date(1900, 1, 1), today - timedelta(days=1), "Expired"
        elif filter_key == "today":
            start = end = today
            label = "Today"
        elif filter_key == "next_7":
            start, end, label = today, today + timedelta(days=7), "Next 7 Days"
        else:
            start, end, label = today, today + timedelta(days=30), "Next 30 Days"
        self.apply_date_range(start, end, label)

    def apply_custom_date_range(self):
        if not self.is_date_field():
            return
        start, end = self.range_start_picker.get_date(), self.range_end_picker.get_date()
        if start > end:
            messagebox.showwarning("FTMS PRO: Date Range", "The start date must be on or before the end date.")
            return
        self.apply_date_range(start, end, "Custom Range")

    def apply_date_range(self, start, end, label):
        column = self.selected_date_column()
        self.active_date_filter = (column, start.isoformat(), end.isoformat(), label)
        self.load_data(date_range=self.active_date_filter)
        self.update_date_filter_summary(label)

    def update_date_filter_summary(self, label):
        matched = len(self.tree.get_children())
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM vehicles")
        total = cursor.fetchone()[0]
        percentage = (matched / total * 100) if total else 0
        self.result_labels[0].config(text=f"{percentage:.1f} %")
        self.result_labels[1].config(text=str(matched))
        self.result_labels[2].config(text=str(total))
        self.result_labels[3].config(text=f"{label}\n{self.field_var.get().strip().title()}")
        
    #==============================ACCEPTS NUMBER ONLY REJECTS EVERYTHING AND LIMITS MAX 7 DIGITS==
    def validate_odometer(self, event):
        if event.keysym in ("Backspace","Delete","Left","Right","Tab"):
            return True
        if  not event.char.isdigit():
            return "break"
        odom_value=self.value_box.get()
        if len(odom_value)>6:
            return "break"
        else:
            return False
    # ============================= ON VALUE SELECTED =============================================
        
    def on_value_selected(self, event):
        self.cleared=False
        self.search_btn.config(state="active")
        selected_field=self.field_combo.get().strip()
        selected_value=self.value_box.get()
        if selected_field=="Brand":
            self.selected_brand=selected_value
    
    
    #============================FUNCTION TO CHECK FUEL TYPE/VEHICLE TYPE/BODY TYPE/ TAIL LIFT=====
    
    def get_distinct_values(self, column_name):
        conn=sqlite3.connect("D:/FTMS PRO/ftms.db")
        cursor=conn.cursor()
        query = f"SELECT DISTINCT {column_name} FROM vehicles"
        cursor.execute(query)
        values=[str(row[0]) for row in cursor.fetchall() if row[0] is not None]
        conn.close()
        return sorted(values)
    
    #=========================== TOGGLE FILTER MODE ON/OFF=========================================
    
    def toggle_filter_mode(self):
        if self.advanced_var.get()==1:
            self.enable_advanced_filter()
            self.filter_combo.config(state="disabled")
        else:
           self.disable_advanced_filter()
           self.filter_combo.config(state="enabled")
           
    #====================================== ENABLE ADVANCED FILTER================================
    
    def enable_advanced_filter(self):
        if hasattr(self, "field_combo"):
            self.field_combo.set("Select the Field")
        if hasattr(self, "add_btn"):
            self.add_btn.config(state="normal")
        if hasattr(self, "delete_btn"):
            self.delete_btn.config(state="normal")
        if hasattr(self, "search_btn"):
            self.add_btn.config(state="normal")
            
        self.advanced_filtermode=True
        self.field_combo.set("Select the Field")
        self.criteria_frame.grid()
        self.add_btn.config(state="normal")
        self.delete_btn.config(state="normal")
        self.search_btn.config(state="normal")
        self.field_combo.config(state="enabled")
        self.op_combo.config(state="enabled")
        self.value_box.config(state="enabled")
        #WHEN CLICKING ADVANCED FILTER, SHOWING THE VISIBILITY OF HIDDEN BOX ALREADY CREATED.
        for box in self.criteria_boxes:
            box.grid()
            
    #====================================== DISABLE ADVANCED FILTER================================
    def disable_advanced_filter(self):
        if hasattr(self, "add_btn"):
            self.add_btn.config(state="disable")
        if hasattr(self, "delete_btn"):
            self.delete_btn.config(state="disable")
        if hasattr(self, "search_btn"):
            self.search_btn.config(state="disable")
        self.advanced_filtermode=False
        self.add_btn.config(state="disabled")
        self.delete_btn.config(state="disabled")
        self.search_btn.config(state="disabled")
        self.field_combo.config(state="disabled")
        self.op_combo.config(state="disabled")
        self.value_box.config(state="disabled")
        self.delete_criteria()
        for box in self.criteria_boxes:
            for widget in box.winfo_children():
                widget.destroy()
        self.criteria_set.clear()
        for box in self.criteria_boxes:
            box.grid_remove()
            
        self.criteria_frame.grid_remove()
        self.value_box.delete(0, tk.END)
    
    #========================================== SAFE SET LOGIC=====================================
    
    def safe_set_logic(self, value):
        if self.logic_var.get()!=value:
            self._internal_update=True
            self.logic_var.set(value)
            self._internal_update=False
            
    #================= ON LOGIC CHANGE ============================================================
            
    def on_logic_change(self, *args):
        if getattr(self, "_internal_update", False):
            return
        
    # ================= PRINT =====================================================================
    def print_report(self):
        messagebox.showinfo("FTMS PRO: Print", "Printing feature will be added next")

    # ================= EXPORT TO EXCEL ===========================================================
    def export_excel(self):
        self.export_vehicle_pdf()
            
    #===========================BUILD CONDITIONS===================================================
    # DIVIDE & RULE POLICY ON CRITERIA SEARCHING
    # THREE SECTIONS
    #1. COLUMN MAPPING : ALREADY DECLARED IN THE INIT MAIN FUNCTION
    #2. BUILD CONDITIONS
    #3. BUILD WHERE CLAUSE
    #----------------------------------------------------------------------------------------------
    # DIVIDE & RULE POLICY ON CRITERIA SEARCHING
    #2. BUILD CONDITIONS
    def build_condition(self, field, column, operator, value):
        # TEXT FIELDS VALUE LIKE YES/NO, DIESEL/PETROL ETC OTHER THAN NUMERIC
        try:
            float(value)
            condition = f"{column} {operator} {value}"
        except ValueError:
            condition = f"{column}{operator} '{value}'"
            
        value = value.strip()
        operator = operator.strip().upper()
        text_fields = ["brand", "model", "body_type", "fuel_type", "status", 
                        "vehicle_type", "tail_lift", "chassis_no", "engine_no","ownership_type"]
        date_fields = ["mulkiya_issue_date", "mulkiya_expiry_date"]
        
        # 1. CHECKING: = (EQUAL)
        if operator == "=":
            if field =="vehicle number" or column in text_fields:
                return f"LOWER({column}) = LOWER('{value}')"        
            else:
                return f"{column} = '{value}'"
            
        #2. NOT != (NOT EQUAL)
        elif operator == "!=":
            if column in text_fields:
                return f"LOWER({column}) != LOWER('{value}')" 
            
        #3. CHECKING: LIKE
        elif operator == "LIKE":
                return f"LOWER({column}) LIKE LOWER('%{value}%')"
            
        #4. CHECKING NUMERIC COMPARISON >, <, >=, <=
        elif operator in (">", "<", ">=", "<="):
        #DATE HANDLING    
            if column in date_fields:
                return f"DATE({column}) {operator} DATE('{value}')"
            elif field in self.numeric_fmap:
                return f"CAST({column} AS REAL) {operator} {float(value)}" # for checking 
            #numeric comparison like 10>2 nor as "10" > "2"
            else:
                return f"LOWER({column}) {operator} LOWER({value})"
        return None
    
    #=================COMBINING CONDITIONS=========================================================
    # DIVIDE & RULE POLICY ON CRITERIA SEARCHING
    #3. COMBINE CONDITIONS
    def build_where_clause(self, criteria_list):
        where_clause = ""
        if not criteria_list:
            return ""
        for i, item in enumerate(criteria_list): # LOOP TO CHECK how many criterias are in the list.
            
            field = item.get('field').lower()
            operator = item.get('operator')
            value = item.get('value')
            logic = item.get('logic','').strip().upper()
            column = self.field_mapping.get(field)
            condition = self.build_condition(field, column, operator, value)
            
            if not condition:
                continue
            if i==0:
                where_clause = condition
            else:
                    where_clause += f" {logic} {condition}"
        return where_clause # RETURN FINAL CONDITION
    
    #UPDATE COUNT HOW MANY RECORDS MET THE GIVEN CRITERIA==========================================
    def update_count(self, where_clause):
        cursor = self.conn.cursor()
        if where_clause:
            query = f"SELECT COUNT(*) FROM vehicles WHERE {where_clause}"
        else:
            query = f"SELECT COUNT(*) FROM vehicles"
        cursor.execute(query)
        row = cursor.fetchone()
        match_count = row[0] if row else 0
        #HOW MANY TOTAL RECORDS: ..................................................................
        cursor.execute("SELECT COUNT(*) FROM vehicles")
        total_count = cursor.fetchone()[0]
        if total_count > 0:
            percentage = (match_count/total_count)*100
            if percentage>=70:
                color = "green"
            elif percentage>=40:
                color ="orange"
            else:
                color = "red"
        else:
            percentage = 0
            color = "black"
        self.result_labels[0].config(fg = color)
        self.result_labels[1].config(fg = color)
        self.result_labels[2].config(fg = color)
        percentage_text = f"{percentage: .1f}" +' %'
        
        #UPDATING VARIABLES
        self.result_labels[1].config(text=str(match_count)) # MATCHING RECORDS
        self.result_labels[2].config(text=str(total_count)) # OUT OF?
        self.result_labels[0].config(text=str(percentage_text)) # how many percentage
        
    
    #===============UPDATE OPERATOR================================================================
    
    #OPERATOR FIXING: ON FIELD CHANGES
    #WHICH OPERATOR SHOULD BE ACTIVE FOR EACH FIELD
    def update_operator(self, selected_field):
        if selected_field in self.numeric_fmap:
            operators = ["<", "<=", ">",">="]
        else:
            operators = ["=","!=","LIKE"]
        self.op_combo['values']=operators
        self.op_combo.current(0)
        
    #=============SEARCH BUTTON====================================================================
    def search_button_click(self):
        self.load_data(criteria_list=self.criteria_list)
        self.search_btn.config(state="disabled")
        where_clause = self.build_where_clause(self.criteria_list)
        self.update_count(where_clause)
            
    #=============== SORT TREE VIEW================================================================
    def sort_treeview(self):
        selected_field = self.sort_var.get() #Sort By field
        order = self.sort_order.get() #Radio button Ascending / Descending
        if not selected_field:
            return
        selected_field = selected_field.strip().lower()
        col_index = self.column_map.get(selected_field)
        if col_index is None:
            return
        data = []
        for row in self.tree.get_children():
            values = self.tree.item(row)["values"]
            data.append((values, row))
            numeric_fields=["Year", "Mulkiya Issue Date", "Mulkiya Expiry Date", "Ton Capacity", "Odometer"]
        
        if selected_field in numeric_fields:
                data.sort(
                    key=lambda x:
                        self.safe_float(x[0][col_index]), reverse = (order == "DESC")
                        )
        else:
            data.sort(
                    key=lambda x: str(x[0][col_index]).lower(), reverse = (order == "DESC")
                        )
        for index, (values, row) in enumerate(data):
            self.tree.move(row, "", index)
                
    # SAFE FLOAT FUNCTION =========================================================================
    
    def safe_float(self, value):
        try:
            return float(str(value).strip())
        except:
            return 0
        
    # ================= CLOSE =====================================================================
    def close_report(self):
        sure=messagebox.askyesno("FTMS PRO:","Are you sure you want to Exit?")
        if sure:
            self.parent.grab_release()
            self.parent.destroy()
            if hasattr(self.controller, "set_form_mode"):
                self.controller.set_form_mode(False)
                self.controller.clear_content_area()
                
    def get_vehicle_pdf_config(self):
        vehicle_columns = list(self.tree["columns"])
        vehicle_field_mapping = {
            "vehicle number": "vehicle_number",
            "brand": "brand",
            "model": "model"}
        return vehicle_columns, vehicle_field_mapping
    
    def export_vehicle_pdf(self):
        vehicle_columns, vehicle_field_mapping = self.get_vehicle_pdf_config()
        vehicle_data = []
        for item in self.tree.get_children():
            vehicle_data.append(self.tree.item(item)["values"])
            
        pdf = ConvertPdf(parent = self.parent, controller=self, report_title="Vehilce Report",
            report_type = "Vehicle", columns = vehicle_columns, data = vehicle_data, table_name = "vehicles",
            field_mapping = vehicle_field_mapping)
        pdf.open_pdf_settings()
        
    def print_report(self):
        vehicle_data = []
        for item in self.tree.get_children():
            vehicle_data.append(self.tree.item(item)["values"])
            
        vehicle_columns, vehicle_field_mapping = self.get_vehicle_pdf_config()
        pdf = ConvertPdf(parent=self.parent, controller=self,report_title="Vehicle Report",
                         report_type="Vehicle", columns=vehicle_columns, data = vehicle_data, table_name="vehicles",
                         field_mapping=vehicle_field_mapping)
        pdf.open_pdf_settings()
