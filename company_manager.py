 
from PIL import Image, ImageTk
from config import DATABASE_PATH
import sqlite3
import os
def get_company_details():
        try:
            with sqlite3.connect(DATABASE_PATH) as conn:
                row = conn.execute("SELECT name, logo FROM company LIMIT 1").fetchone()
            return row if row else ("", "")
        except sqlite3.Error:
            return "", ""
        
def show_company_logo(logo_canvas, width=100, height=60):
    _company_name, logo_path = get_company_details()
    logo_canvas.delete("all")
    if logo_path and os.path.exists(logo_path):
        try:
            image = Image.open(logo_path)
            image = image.resize((width,height), Image.LANCZOS)
            logo_canvas.logo_img = ImageTk.PhotoImage(image)
            logo_canvas.create_image((width //2)+5, (height//2)+5, image=logo_canvas.logo_img, anchor="center")
            return
        except Exception:
            pass
    logo_canvas.create_text(150, 72, text="No Logo Available", fill="grey", font=("Arial", 16, "bold"))