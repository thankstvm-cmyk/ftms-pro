import tkinter as tk
from tkinter import messagebox

class LoginDialog:
    
    def __init__ (self, parent, on_success):
        self.parent = parent
        self.on_success = on_success # FOR CALL BACK

    def show_login(self):
        self.win = tk.Toplevel(self.parent)
        self.win.title("Admin Login")
        self.win.update_idletasks()
        width = 300
        height = 150
        screen_width = self.win.winfo_screenwidth()
        screen_height = self.win.winfo_screenheight()
        x = int((screen_width/2)-(width/2))
        y = int((screen_height/2)-(height/2))
        self.win.geometry(f"{width}x{height}+{x}+{y}")
        self.win.resizable(False, False)
        self.win.grab_set()
        tk.Label(self.win, text="Enter Password", font=("Arial", 13)).pack(pady=10)
        self.pwd_var = tk.StringVar()
        entry = tk.Entry(self.win, textvariable=self.pwd_var, show="*")
        entry.pack(pady=5)
        entry.focus()
        tk.Button(self.win, text="Login", command=self.check_password).pack(pady=10)        
        self.win.bind("<Return>", lambda e: self.check_password())
        
    def check_password(self):
        if self.pwd_var.get()=="Admin123":
            self.win.destroy()
            self.on_success()
        else:
            messagebox.showerror("FTMS Error:", "Wrong Password")

    
        