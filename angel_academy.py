# ==========================================================
# ANGEL ACADEMY
# Smart Learning Engine for FTMS FleetPro
# Version : 1.0
# Created by : Thankappan Dharmanathan
# Powered by : Angel AI
# ==========================================================

import tkinter as tk
from tkinter import ttk
from datetime import datetime

class AngelAcademy:

    def __init__(self, parent):

        self.parent = parent

        self.lessons = {
            "Vehicles": self.lesson_vehicles,
            "Drivers": self.lesson_drivers,
            "Fuel": self.lesson_fuel,
            "Repairs": self.lesson_repairs,
            "Insurance": self.lesson_insurance,
            "Accidents": self.lesson_accidents,
            "Reports": self.lesson_reports
        }

        self.knowledge = {
                        "system":{"what is ftms fleetpro": "here its explanation?   "}
        }
            
    def start(self):
        self.show_main_menu()

    def show_main_menu(self):

        win = tk.Toplevel(self.parent)
        win.title("🎓 Angel Academy")
        win.geometry("700x500")

        tk.Label(
            win,
            text="Welcome to Angel Academy",
            font=("Calibri",18,"bold")
        ).pack(pady=10)

        tk.Label(
            win,
            text="Select a lesson to begin learning.",
            font=("Calibri",11)
        ).pack()

        listbox = tk.Listbox(win,font=("Calibri",12))

        for lesson in self.lessons:
            listbox.insert(tk.END, lesson)

        listbox.pack(fill="both",expand=True,padx=20,pady=10)

        def open_lesson():
            sel = listbox.curselection()
            if sel:
                lesson = listbox.get(sel[0])
                self.lessons[lesson]()

        ttk.Button(
            win,
            text="Start Lesson",
            command=open_lesson
        ).pack(pady=10)

    # ---------------------------------------------------
    # LESSONS
    # ---------------------------------------------------

    def lesson_vehicles(self):
        self.show_lesson(
            "Vehicles",
            "A vehicle is the heart of FleetPro.\n\n"
            "Each vehicle has:\n"
            "• Plate Number\n"
            "• Brand\n"
            "• Model\n"
            "• Year\n"
            "• Capacity\n"
            "• Current Odometer\n"
            "• Status"
        )

    def lesson_drivers(self):
        self.show_lesson(
            "Drivers",
            "Every driver is linked to vehicles and trips.\n"
            "Store licence, phone, nationality and status."
        )

    def lesson_fuel(self):
        self.show_lesson(
            "Fuel",
            "Fuel records calculate mileage and fuel efficiency."
        )

    def lesson_repairs(self):
        self.show_lesson(
            "Repairs",
            "Repairs record maintenance history and repair costs."
        )

    def lesson_insurance(self):
        self.show_lesson(
            "Insurance",
            "Insurance records issue date, expiry date and company."
        )

    def lesson_accidents(self):
        self.show_lesson(
            "Accidents",
            "Record accident date, driver, vehicle and repair status."
        )

    def lesson_reports(self):
        self.show_lesson(
            "Reports",
            "Reports analyse FleetPro data for management decisions."
        )

    # ---------------------------------------------------

    def show_lesson(self,title,text):

        lesson = tk.Toplevel(self.parent)
        lesson.title("Angel Academy - " + title)
        lesson.geometry("650x450")

        tk.Label(
            lesson,
            text=title,
            font=("Calibri",18,"bold")
        ).pack(pady=10)

        txt = tk.Text(
            lesson,
            wrap="word",
            font=("Calibri",12)
        )

        txt.pack(fill="both",expand=True,padx=10,pady=10)

        txt.insert("1.0",text)
        txt.config(state="disabled")

        ttk.Button(
            lesson,
            text="Close",
            command=lesson.destroy
        ).pack(pady=10)