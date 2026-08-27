import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import pandas as pd
from ui_components import create_header, create_page_title
from datetime import datetime
from tkinter import END#LEFT SIDE HEADER
from datetime import datetime

class EditCommercial:
    def __init__(self, parent, controller):
        self.parent = parent
        self.controller = controller
        self.fields = {}
        self.source_var = tk.StringVar()
        self.code_var = tk.StringVar()
        self.number_var = tk.StringVar()
        self.vehicle_type_var=tk.StringVar()
        self.body_type_var = tk.StringVar()
        self.fuel_type_var = tk.StringVar()
        self.tail_lift_var = tk.StringVar()
        self.odometer_var = tk.StringVar()
        self.frame=tk.Frame(parent, bg="#d8caa3")
        self.frame.place(x=40, y=80, relwidth=0.95, relheight=0.90)
        header_frame = tk.Frame(self.frame, bg="#d8caa3")
        header_frame.pack(fill="x")
        header_left = tk.Frame(header_frame, bg="#d8caa3")
        header_left.pack(side="left", padx=10)
        header_right = tk.Frame(header_frame, bg="#d8caa3")
        header_right.pack(side="right", padx=15)
        search_frame=tk.Frame(self.frame, bg="#d8caa3")
        tk.Label(search_frame, text="Search Vehicle:",
                font=("Arial", 11)).pack(side="left", padx=10)
        search_frame.pack(fill="x", pady=18)
        self.search_var = tk.StringVar()
        self.frame.grab_set()
        search_box = ttk.Combobox(
            search_frame, 
            textvariable=self.search_var,
            width=25
        )
        search_box.pack(side="left", padx=5)
        search_box.bind("<KeyRelease>", self.search_vehicle)
        # =========================
        # MAIN FRAME (LEFT + RIGHT)
        # =========================
        self.main_frame = tk.Frame(self.frame, bg="#d8caa3")
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=1)
        # =========================
        # LEFT PANEL (Vehicle List)
        # =========================
        self.last_updated_label =tk.Label(self.main_frame, text="Last Updated : Not Available",
                                          font=("Arial", 9), bg="#d8caa3", fg="blue", 
                                          anchor="w", justify="left")
        self.last_updated_label.place(x=62, y=170)
        left_frame = tk.Frame(self.main_frame, bg="#d8caa3", width=420)
        left_frame.pack(side="left", fill="y")
        left_frame.config(width=300)
        left_frame.pack_propagate(False)
        tk.Label(left_frame, text="Fleet Vehicle List",
                font=("Arial", 12, "bold")).pack(pady=2)
        tree_frame = tk.Frame(left_frame, bg="#d8caa3")
        tree_frame.pack(fill="both", expand=True, pady=(0,20))
         # Scrollbar
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Small.TCombobox", padding = 1,
                        gripcount=0, background="gray",
                        darkcolor="gray",
                        lightcolor="lightgray",
                        troughcolor="#f0f0f0",
                        bordercolor="#c0c0c0",
                        arrowcolor="black", width=18)
        scroll = ttk.Scrollbar(tree_frame, orient="vertical", 
                               style="Vertical.TScrollbar")
        scroll.pack(side="right", fill="y", pady=0)
        
        self.tree = ttk.Treeview(tree_frame,
                                columns=("id","source", "code", "number"),
                                show="headings",
                                height=8, yscrollcommand=scroll.set)
        #CONFIGURE HEADINGS
        self.tree.heading("id", text="ID")
        self.tree.heading("source", text="Plate Source")
        self.tree.heading("code", text="Plate Code")
        self.tree.heading("number", text="Plate Number")
        
        #COLUMNS
        self.tree.column("id", width=0, stretch=False)
        self.tree.column("source", width=120, anchor="center")
        self.tree.column("code", width=80, anchor="center")
        self.tree.column("number", width=120, anchor="center")
        self.tree.pack(fill="both", expand=True)
        #pady=(0,10)
        scroll.config(command=self.tree.yview)
        self.tree.bind("<<TreeviewSelect>>", self.on_vehicle_select) 
        self.load_vehicle_list()
        # =========================
        # RIGHT PANEL (FORM)1
        # =========================
        #right_frame = tk.Frame(main_frame, bg="#d8caa3", width=700)
        #right_frame.pack(side="left", fill="both", expand=False, padx=10)
        #right_frame.pack_propagate(False)
        
        header_frame=tk.Frame(self.main_frame, bg="#d8caa3")
        header_frame.pack(fill="x", pady=5)
        top_header_frame = tk.Frame(self.main_frame, bg="#d8caa3", bd=2, relief="solid")
        top_header_frame.pack(fill="x", padx=40, pady=0, ipady=0)
        title_label=tk.Label(top_header_frame, text="EDIT VEHICLE DETAILS",
                font=("Arial", 16, "bold"))
        seperator = tk.Frame(top_header_frame, bg="#666666", width=2, height=60) 
        # Status label
        self.status_label = tk.Label(top_header_frame, text="STATUS",
                                     bg="green", fg="white", font=("Arial", 9, "bold"),
                                     width=110, height=1, justify="center"
                                    )
        title_label.pack(side="left", padx=60)
        seperator.pack(side="left", padx=40, fill="y")
        self.status_label.pack(side="left", padx=15, fill="y") 
        info_frame= tk.Frame(self.main_frame, bg="#d8caa3")
        info_frame.pack(pady=5)
        self.entry_plate_source = tk.Entry(info_frame, width=15, justify="center")
        self.entry_plate_code = tk.Entry(info_frame, width=15, justify="center")
        self.entry_plate_number = tk.Entry(info_frame, width=15, justify="center")
        
        tk.Label(info_frame, text="Plate Source",bg="#d8caa3",font=("Arial",10, 
                                                                    "bold")).grid(row=0, 
                                                                                  column=0, 
                                                                                  padx=10)
        
        tk.Label(info_frame, text="Plate Code", bg="#d8caa3", font=("Arial",10, 
                                                                 "bold")).grid(row=0, column=1, 
                                                                               padx=10)
        
        tk.Label(info_frame, text="Plate Number", bg="#d8caa3",font=("Arial",10, 
                                                                  "bold")).grid(row=0, 
                                                                                column=2, 
                                                                                padx=10)
        self.entry_plate_source.grid(row=1, column=0, padx=10)
        self.entry_plate_code.grid(row=1, column=1, padx=10)
        self.entry_plate_number.grid(row=1, column=2, padx=10)    
        
         # ===== EDITABLE FRAME =====
        self.edit_frame = tk.LabelFrame(self.main_frame, bg="#e7e7e7", text="Editable Fields", 
                                   font=("Arial",10, "bold"),
                                   width=450,height=260,padx=20, pady=15)
        self.edit_frame.pack(pady=15) # TO GIVE MORE WIDTH TO BOX
        self.edit_frame.pack_propagate(False)
        
         #  EDIT BUTTONS
        # =========================
        self.btn_frame = tk.Frame(self.main_frame,bg="#d8caa3")
        self.btn_frame.pack(pady=5)
        
        self.edit_btn=tk.Button(self.btn_frame, text="EDIT", width=20, height=2,
                command=self.enable_edit)
        self.edit_btn.pack(side="left", padx=5)

        self.update_btn=tk.Button(self.btn_frame, text="UPDATE", width=20, height=2,
                command=self.update_vehicle)
        self.update_btn.pack(side="left", padx=5)
        self.update_btn.config(state="disabled")

        self.close_btn=tk.Button(self.btn_frame, text="CLOSE", width=20, height=2,
                command=self.close_edit_page)
        self.close_btn.pack(side="left", padx=3)
        
        status_frame=tk.Frame(header_frame, bg="#d8caa3")
        status_frame.pack(side="right",padx=20)
        
        
        # IPAD = INTERNAL PAD EXPANSION

        # ----- Vehicle Type -----
        tk.Label(self.edit_frame, text="Vehicle Type", bg="white").grid(row=0, column=0, sticky="w", padx=(30,20))
        self.entry_vehicle_type = ttk.Combobox(self.edit_frame, textvariable=self.vehicle_type_var, values=["Chiller", "Non-Chiller", "Freezer"], state="readonly", width=15)
        self.entry_vehicle_type.grid(row=0, column=1, padx=15,pady=10, sticky="ew", ipadx=35)

        # ----- Body Type -----
        tk.Label(self.edit_frame, text="Body Type", bg="#e7e7e7").grid(row=1, column=0, sticky="w", padx=(30,20))

        self.entry_body_type = ttk.Combobox(self.edit_frame, textvariable=self.body_type_var, values=["Closed", "Open", "Flat Bed"], state="readonly", width=15)
        self.entry_body_type.grid(row=1, column=1, padx=15, pady=10, sticky="ew",ipadx=35)

        # ----- Fuel Type -----
        tk.Label(self.edit_frame, text="Fuel Type", bg="white").grid(row=2, column=0, sticky="w", padx=(30,20))

        self.entry_fuel_type = ttk.Combobox(self.edit_frame, textvariable=self.fuel_type_var, values=["Petrol", "Diesel", "Electric","Hybrid", "CNG","Other"], 
                                            state="readonly", width=15)
        self.entry_fuel_type.grid(row=2, column=1, padx=15, pady=10, sticky="ew",ipadx=35)
        
        # ----- Tail Lift -----
        tk.Label(self.edit_frame, text="Tail Lift", bg="white").grid(row=3, column=0, sticky="w", padx=(30,20))

        self.entry_tail_lift = ttk.Combobox(self.edit_frame,textvariable=self.tail_lift_var, values=["Yes", "No"], state="readonly", 
                                            width=15)
        self.entry_tail_lift.grid(row=3, column=1, padx=15, pady=10,sticky="ew", ipadx=35)

        # ----- Odometer -----
        tk.Label(self.edit_frame, text="Odometer").grid(row=4, column=0, sticky="w", padx=(30,20))

        self.entry_odometer = tk.Entry(self.edit_frame, textvariable=self.odometer_var, width=15, state="readonly")
        self.entry_odometer.grid(row=4, column=1, padx=15, pady=10, ipadx=35, sticky="ew")
        
        #FIELD MAPPING
        self.fields = {"vehicle_type": self.entry_vehicle_type,
                          "body_type": self.entry_body_type,
                          "fuel_type": self.entry_fuel_type,
                          "tail_lift": self.entry_tail_lift,
                   "current_odometer": self.entry_odometer,
                       "plate_source": self.entry_plate_source,
                         "plate_code": self.entry_plate_code,
                       "plate_number": self.entry_plate_number
                       }
        
        
        bottom_section = tk.Frame(self.main_frame,bg="#d8caa3")
        bottom_section.pack(fill="x", pady=10)
        
        self.form_frame = tk.Frame(self.main_frame, bg="#d8caa3")
        self.form_frame.pack(fill="both", expand=True, padx=20, pady=5)
        self.form_frame.config(bg="#e7e7e7")
        self.inline_msg = tk.Label(self.form_frame,text="", fg="green", font=("Arial",8))
        self.inline_msg.grid(row=10, column=0, columnspan=20, pady=2, sticky="ew")
        self.form_frame.grid_columnconfigure(0,weight=1)
        # =========================
        # LOAD DATA
        # =========================
        self.tree.bind("<ButtonRelease-1>", self.on_vehicle_select)
        
    def close_edit_page(self):
        confirm=messagebox.askyesno("FTMS PRO: Confirm Exit", "Are you sure you want to Close?")
        if confirm:
            self.frame.grab_release()
            self.frame.destroy()
    
    def load_vehicle_list(self, event=None):
        #DATABASE CONNECTING
        conn = sqlite3.connect("D:/FTMS PRO/ftms.db")
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM vehicles")
        rows = cursor.fetchall()
        for item in self.tree.get_children():
            self.tree.delete(item)
        for row in rows:
            vehicle_id=row["id"]
            plate_source = row["plate_source"]
            plate_code = row["plate_code"]
            plate_number = row["plate_number"]
            self.tree.insert("", "end", values=(
                vehicle_id,
                plate_source,
                plate_code,
                plate_number
            ))
        conn.close()
