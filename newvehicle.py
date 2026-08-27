import tkinter as tk
from tkinter import ttk
from header import create_header

class AddVehicleWindow:

    def __init__(self, parent):
        self.parent = parent

        self.frame = tk.Frame(parent, bg="white")
        self.frame.pack(fill="both", expand=True)
        create_header(self.frame)

        self.create_widgets()

    def create_widgets(self):

        # MAIN CONTAINER
        main_container = tk.Frame(self.frame, bg="white")
        main_container.pack(padx=20, pady=10)

        # VEHICLE INFORMATION
        vehicle_frame = ttk.LabelFrame(main_container, text="Vehicle Information")
        vehicle_frame.pack(side="left", padx=10)

        ttk.Label(vehicle_frame, text="Plate Number").grid(row=0, column=0, padx=10, pady=5)
        ttk.Entry(vehicle_frame).grid(row=0, column=1, padx=10, pady=5)

        ttk.Label(vehicle_frame, text="Brand").grid(row=1, column=0, padx=10, pady=5)
        ttk.Entry(vehicle_frame).grid(row=1, column=1, padx=10, pady=5)

        ttk.Label(vehicle_frame, text="Model").grid(row=2, column=0, padx=10, pady=5)
        ttk.Entry(vehicle_frame).grid(row=2, column=1, padx=10, pady=5)

        # DOCUMENTS FRAME
        documents_frame = ttk.LabelFrame(main_container, text="Vehicle Documents")
        documents_frame.pack(side="right", padx=10)

        tk.Label(
            documents_frame,
            text="Vehicle Image",
            width=25,
            height=8,
            relief="solid"
        ).pack(padx=10, pady=10)

        ttk.Button(
            documents_frame,
            text="Upload Vehicle Image"
        ).pack(pady=5)

        # ACTION BAR
        action_frame = tk.Frame(self.frame, bg="white")
        action_frame.pack(pady=20)

        save_btn = tk.Button(
            action_frame,
            text="SAVE",
            width=15,
            command=self.save_vehicle
        )
        save_btn.pack()

    def save_vehicle(self):
        print("Vehicle Saved")


if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("1000x600")
    app = AddVehicleWindow(root)
    root.mainloop()