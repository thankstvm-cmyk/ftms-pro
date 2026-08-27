import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from datetime import datetime
from edit import open_edit_window   # import edit form

class LoginEdit:
    
    def __init__(self, parent, controller):
        self.parent=parent
        self.controller=controller
        #MAIN CONTAINER
        self.frame=tk.Frame(parent, bg="white")
        self.frame.grid(row=0, column=0, sticky="nsew")


    def open_login(self):
        auth_win = Toplevel(self)
        auth_win.title("Edit Authorization")
        auth_win.geometry("400x300")
        auth_win.grab_set()

        Label(auth_win, text="User Name").pack(pady=5)
        entry_user = Entry(auth_win, width=30)
        entry_user.pack()

        Label(auth_win, text="Reason for Edit").pack(pady=5)
        entry_reason = Entry(auth_win, width=30)
        entry_reason.pack()

        now = datetime.now()
        current_date = now.strftime("%Y-%m-%d")
        current_time = now.strftime("%H:%M:%S")

        Label(auth_win, text=f"Date: {current_date}").pack(pady=5)
        Label(auth_win, text=f"Time: {current_time}").pack(pady=5)

        def proceed():
            user = entry_user.get()
            reason = entry_reason.get()

            if user.strip() == "" or reason.strip() == "":
                messagebox.showerror("Error", "All fields are required")
                return

            auth_win.destroy()

            # Open Edit Form
            open_edit_window(self, user, reason, current_date, current_time)

        Button(auth_win, text="Continue", bg="green", fg="white",
            command=proceed).pack(pady=20)