#--------------------------------------------------------
    def load_vehicle_details(self, vehicle_id):
        import sqlite3

        conn = sqlite3.connect("D:/FTMS PRO/ftms.db")
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM vehicles WHERE id=?", (vehicle_id,))
        data = cursor.fetchone()
        if data is None:
            messagebox.showerror("FTMS PRO:", "Vehicle details not found")
            conn.close()
            return

        self.current_vehicle_id = vehicle_id
        self.entry_plate_source.config(state="normal")
        self.entry_plate_code.config(state="normal")
        self.entry_plate_number.config(state="normal")

        self.entry_plate_source.delete(0, "end")
        self.entry_plate_source.insert(0, data["plate_source"])

        self.entry_plate_code.delete(0, "end")
        self.entry_plate_code.insert(0, data["plate_code"])

        self.entry_plate_number.delete(0, "end")
        self.entry_plate_number.insert(0, data["plate_number"])

        self.status_label.config(text=f"Status: {data['status']}")
        
    def search_vehicle(self, event=None):
        keyword = self.search_var.get().lower()
        # Clear existing rows
        for item in self.tree.get_children():
            self.tree.delete(item)
        conn = sqlite3.connect("D:/FTMS PRO/ftms.db")
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM vehicles
            WHERE
                LOWER(plate_source) LIKE ?
                OR LOWER(plate_code) LIKE ?
                OR LOWER(plate_number) LIKE ?
        """, (
            f"%{keyword}%",
            f"%{keyword}%",
            f"%{keyword}%"
        ))

        rows = cursor.fetchall()

        for row in rows:
            self.tree.insert("", "end", values=(
                row["id"],
                row["plate_source"],
                row["plate_code"],
                row["plate_number"]
            ))

        conn.close()
        
    def on_vehicle_select(self, event):
        selected = self.tree.selection()
        if not selected:
            return
        item_id = selected[0]
        if not self.tree.exists(item_id):
            return
        item = self.tree.item(item_id)
        values = item["values"]
        if len(values)>3:
            plate_number = values[3]
        else:
            plate_number=""
        vehicle_id = values[0]
        plate_source = values[1]
        plate_code = values[2]

        self.load_vehicle_details(vehicle_id)

        # SHOW TOP VALUES
        self.source_var.set(plate_source)
        self.code_var.set(plate_code)
        self.number_var.set(plate_number)
        # DATABASE FETCH
        conn = sqlite3.connect("D:/FTMS PRO/ftms.db")
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM vehicles
            WHERE plate_source=?
            AND plate_code=?
            AND plate_number=?
        """, (
            plate_source,
            plate_code,
            plate_number
        ))
        row = cursor.fetchone()
     
        if row:
            status = row["status"]
            self.vehicle_type_var.set(row["vehicle_type"])
            self.body_type_var.set(row["body_type"])
            self.fuel_type_var.set(row["fuel_type"])
            self.tail_lift_var.set(row["tail_lift"])
            self.odometer_var.set(row["current_odometer"])
            
            updated_at = row["updated_at"]
            if updated_at:
                self.last_updated_label.config(text=f"Last Updated :{updated_at}")
            else:
                self.last_updated_label.config(text="Last Updated : Not Available")
        # CHECKING THE STATUS OF THE VEHICLE
            if status.upper() in ["ACTIVE","UNDER REPAIR"]:
                self.status_label.config(bg="green", text=f"STATUS : {status}\n\nYOU CAN EDIT THIS RECORD")
                self.edit_btn.config(state="normal")
                self.inline_msg.config(text="STATUS: ACTIVE  You can click EDIT to modify", fg="green")
            
            else:
                self.status_label.config(bg="red", text=f"STATUS : {status}\n\nSORRY YOU CAN'T EDIT\nTHIS RECORD OF VEHICLE")
                self.edit_btn.config(stat="disabled")
                self.inline_msg.config(fg="red", text=f"STATUS: {status} EDITING NOT ALLOWED")
        conn.close()
        
    def enable_edit(self):
        for field in self.fields.values():
            try:
                field.state(["!disabled"])
                field.state(["!readonly"])
            except:
                field.config(state="normal")
                self.entry_odometer.config(state="normal")
        self.edit_frame.config(bg="#d8ffd8", text="EDIT MODE ACTIVATED", labelanchor="n")
        self.update_btn.config(state="normal")
        
    def update_vehicle(self):
        update_fields=[]
        update_values=[]
        changed_fields=[]
        vehicle_type= self.fields["vehicle_type"].get()
        body_type = self.fields["body_type"].get()
        fuel_type = self.fields["fuel_type"].get()
        tail_lift = self.fields["tail_lift"].get()
        if (vehicle_type=="Chiller" or vehicle_type=="Freezer") and (body_type=="Open" or body_type=="Flat Bed"):
            messagebox.showerror("FTMS PRO:", "Invalid Section\n Chiller/Freezer Vehicle cannot have Open/Flatbed body type")
            return
        elif fuel_type =="Electric" and tail_lift=="Yes":
            messagebox.showerror("FTMS PRO:", "Invalid Section\n Electric Vehicle cannot have Hydraulic Tail Lift")
            return
            
        if not hasattr(self, "current_vehicle_id"):
            return
        conn = sqlite3.connect("D:/FTMS PRO/ftms.db")
        cursor = conn.cursor()
        
        #GETTING THE CURRENT RECORD OLD VALUES BEFORE UPDATION
        selected_item = self.tree.focus()
        selected_id = self.tree.item(selected_item)["values"][0]
        cursor.execute(""" SELECT body_type,vehicle_type, fuel_type, tail_lift, 
                       current_odometer FROM vehicles WHERE id=?""",(selected_id,))
        row = cursor.fetchone()
        old_data = {
               "body_type":row[0],
            "vehicle_type":row[1],
               "fuel_type":row[2],
               "tail_lift":row[3],
        "current_odometer":row[4]
        }
        
        new_data = {
               "body_type":self.body_type_var.get(),
            "vehicle_type":self.vehicle_type_var.get(),
               "fuel_type":self.fuel_type_var.get(),
               "tail_lift":self.tail_lift_var.get(),
        "current_odometer":self.odometer_var.get()
        }
        
        
        for field in old_data:
            if str(old_data[field])!=str(new_data[field]):
                changed_fields.append({"field":field,
                                       "old":old_data[field],
                                       "new":new_data[field]})
                
                update_fields.append(f"{field}=?")
                update_values.append(new_data[field])
                
        today = datetime.now().strftime("%d-%b-%Y")
        update_fields.append("updated_at=?")
        update_values.append(today)
        cursor.execute(""" SELECT updated_at FROM vehicles WHERE id=?""",(selected_id,))
        vehicle_updated_at=cursor.fetchone()[0]
        for change in changed_fields:
            #CLOSE OLD ACTIVE HISTORY RECORD
            cursor.execute(""" UPDATE vehicle_history 
                           SET effective_to=?
                           WHERE vehicle_id=?
                           AND field_name=?
                           AND effective_to IS NULL """,(today, selected_id, change["field"]))
            
            #INSERT NEW HISTORY RECORD
            cursor.execute(""" INSERT INTO vehicle_history(
                vehicle_id, field_name, old_value, new_value, effective_from,
                effective_to, changed_by)
                VALUES (?,?,?,?,?,?,?)""",(selected_id, change["field"],
                                           str(change["old"]),
                                           str(change["new"]), vehicle_updated_at, today, "Admin"))
        
        sql = f""" UPDATE vehicles SET {','.join(update_fields)} WHERE id=?"""
        update_values.append(selected_id)    
        cursor.execute(sql, update_values)
        conn.commit()
        messagebox.showinfo("Success", "Vehicle updated")
        self.edit_btn.config(state="disabled")
        self.update_btn.config(state="disabled")
        self.inline_msg.config(text=f"Vehicle updated on {vehicle_updated_at} by Admin", fg="green")
        
        if not changed_fields:
             #USER CHANGED THE DATA OR NOT?
                messagebox.showinfo("FTMS PRO:","No Changes!\nNo Fields were modified")
                return
    