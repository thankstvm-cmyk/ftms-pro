import tkinter as tk
from tkinter import ttk
from FTMS_Add_Vehicle_UI import AddVehicleWindow
from PIL import Image, ImageTk
from vehicle_insurance import InsurancePage
from vehicle_report import VehicleReportPage
from tkinter import messagebox
from newlogin import LoginDialog
from edit_vehicles import EditPage
import sqlite3
from edit_commercial import EditCommercial
from font_manager import FontManager
from config import IMAGE_DIR
from dashboard import Dashboard
from angel.ftmsangel import Angel
from employees_form import EmployeeForm

class FTMSApp:
    def __init__(self, root):
        self.root=root
        # Safe navigation bridge for Smart Angel.  Angel only invokes existing
        # FTMSApp methods registered in its action router.
        self.root.ftms_app = self
        self.root.title("FTMS Pro - Fleet Transportation Management System")
        self.root.state('zoomed')
        self.root.resizable(True, True)
        self.root.protocol("WM_DELETE_WINDOW", self.disable_close)
        #self.top=tk.Toplevel(self.parent)
          # Sidebar Frame
        
        self.sidebar = tk.Frame(self.root, bg="#1f2937", width=250)
        self.sidebar.pack(side="left", fill="y")
        
        #MAIN CONTENT FRAME
        self.main_content=tk.Frame(self.root,bg="#1f2c3c", width=200 )
        self.main_content.pack(side="left", fill="both", expand=True)
        
        #TITLE
        self.module_title=tk.Label(self.main_content, text="FTMS PRO | Dashboard", 
                                   font=("Segoe UI", 16, "bold"), fg="white", bg="#1f2937")
        self.module_title.pack(fill="x", padx=20, pady=10)
        
        #SUBMENU FRAME
        self.submenu_frame=tk.Frame(self.main_content, bg="#edd177", height=40)
        self.submenu_frame.pack(fill="x")
        self.content_area=tk.Frame(self.main_content, bg="white")
        self.content_area.pack(fill="both", expand=True)
        
        #MAIN PROGRAM
        # FTMS LOGO
        logo_img=Image.open(IMAGE_DIR / "FTMS LOGO.JPG")
        logo_img=logo_img.resize((120,120))
        self.logo=ImageTk.PhotoImage(logo_img)
        logo_label=tk.Label(self.sidebar, image=self.logo, bg="#1f2937")
        logo_label.pack(pady=10)
     
        
        
        menu_items = [
            ("Dashboard", self.show_dashboard),
            ("Vehicle Details Updation Menu", self.show_vehicle),
            ("Staff Management Menu", self.show_staff),
            ("Vehicle Management Menu", self.show_fuel),
            ("Odomenter Entry Menu", self.show_odometer),
            ("View Report Menu", self.show_reports),
            ("Exit", self.root.quit)
            ]

        for text, command in menu_items:
            btn = tk.Button(self.sidebar, text=text, command=command,
            fg="white", bg="#374151", activebackground="#4b5563", 
            relief="flat", padx=10, pady=10)
            btn.pack(fill="x", padx=10, pady=5)
        
        tk.Frame(self.main_content, height=1,bg="#1f2937").pack(fill="x")
        
        #Admin Side Button 
        img=Image.open(IMAGE_DIR / "lock.jpeg")
        img=img.resize((20,20))
        lock=ImageTk.PhotoImage(img)
        btn_admin = tk.Button(self.sidebar, text="Admin Settings",image=lock, compound="left",
                               bg="#1c0bdf", fg="white",
                              font=("Arial", 11, "bold"), relief="flat", command=self.show_admin_menu)
        btn_admin.image=lock
        btn_admin.pack(fill="x", padx=10, pady=(20,5))
        seperator=tk.Frame(self.sidebar, height=2, bg="#5a6f86")
        seperator.pack(fill="x", padx=10, pady=10)
        
        ##########################################################################################################
        #SHOW WELCOME SCREEN
        ##########################################################################################################
        self.show_main_menu()
        
    def show_dashboard(self):
        self.clear_submenu()
        self.load_page("Dashboard")
        self.submenu_frame.pack_forget()
        self.clear_content_area()
        Dashboard(self.content_area)
        #FTMS BACKGROUND
        """
       
        """
        
    def show_main_menu(self):
        self.clear_content_area()
        self.main_content.pack(fill="both", expand=True)
        bg_img=Image.open(IMAGE_DIR / "background.jpg")
        bg_img=bg_img.resize((900, 500))
        self.bg=ImageTk.PhotoImage(bg_img)
        
        bg_label=tk.Label(self.content_area,image=self.bg, bg="blue", bd=2, highlightbackground="#5a7fa6")
        bg_label.place(relx=0.5, rely=0.50, anchor="center")
        
        welcome_frame=tk.Frame(self.content_area, bg="white")
        welcome_frame.place(relx=0.5, rely=0.10, anchor="center")
        
        welcome_label=tk.Label(welcome_frame, text="WELCOME TO FTMS PRO", 
                               font=("Segoe UI", 26, "bold"), fg="#1f2937", bg="#f8fafc")
        welcome_label.pack()
        welcome_label.lift()
        sub_label=tk.Label(welcome_frame, text="FLEET TRANSPORTATION MANAGEMENT SYSTEM", 
                           font=("Segoe UI",14),fg="gray40", bg="white")
        sub_label.pack(pady=(0,0))
        sub_label.lift()
        
        divider=tk.Frame(welcome_frame, bg="#073014", height=3, width=430)
        divider.pack(pady=1)
        divider.lift()
        
        
    def load_page(self, title):
        if title=="Dashboard":
            self.submenu_frame.pack_forget()
        else:
            self.submenu_frame.pack(fill="x", before=self.content_area)
            self.clear_content_area()
        self.module_title.config(text=f"FTMS PRO |{title}")    
        
       
    def show_vehicle(self):
        self.load_page("Vehicle Updation")
        self.show_vehicle_menu()

    def show_staff(self):
        self.load_page("Staff Management")
        self.show_staff_menu()

    def show_odometer(self):
        self.load_page("Odometer Section")

    def show_fuel(self):
        self.load_page("Vehicle Management")
        
        
    def show_admin_menu(self):
        self.load_page("Admin Settings - Page")
        self.clear_submenu()
        btn_user=tk.Button(self.submenu_frame, text="User Management", width=18)
        btn_user.pack(side="left", padx=5, pady=5)
        btn_roles=tk.Button(self.submenu_frame, text="Roles", width=15)
        btn_roles.pack(side="left", padx=5, pady=5)
        btn_settings=tk.Button(self.submenu_frame, text="System Settings", width=18)
        btn_settings.pack(side="left", padx=5, pady=5)
        
    def show_staff_menu(self):
        self.clear_submenu()
        btn_new_emp=tk.Button(self.submenu_frame, text="New Employee", command=self.new_employee, width=20)
        btn_new_emp.pack(side="left", padx=5, pady=5)
        
        btn_edit_emp=tk.Button(self.submenu_frame, text="Edit Employee Details", width=20)
        btn_edit_emp.pack(side="left", padx=5, pady=5)
        
        btn_veh_undertake=tk.Button(self.submenu_frame, text="Vehicle Undertake", width=20)
        btn_veh_undertake.pack(side="left", padx=5, pady=5)
        
        btn_assign_route=tk.Button(self.submenu_frame, text="Assign Route/Vehicle", width=20)
        btn_assign_route.pack(side="left", padx=5, pady=5)
        
        
        
        btn_resign=tk.Button(self.submenu_frame, text="Resignation", width=20)
        btn_resign.pack(side="left", padx=5, pady=5)
        

    def show_vehicle_menu(self):
        self.clear_submenu()
        btn_pick=tk.Button(self.submenu_frame, text="Pickup / Truck / Trailer", command=self.open_add_vehicle, width=20)
        btn_pick.pack(side="left",padx=5, pady=5)
        
        bik_bus=tk.Button(self.submenu_frame, text="Bike/ Bus", width=20)
        bik_bus.pack(side="left",padx=5, pady=5)
        
        off_veh=tk.Button(self.submenu_frame, text="Office Vehicles", width=20)
        off_veh.pack(side="left",padx=5, pady=5)
        
        edt_veh=tk.Button(self.submenu_frame, text="Edit Vehciles", command=self.open_logintoedit, width=20)
        edt_veh.pack(side="left",padx=5, pady=5)
        
        ins_det=tk.Button(self.submenu_frame,text="Insurance Details", command=self.open_vehicleins_page, width=20)
        ins_det.pack(side="left",padx=5, pady=5)
        
    def open_add_vehicle(self):
        self.show_overlay()
        self.set_form_mode(True)
        self.set_page_title("Add New Vehicle")
        self.add_vehicle=AddVehicleWindow(self.overlay, self)
        
    def open_logintoedit(self):
        self.show_overlay()
        self.set_form_mode(True)
        login = LoginDialog(self.root, self.open_edit_page)
        login.show_login()
        
    def open_edit_page(self):
        self.overlay=tk.Frame(self.root, bg="white")
        self.overlay.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.overlay.lift()
        self.overlay.grab_set()
        for widget in self.overlay.winfo_children():
            widget.destroy()
        self.set_form_mode(True)
        self.set_page_title("Edit Vehicle Details")
        page = EditPage(self.overlay, self)
        page.open_vehicle_list() 
        
        
    def open_vehicleins_page(self):
        self.overlay=tk.Frame(self.root, bg="white")
        self.overlay.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.overlay.lift()
        self.overlay.grab_set()
        self.set_form_mode(True)
        self.set_page_title("Insurance Details of Vehicle")
        self.ins_page=InsurancePage(self.overlay, self)    
    
        
    # REPORT SECTION

    def show_reports(self):
        self.load_page("Report Section")
        self.show_report_menu()
        
    def show_report_menu(self):
        self.clear_submenu()
        btn_vehicle = tk.Button(
            self.submenu_frame,
            text="Vehicle Reports",
        command=self.show_vehicle_reports,
        width=25
        )
        btn_vehicle.pack(side="left", padx=10, pady=5)

        btn_staff = tk.Button(
            self.submenu_frame,
            text="Staff Reports", command=self.show_staff_reports,
            width=25
        )
        btn_staff.pack(side="left", padx=10, pady=5)
        
    def show_vehicle_reports(self):
        self.clear_content_area()
        self.set_module_title("Vehicles' Report Section - Sub Menu")
        self.clear_submenu()
        veh_rep=tk.Button(self.submenu_frame, text="Vehicles Report", width=15, command=self.open_vehicle_report)
        veh_rep.pack(side="left",padx=5, pady=5)
        
        acc_rep=tk.Button(self.submenu_frame, text="Accident Report", width=15)
        acc_rep.pack(side="left",padx=5, pady=5)
        
        fue_rep=tk.Button(self.submenu_frame, text="Fuel usage Report", width=15)
        fue_rep.pack(side="left",padx=5, pady=5)
        
        brk_rep=tk.Button(self.submenu_frame, text="Breakdown Report", width=15)
        brk_rep.pack(side="left",padx=5, pady=5)
        
        mai_rep=tk.Button(self.submenu_frame, text="Maintenance Report", width=15)
        mai_rep.pack(side="left",padx=5, pady=5)
        
        doc_rep=tk.Button(self.submenu_frame, text="Documents Ren. Report", width=18)
        doc_rep.pack(side="left",padx=5, pady=5)
        
        exp_exp=tk.Button(self.submenu_frame, text="Total Exp. Report", width=17)
        exp_exp.pack(side="left",padx=5, pady=5)

        
       
    def show_staff_reports(self):
        self.clear_content_area()
        self.set_module_title("Staff Report Section - Sub Menu")
        self.clear_submenu()
        emp_rep=tk.Button(self.submenu_frame, text="Total Employees Report", width=19)
        emp_rep.pack(side="left",padx=5, pady=5)
        
        vac_rep=tk.Button(self.submenu_frame, text="Annual Vacation Report", width=19)
        vac_rep.pack(side="left",padx=5, pady=5)
        
        app_rep=tk.Button(self.submenu_frame, text="Vacation for Approval Report", width=19)
        app_rep.pack(side="left",padx=5, pady=5)
        
        att_rep=tk.Button(self.submenu_frame, text="Attendance Report", width=17)
        att_rep.pack(side="left",padx=5, pady=5)
        
        lea_rep=tk.Button(self.submenu_frame, text="Leave Report", width=17)
        lea_rep.pack(side="left",padx=5, pady=5)

    def new_employee(self):
        self.show_overlay()
        self.set_form_mode(True)
        self.set_page_title("Add New Employee")
        self.new_employee=EmployeeForm(self.overlay, self)
        
        
        
    #SUB MENU: SHOW VEHICLE MENU - PICK UP/ TRUCK/TRAILER
    def open_vehicle_report(self):
        self.show_overlay()
        self.set_form_mode(True)
        self.set_page_title("Total Vehicle Report")
        self.vehicle_report=VehicleReportPage(self.overlay, self)
    
        
    # TOTAL PROGRAM CONTROLLING SECTION
    def clear_submenu(self):
        for widget in self.submenu_frame.winfo_children():
            widget.destroy()
    
    
    def open_fullscreen_page(self, page_Cass):
        self.show_overlay() 
        self.current_page=page_Cass(self.overlay, self)
    
    
    def clear_content_area(self):
        if hasattr(self, "content_area"):
            for widget in self.content_area.winfo_children():
                widget.destroy()
        
    def set_module_title(self, module_name):
        self.module_title.config(text=f"FTMS PRO | {module_name}")
        self.current_module = module_name
        if hasattr(self, "angel_chat"):
            self.angel_chat.update_module(module_name)
    
        
    def set_page_title(self, text):
        self.module_title.config(text=f"FTMS PRO |(text)", font=("Segoe UI", 18, "bold"), fg="white")
        
    def disable_menu(self):
        for widget in self.sidebar.winfo_children():
            if isinstance(widget, tk.Button):
                widget.config(state="disabled")
            
    def enable_menu(self):
        for widget in self.sidebar.winfo_children():
            if isinstance(widget, tk.Button):
                widget.config(state="normal")
            
    def show_overlay(self):
        self.overlay=tk.Frame(self.root, bg="white")
        self.overlay.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.overlay.lift()
        self.overlay.grab_set()
        
    def hide_overlay(self):
        try:
            self.overlay.grab_release()
        except:
            pass
            self.overlay.place_forget()
            
        
    def set_form_mode(self, active):
        if active:
            self.root.protocol("WM_DELETE_WINDOW", self.disable_close)
            self.disable_menu()
        else:
            self.root.protocol("WM_DELETE_WINDOW", self.root.destroy)
            self.enable_menu()
        
    def disable_close(self):
        messagebox.showwarning("FTMS Pro|Restricted", "Please Complete the task before exiting.")
        
    def enable_close(self):
        self.root.protocol("WM_DELETE_WINDOW", self.root.destroy)
        
   
 
if __name__ == "__main__":
    root = tk.Tk()
    FontManager.register_fonts()
    app = FTMSApp(root)
    root.mainloop()
