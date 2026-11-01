import tkinter as tk
from tkinter import messagebox

from admin_auth import change_admin_password


class AdminPasswordPage:

    def __init__(self, parent):
        self.parent = parent

        self.form_frame = tk.Frame(parent, bg="#3abcd6", bd=3, relief="ridge",
                                   highlightthickness=1, highlightbackground="white")
        self.form_frame.place(relx=0.5, rely=0.4, anchor="center", width=600, height=300)

        self.inner_frame = tk.Frame(self.form_frame, bg="#d2d3d3")
        self.inner_frame.place(relx=0.5, rely=0.5, anchor="center", width=500, height=230)

        tk.Label(self.inner_frame, text="Set / Change Admin Password", bg="#d2d3d3",
                 font=("Segoe UI", 13, "bold")).grid(row=0, column=0, columnspan=2, pady=(12, 8))

        self.old_var = tk.StringVar()
        self.new_var = tk.StringVar()
        self.confirm_var = tk.StringVar()

        self.old_entry = self._add_row(1, "Old Password", self.old_var)
        self.new_entry = self._add_row(2, "New Password", self.new_var)
        self.confirm_entry = self._add_row(3, "Confirm Password", self.confirm_var)

        tk.Button(self.inner_frame, text="SAVE", width=20, height=2,
                  command=self.save_password).grid(row=4, column=0, columnspan=2, pady=15)

    def _add_row(self, row, text, variable):
        tk.Label(self.inner_frame, text=text, bg="#d2d3d3").grid(row=row, column=0, padx=10, pady=5, sticky="e")
        entry = tk.Entry(self.inner_frame, textvariable=variable, show="*", width=25)
        entry.grid(row=row, column=1, padx=10, pady=5, sticky="w")
        entry.bind("<Return>", lambda e: self.save_password())
        return entry

    def save_password(self):
        success, message = change_admin_password(
            self.old_var.get(), self.new_var.get(), self.confirm_var.get())
        if success:
            messagebox.showinfo("FTMS PRO: Admin Password", message)
            for variable in (self.old_var, self.new_var, self.confirm_var):
                variable.set("")
            self.old_entry.focus()
        else:
            messagebox.showerror("FTMS PRO: Admin Password", message)
