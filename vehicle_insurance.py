import tkinter as tk
from tkinter import ttk
import sqlite3
from globals import EMIRATE_CODES
from tkcalendar import DateEntry
from datetime import datetime, timedelta
from tkinter import messagebox
from ui_components import create_header, create_page_title

class InsurancePage:
    
    def __init__(self, parent, controller):
        self.parent=parent
        self.controller=controller
        #MAIN CONTAINER
        self.frame=tk.Frame(parent, bg="white")
        self.frame.grid(row=0, column=0, sticky="nsew")
        self.frame.grid_rowconfigure(1, weight=1)
        self.frame.grid_columnconfigure(0, weight=1)
        parent.grid_rowconfigure(0, weight=1)
        parent.grid_columnconfigure(0, weight=1)
        
        #HEADER
        create_header(self.frame)
        
        #CENTER - FRAME
        self.center_frame=tk.Frame(self.frame, bg="#1e3a5f")
        self.center_frame.grid(row=1, column=0, sticky="nsew")
        self.center_frame.grid_rowconfigure(0, weight=1)
        self.center_frame.grid_rowconfigure(1, weight=1)
        self.center_frame.grid_rowconfigure(2, weight=1)
        self.center_frame.grid_columnconfigure(0, weight=1)
        
        # PAGE TITLE (STANDARD)
        create_page_title(self.center_frame, "Insurance Details of Vehicle")
       
        self.center_frame.grid_columnconfigure(0, weight=1)
        
        #blue background with white border line outside the content
        self.form_frame=tk.Frame(self.parent, bg="#3abcd6", bd=3, relief="ridge", 
                                 highlightthickness=1, highlightbackground="white")
        self.form_frame.place(relx=0.5, rely=0.45, anchor="center", width=700, height=350)
        
        #INNER FRAME FOR SPACING
        self.inner_frame=tk.Frame(self.form_frame, bg="#d2d3d3")
        self.inner_frame.place(relx=0.5, rely=0.5, anchor="center", width=580, height=260)
        
        self.form_frame.columnconfigure(0, weight=1)
        self.form_frame.columnconfigure(1, weight=2)
      
        
        #DATABASE
        self.conn=sqlite3.connect("D:/FTMS PRO/ftms.db")
        self.cursor=self.conn.cursor()
        self.create_widgets()
        
    def create_widgets(self):
        try:
            vcmd = (self.inner_frame.register(self.validate_amount),'%P')                
        
            # Vehicle
            self.inner_frame.grid_rowconfigure(0, weight=1)
            self.inner_frame.grid_rowconfigure(1, weight=1)
            ttk.Label(self.inner_frame, text="Vehicle Number").grid(row=0, column=0, padx=10, pady=5, sticky="e")
            self.vehicle_combo = ttk.Combobox(self.inner_frame, width=15)
            self.vehicle_combo.grid(row=0, padx=10, pady=5, column=1, sticky="w")
            self.load_vehicles()
            # Insurance Company
            ttk.Label(self.inner_frame, text="Insurance Company Name & Address").grid(row=1, column=0, padx=10, pady=5, sticky="e")
            self.company_entry = tk.Entry(self.inner_frame, width=50)
            self.company_entry.grid(row=1, column=1, padx=10, pady=5, sticky="w")

            # Policy Number
            ttk.Label(self.inner_frame, text="Policy Number").grid(row=2, column=0, padx=10, pady=5, sticky="e")
            self.policy_entry = tk.Entry(self.inner_frame, width=15)
            self.policy_entry.grid(row=2, column=1, padx=10, pady=5, sticky="w")

            # Insurance Type
            tk.Label(self.inner_frame, text="Insurance Type").grid(row=3, column=0, padx=10, pady=5, sticky="e")
            self.type_combo = ttk.Combobox(self.inner_frame, values=["Comprehensive", "Third Party"], width=25, state='readonly')
            self.type_combo.grid(row=3, column=1, padx=10, pady=5, sticky="w")

            # Insurance Amount
            tk.Label(self.inner_frame, text="Insurance Amount").grid(row=4, column=0, padx=10, pady=5, sticky="e")
            self.amount_entry = tk.Entry(self.inner_frame, width=15, validate='key', validatecommand=vcmd)
            self.amount_entry.grid(row=4, column=1,padx=10, pady=5, sticky="w")

            # Issue Date
            tk.Label(self.inner_frame, text="Issue Date").grid(row=5, column=0, padx=10, pady=5, sticky="e")
            self.issue_date_entry=DateEntry(self.inner_frame, width=15, date_pattern='yyyy-mm-dd')
            self.issue_date_entry.grid(row=5, column=1, padx=10, pady=5, sticky="w")
            self.issue_date_entry.bind("<<DateEntrySelected>>", self.calculate_expiry)

            #EXPIRY DATE LABEL
            tk.Label(self.inner_frame, text="Expiry Date").grid(row=6, column=0, padx=10, pady=5,sticky="e")

            # Expiry Date
            self.expiry_date_entry = ttk.Entry(self.inner_frame, width=15, state="readonly")
            self.expiry_date_entry.grid(row=6, column=1, padx=10, pady=5, sticky="w")
            #issue date collected through DateEntry Calendar gadget stored in issue
            
            #BUTTON FRAME
            self.btn_frame=tk.Frame(self.center_frame, bg="#1e3a5f")
            self.btn_frame.grid(row=2, column=0, pady=20)
            
            self.btn_frame.grid_columnconfigure(0, weight=1)
            self.btn_frame.grid_columnconfigure(1, weight=1)     
            self.btn_frame.grid_columnconfigure(2, weight=1)                               
            
            #SAVE BUTTON
            self.save_btn=tk.Button(self.btn_frame, text="SAVE", width=20, height=2, 
                      command=self.save_vehicle).grid(row=0, column=0, padx=10) 
            
            #NEXT VEHICLE
            self.next_btn=tk.Button(self.btn_frame, text="NEXT VEHICLE", width=20, height=2,
                      command=self.next_vehicle, state="disabled").grid(row=0, column=1, padx=10)
            
            #CLOSE BUTTON
            self.close_btn=tk.Button(self.btn_frame, text="CLOSE", width=20, height=2, 
                      command=self.close_window).grid(row=0, column=2, padx=10)
            
        except Exception as e:
            messagebox("ERROR...!",e)
            
        # ENSURING INPUT ONLY DIGITS FOR INSURANCE AMOUNT
    def calculate_expiry(self, event=None):
        issue = self.issue_date_entry.get_date()
        expiry=issue+timedelta(days=364)
        self.expiry_date_entry.config(state="normal")
        self.expiry_date_entry.delete(0,tk.END)
        self.expiry_date_entry.insert(0, expiry.strftime("%Y-%m-%d"))
        self.expiry_date_entry.config(state="readonly")
        messagebox.showinfo("FTMS PRO: INFO !", f"Vehicle Insurance will Expire on {expiry.strftime('%Y-%m-%d')}")
        self.issue_date_entry.config(state='disabled')
   
    def validate_amount(self, value):
        if value=="":
            return True
        if value.isdigit() and len(value)<=5:
            return True
        else:
            return False

    def load_vehicles(self):
        self.cursor.execute("SELECT id, plate_source, plate_code, plate_number FROM vehicles")
        self.vehicles = self.cursor.fetchall()
        vehicle_list= []
        for v in self.vehicles:
            emirate=EMIRATE_CODES.get(v[1], v[1])
            plate=(f"{emirate} {v[2]} {v[3]}") 
            vehicle_list.append(plate)
            self.vehicle_combo['values'] = vehicle_list

    def save_vehicle(self):
        try:
            vehicle_no_value=self.vehicle_combo.get()
            insurance_company_value=self.company_entry.get()
            policy_number_value=self.policy_entry.get()
            insurance_type_value=self.type_combo.get()
            insurance_amount_value=self.amount_entry.get()
            issue_date_value=self.issue_date_entry.get()
            expiry_date_value=self.expiry_date_entry.get() 
            
            # BLOCKING EMPTY FIELDS SAVE
            
            if (vehicle_no_value=="" or insurance_amount_value=="" 
            or 
                policy_number_value=="" or insurance_type_value=="" 
            or  insurance_amount_value=="" or issue_date_value=="" 
            or expiry_date_value==""):
                messagebox.showwarning("FTMS PRO: Missing Data", "Please fill all required fields before saving.") 
                return
            
            self.cursor.execute("""
            INSERT INTO vehicle_insurance (vehicle_id, insurance_company, policy_number, insurance_type, 
            insurance_amount, issue_date, expiry_date) 
            VALUES (?,?,?,?,?,?,?)
            """, ( vehicle_no_value, insurance_company_value,
            policy_number_value, insurance_type_value, insurance_amount_value,
            issue_date_value,expiry_date_value ))
            self.conn.commit()
            messagebox.showinfo("FTMS PRO: ", "Success..! All Data are valid & Saved Succesfully")
            self.save_btn.config(state="disabled")
            self.next_btn.config(state="normal")
                
        except sqlite3.IntegrityError:
            messagebox.showerror("FTMS PRO: Duplicate Vehicle", "This vehicle plate already exists. Check your Data")
        except Exception as e:
            messagebox.showerror("FTMS PRO: Data Error:", str(e))
            
    def next_vehicle(self):
            self.vehicle_combo.set("")
            self.company_entry.delete(0, tk.END)
            self.policy_entry.delete(0, tk.END)
            self.type_combo.set("")
            self.amount_entry.delete(0, tk.END)
            self.issue_date_entry.set("")
            self.expiry_date_entry.set("")
            self.save_btn.config(state="normal")
            
    def close_window(self):
        confirm=messagebox.askyesno("FTMS PRO: Confirm Exit", "Are you sure you want to Close?")
        if confirm:
            self.parent.grab_release()
            self.controller.overlay.destroy()
            self.controller.set_form_mode(False)
            #close overlay
            #tk.Label(self.controller.content_area, text="Dashboard", font=("Segoe UI", 20)).pack(pady=50)
            self.controller.show_main_menu()
            
                
       
       
            
        
        
        

