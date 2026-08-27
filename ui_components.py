import tkinter as tk
from tkinter import PhotoImage
from globals import COMPANY_NAME, SYSTEM_NAME, HEADER_BG, HEADER_FG, HEADER_FONT, SYSTEM_FONT

def create_header(parent):
    header_frame=tk.Frame(parent, height=80, bg=HEADER_BG)
    header_frame.grid(row=0, column=0, sticky="ew")
    header_frame.grid_columnconfigure(0, weight=1)
    #COMPANY NAME : HEADER
    tk.Label(header_frame, text=COMPANY_NAME, 
            bg=HEADER_BG, fg=HEADER_FG,
            font=HEADER_FONT, anchor="center").grid(row=0, column=0, sticky="ew")
    #SYSTEM NAME : HEADER
    tk.Label(header_frame, text=SYSTEM_NAME, 
            bg=HEADER_BG, fg=HEADER_FG,
            font=SYSTEM_FONT, anchor="center").grid(row=1, column=0, sticky="ew")
   
    return header_frame

    #TITLE NAME
def create_page_title(parent, text):
        title=tk.Label(parent, text=text, font=("Segoe UI", 18, "bold"), bg="#1e3a5f", fg="white", anchor="center")
        title.grid(row=0, column=0, pady=(5,5), sticky="ew")
        return title