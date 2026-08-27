import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from docx2pdf import convert
import tempfile
import win32com.client
from pypdf import PdfWriter
from PIL import Image, ImageTk
import os
import time
import pythoncom
from ImageEnhancer import ImageEnhancer
import cv2
from scanner_engine import ScannerEngine
import shutil



class GraceScan:
    def __init__(self, parent):
        self.parent = parent
        self.root = parent
        self.scanned_images = []
        self.available_scanners = []
        self.page_count = 0
        self.source_manager = None
        self. image_enhancer = ImageEnhancer()
        self.scanner_engine = ScannerEngine()
        
        #DEFAULT SETTINGS
        DEFAULT_SCAN_SOURCE = "Flatbed"
        DEFAULT_OUTPUT_TYPE = "PDF"
        DEFAULT_DPI = 300
        DEFAULT_COLOUR = "Colour"
        DEFAULT_DOCUMENT_SIZE = "Auto Detect (Default)"
        DEFAULT_SCAN_TYPE = "Document"
        
        self.scan_settings = {
    "scan_source": DEFAULT_SCAN_SOURCE,
    "output_type": DEFAULT_OUTPUT_TYPE,
            "dpi": DEFAULT_DPI,
         "colour": DEFAULT_COLOUR,
  "document_size": DEFAULT_DOCUMENT_SIZE,
      "scan_type": DEFAULT_SCAN_TYPE }
        if isinstance(parent, tk.Tk):
            self.pdf_win = parent
        else:
            self.pdf_win = tk.Toplevel(parent)
        self.output_folder = os.path.join(os.path.expanduser("~"), "Desktop")
        self.pdf_win.title("GraceScan")
        self.pdf_win.state("zoomed")
        self.pdf_win.deiconify()
        self.pdf_win.lift()
        self.pdf_win.attributes("-topmost", True)
        self.pdf_win.after(1000, lambda: self.pdf_win.attributes("-topmost", False))
        #self.pdf_win.transient(parent)
        #self.pdf_win.grab_set()        
        self.main_frame = ttk.Frame(self.pdf_win)
        self.main_frame.pack(fill="both", expand=True)
        self.main_frame.rowconfigure(1, weight=1)
        self.main_frame.columnconfigure(0, weight=2) #LEFT PANEL
        self.main_frame.columnconfigure(1, weight=4) #CENTRE
        self.main_frame.columnconfigure(2, weight=3)
       
    #CREATE UI SECTIONS
        self.create_header()
        self.create_left_panel()
        self.create_preview_panel()
        self.create_bottom_panel()
        self.create_status_bar()
        self.create_right_panel()
        
#BOTTOM PANEL======================================================================================================
    def create_bottom_panel(self):
        pass
    
#STATUS BAR =======================================================================================================
    def create_status_bar(self):
        pass
        
    def move_down(self):
        selected = self.file_list.curselection()
        if not selected:
            return
        index = selected[0]
        #PREVENT MOVING LAST ITEM FURTHER DOWN
        if index == self.file_list.size()-1:
            return
        item = self.file_list.get(index)
        self.file_list.delete(index)
        self.file_list.insert(index+1, item)
        self.file_list.selection_set(index+1)
    
    #HELPER FUNCTION: LIST BOX UP ARROW ⬆
    def move_up(self):
        selected = self.file_list.curselection()
        if not selected:
            return
        index = selected[0]
        #PREVENT MOVING LAST ITEM FURTHER DOWN
        if index == 0:
            return
        item = self.file_list.get(index)
        self.file_list.delete(index)
        self.file_list.insert(index-1, item)
        self.file_list.selection_set(index-1)
        #HELPER FUNCTION: TO REMOVE ANY FILE IF NO MORE NEEDED IN THE LIST BOX
        
    def remove_file(self):
        selected = self.file_list.curselection()
        if not selected:
            return
        self.file_list.delete(selected[0])
    # HELPER FUNCTION: GENERATE PDF

    def select_files(self):
        self.selected_files = filedialog.askopenfilenames(title="Select file(s) to Convert/Merge", 
                                            filetypes=[
                                                ("All Supported", "*.doc *.docx *.xls *.xlsx *.xlsm *.pdf *.jpg  *.tiff *.tif *.jpeg *.bmp *.png *.pptx"),
                                                ("Word Files", "*.doc *.docx"),
                                                ("Excel Files", "*.xls *.xlsx *.xlsm"),
                                                ("Image Files","*jpg*, *.jpeg" "*.png *.bmp *.tif *.tiff")
                                            ], parent=self.pdf_win)
        if self.selected_files:
            self.file_list.delete(0, tk.END)
            for file in self.selected_files:
                self.file_list.insert(tk.END, os.path.basename(file))
                
    def convert_listbox_to_pdf(self):
        word = None
        document = None
        excel = None
        workbook = None
        processed_images = []
        temp_pdf_files = []
        converted_files = []
        writer = PdfWriter()
        pythoncom.CoInitialize()
        convert_files = self.file_list.get(0, tk.END)
        
        """Converts files tracked inside the workspace listbox directly into a compiled PDF file."""
        # 1. Check if the listbox contains items
        if not self.file_list or self.file_list.size() == 0:
            messagebox.showwarning("FTMS Warning", "No files added for PDF convertion")
            return

        # 2. Ask user where to save the compiled PDF layout using Save As Dialog Box
        save_path = filedialog.asksaveasfilename(
            title="Save Compiled PDF As",
            defaultextension=".pdf",
            filetypes=[("PDF Document", "*.pdf")],
            initialfile="Compiled_Vehicle_Documents.pdf"
        )
        #ARRAMGE FILES SAME ORDER AS LISTBOX
        ordered_names = list(self.file_list.get(0, tk.END))
        ordered_files = []
        for name in ordered_names:
            for path in self.selected_files:
                if os.path.basename(path).strip().lower()==name.strip().lower():
                    ordered_files.append(path)
                    break
                print("TOTAL FILES : ", len(ordered_files))
                for f in ordered_files:
                    print("READY :", f)
        total_files = len(ordered_files)
        # Exit execution safely if the user cancels out of the Save Dialog window
        if not save_path:
            return
        try:
            word = None
            self.show_progress()
            for index, filepath in enumerate(ordered_files):
                self.update_progress(index + 1, total_files)
                # Loop dynamically to load and transform valid local image format configurations
                if not os.path.exists(filepath):
                    continue
                ext = os.path.splitext(filepath)[1].lower()
                
    #CHECKING FOR IMAGES FILES AND FOR PDF CONVERSION
                if ext in [".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff"]:
            
                    img = Image.open(filepath)
                    # Force RGB channel mapping mode configurations to ensure compatibility with modern PDF profiles
                    if img.mode in ("RGBA", "P"):
                        img = img.convert("RGB")
                        
                    processed_images.append(img.copy())
    #CHECKING FOR PDF FILES AND FOR MERGING
                elif ext == ".pdf":
                    converted_files.append(filepath)
            
    #CHECKING FOR IF EXCEL FILES ADD FOR EXPORTING
                elif ext in [".xlsx", ".xlsm", ".xls"]:
                    try:
                        if excel is None:
                            excel = win32com.client.DispatchEx("Excel.Application")
                            excel.visible = False
                        workbook = excel.Workbooks.Open(filepath)
                        #KEEP USER'S ORIGINAL EXCEL PAGE SETUP 
                        for sheet in workbook.Worksheets:
                            sheet.PageSetup.Zoom = False
                        temp_pdf = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf").name
                        workbook.ExportAsFixedFormat(Type=0, Filename=temp_pdf, Quality=0, 
                        IncludeDocProperties=True, IgnorePrintAreas=False, OpenAfterPublish=False)
                        workbook.Close(False)
                        temp_pdf_files.append(temp_pdf)
                        converted_files.append(temp_pdf)
                    except Exception as e:
                        print("EXCEL EROR: ",e)
                    finally:
                        try:
                            if excel:
                                excel.Close(False)
                        except:
                            pass
                        excel = None
    #CHECKING FOR WORD DOCUMENTS AND PDF CONVERSION
    
                elif ext in [".docx", ".doc"]:
                    
                    try:
                        if word is None:
                            word = win32com.client.DispatchEx("Word.Application")
                            word.Visible = False
                            word.DisplayAlerts = False
                        temp_pdf = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf").name
                        document = word.Documents.Open(os.path.abspath(filepath), ReadOnly = True)
                        document.ExportAsFixedFormat(
                        OutputFileName = os.path.abspath(temp_pdf), ExportFormat=17,
                        OpenAfterExport=False, OptimizeFor=0, CreateBookmarks=0)
                        converted_files.append(temp_pdf)
                        temp_pdf_files.append(temp_pdf)
                        document.Close(False)
                    except:
                            pass
                            document = None
                            
            if not converted_files:
                messagebox.showerror("Conversion Failed", "None of the specified file targets could be correctly read as image files.")
                return
    
            if processed_images:
                image_temp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf").name
                processed_images[0].save(image_temp, save_all = True,
                append_images = processed_images[1:])
                writer.append(image_temp)
                
            for pdf_file in converted_files:
                try:
                    if os.path.exists(pdf_file) and os.path.getsize(pdf_file)>0:
                        writer.append(pdf_file)
                        print("ADDED TO FINAL PDF:", pdf_file)
                except Exception as e:
                    print("MERGE ERROR: ", pdf_file, e)
                    
            try:
                if word:
                    word.Quit()
            except:
                pass
            
            try:
                if excel:
                    excel.Quit()
            except:
                pass
            pythoncom.CoUninitialize()        
            
            #FINAL OUTPUT PDF
            if len(writer.pages)==0:
                messagebox.showerror("PDF Error", "No pages added to final PDF")
                return
            with open(save_path, "wb") as final_pdf: writer.write(final_pdf)
            self.close_progress()
            
    #CLEAN UP SECTION
            for temp_file in temp_pdf_files:
                try:
                    if os.path.exists(temp_file):
                        os.remove(temp_file)
                except Exception:
                    pass
            try:
                if processed_images and os.path.exists(image_temp):
                    os.remove(image_temp)
            except Exception:
                pass
                

    # FINAL SUCCESS MESSAGE WITH DETAILS
            input_count = len(ordered_files)
            converted_count = len(converted_files)
            
            answer = messagebox.askyesno(
                "GraceScan", 
                f"PDF conversion finished successfully!\n\n" f"Total Files Converted       :{total_files}\n" 
                f"Input Files                         :{input_count}\n"
                f"Processed Files                 :{converted_count}\n\n"
                f"Saved File Target Destination  :\n" f"{save_path}\n\n"
                f"Do you want to open the PDF now.....?")
            if answer:
                os.startfile(save_path)
        except Exception as e:
            try:
                self.close_progress()
            except:
                pass
    
    
    def create_header(self):
        self.header_frame = tk.Frame(self.main_frame)
        self.header_frame.grid(row=0, column=0, columnspan=3, sticky="ew")
        self.header_frame.columnconfigure(1, weight=1)
        
        title = ttk.Label(self.header_frame, text="GraceScan", font=("Segoe UI", 20,"bold"))
        title.grid(row=0, column=0, padx=10, sticky="W")
        
        version = ttk.Label(self.header_frame, text="Scan Documents & convert | Convert your Documents to PDF", font=("Segoe UI", 10))
        version.grid(row=1, column=0, padx=12, sticky="w")
        
        status = ttk.Label(self.header_frame, text="Version 1.0", foreground="green", font=("Segoe UI", 10,"bold"))
        status.grid(row=0, column=2, padx=20, sticky="e")
     
    def create_left_panel(self):
        self.left_panel=tk.Frame(self.main_frame, width=75)
        self.left_panel.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
        self.left_panel.grid_propagate(False)
        self.left_panel.rowconfigure(0, weight=0)
        self.left_panel.rowconfigure(1, weight=0)
        self.left_panel.rowconfigure(2, weight=1)
        self.left_panel.columnconfigure(0, weight=1)
        self.scanner_frame = ttk.LabelFrame(self.left_panel,text="Scanner Settings", padding=10)
        self.scanner_frame.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        
    #REFRESH BUTTON
      
    
    # FRAME FOR SCANNER COMBO + REFRESH BUTTON  ====================================================================================
        ttk.Label(self.scanner_frame, text="Scanner").grid(row=0, column=0, padx=10, pady=(10, 5), sticky="w")
        self.scanner_select_frame = ttk.Frame(self.scanner_frame)
        self.scanner_select_frame.grid(row=1, column=0, padx=10, pady=(0,10), sticky="ew")
        self.scanner_select_frame.columnconfigure(0, weight=1)
        self.scanner_frame.columnconfigure(0, weight=1)
        self.scanner_frame.columnconfigure(1, weight=0)
    
    #SCANNER COMBO
        self.scanner_combo= ttk.Combobox(self.scanner_select_frame, state="readonly", width=30)
        self.scanner_combo.grid(row=0, column=0,  sticky="ew")
        self.scanner_combo.bind("<<ComboboxSelected>>",self.on_scanner_selected)
        
    #REFRESH BUTTON
        self.refresh_btn = ttk.Button(self.scanner_select_frame, text="Refresh", width=10, command=self.load_scanners)
        self.refresh_btn.grid(row=0, column=1, padx=(5,0))
        self.status_frame = ttk.Frame(self.scanner_frame)
        self.status_frame.grid(row=2, column=0, padx=10, pady=(5,10), sticky="w")
        ttk.Label(self.status_frame, text="Status : ").pack(side="left")
        self.scanner_status = ttk.Label(self.status_frame, text="Searching...", foreground="blue")
        self.scanner_status.pack(side="left", padx=(5,0))
        
    # SCAN SOURCE COMBO BOX ====================================================================================
        ttk.Label(self.scanner_frame, text="Scan Source").grid(row=4, column=0, padx=10, pady=(10, 5), sticky="w")
        self.scan_source_combo = ttk.Combobox(self.scanner_frame, values=["Feeder","Flatbed", "Auto Detect"], state="readonly", width=28)
        self.scan_source_combo.current(1)
        self.scan_source_combo.grid(row=5, column=0, padx=10, pady=(0,10), sticky="ew")
        
    # SCAN OUTPUT TYPE COMBO BOX ====================================================================================
        ttk.Label(self.scanner_frame, text="Output Type").grid(row=6, column=0, padx=10, pady=(10, 5), sticky="w")
        self.output_type_combo = ttk.Combobox(self.scanner_frame, values=["PDF","JPEG", "PNG"], state="readonly", width=7)
        self.output_type_combo.current(0)
        self.output_type_combo.grid(row=7, column=0, padx=10, pady=(0,10), sticky="ew")
        
        self.output_folder_btn = ttk.Button(self.scanner_frame, text="📂 Browse:", command=self.browse_output_folder)
        self.output_folder_btn.grid(row=6, column=1, pady=(10,5), sticky="ew")
        self.output_folder_label = ttk.Label(self.scanner_frame, text="", width=14, anchor="w", justify="left", foreground="#1D025B")
        self.output_folder_label.grid(row=7, column=1, padx=5,pady=(0,10), sticky="w")
    
    #RESOLUTION DPI    ================================================================================================
        ttk.Label(self.scanner_frame, text="Resolution").grid(row=8, column=0, padx=10, pady=(10, 5), sticky="w")
        self.dpi_combo = ttk.Combobox(self.scanner_frame, values=["100", "150", "200", "300", "600"], state="readonly", width=28)
        self.dpi_combo.current(3)
        self.dpi_combo.grid(row=9, column=0, padx=10, pady=(0,10), sticky="ew")
    
    #COLOUR MODE   ====================================================================================================
        ttk.Label(self.scanner_frame, text="Colour").grid(row=10, column=0, padx=10, pady=(10, 5), sticky="w")
        self.colour_combo = ttk.Combobox(self.scanner_frame, values=["Colour", "Grayscale", "Black & White"], state="readonly", width=28)
        self.colour_combo.current(0)
        self.colour_combo.grid(row=11, column=0, padx=10, pady=(0,10), sticky="ew")
        
    #DOCUMENT SIZE   ====================================================================================================
        ttk.Label(self.scanner_frame, text="Document Size").grid(row=12, column=0, padx=10, pady=(10, 5), sticky="w")
        self.document_size_combo = ttk.Combobox(self.scanner_frame, values=["Auto Detect(Default)", "A4", "A5", "A6","Letter",
        "Legal", "Business Card", "ID Card", "Passport", "Photo (4x6)", "Custom Size"], state="readonly", width=28)
        self.document_size_combo.current(0)
        self.document_size_combo.grid(row=13, column=0, padx=10, pady=(0,10), sticky="ew")
        
    #SCAN  TYPE   ====================================================================================================
        ttk.Label(self.scanner_frame, text="Scan Type").grid(row=14, column=0, padx=10, pady=(10, 5), sticky="w")
        self.scan_type_combo = ttk.Combobox(self.scanner_frame, values=["Document", "Receipt", "Invoice", "Photo","Business Card",
        "ID Card", "Passport"], state="readonly", width=28)
        self.scan_type_combo.current(0)
        self.scan_type_combo.grid(row=15, column=0, padx=10, pady=(0,10), sticky="ew")
        
    # SCAN BUTTON
        self.scan_btn = ttk.Button(self.scanner_frame, text="SCAN DOCUMENT", command=self.scan_document)
        self.scan_btn.grid(row=16, column=0, columnspan=2, pady=20, sticky="ew")
        self.load_scanners()
        
    def create_right_panel(self):
        self.right_panel=tk.Frame(self.main_frame)
        self.right_panel.grid(row=1, column=2, padx=5, pady=5, sticky="nsew")
        self.right_panel.rowconfigure(0, weight=1)
        self.right_panel.rowconfigure(1, weight=0)
        self.right_panel.rowconfigure(2, weight=0)
        self.right_panel.columnconfigure(0, weight=1)
        
        self.right_panel.grid_propagate(False)
        
        self.file_list_frame = ttk.LabelFrame(self.right_panel, text="Files to Convert", padding=10, height=220)
        self.file_list_frame.grid(row=0, column=0, padx=5, pady=5, sticky="new")
        self.file_list_frame.columnconfigure(0, weight=1)
        self.file_list_frame.columnconfigure(1, weight=0)
        
        self.convert_frame = ttk.LabelFrame(self.right_panel, text="Document(s) to Convert", padding=10)
        self.convert_frame.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        tk. Button(self.file_list_frame, text="Select the File(s)/Merge", command=self.select_files, width=22, 
                                                       justify="left").grid(row=0, column=0, columnspan=2, pady=(5,10))
        
        self.file_list=tk.Listbox(self.file_list_frame, width=27, height=15, selectmode=tk.SINGLE)
        self.file_list.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
        
        self.convert_pdf_btn = ttk.Button(
            self.file_list_frame, 
            text="Convert to PDF", 
            command=self.convert_listbox_to_pdf, width=22
        )
        self.convert_pdf_btn.grid(row=2, column=0, padx=5, pady=(5,10), sticky="ew")
        
        button_frame=ttk.Frame(self.file_list_frame)
        button_frame.grid(row=1, column=1, padx=(5,0), pady=5, sticky="n")
        tk.Button(button_frame, text="⬆", command=self.move_up, width=2 ).pack(pady=8)
        tk.Button(button_frame, text="⬇", command=self.move_down, width=2).pack(pady=8)
        tk.Button(button_frame,text="\u2702", command=self.remove_file,font=("Segoe UI Symbol", 12, "bold"), width=2).pack(pady=8)
        
    def create_preview_panel(self):
        self.center_panel=tk.Frame(self.main_frame)
        self.center_panel.grid(row=1, column=1, padx=5, pady=0, sticky="nsew")
        self.center_panel.rowconfigure(1, weight=1)
        self.center_panel.columnconfigure(1, weight=1)
        
        self.center_panel.grid_propagate(True)
        self.toolbar_frame = ttk.LabelFrame(self.center_panel, text="Preview Toolbar", padding=5)
        self.toolbar_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        
        self.thumbnail_frame = ttk.LabelFrame(self.center_panel, text="Page Thumbnails", padding=5)
        self.thumbnail_frame.grid(row=1, column=0, sticky="nsw", padx=5, pady=5)
        
        self.preview_frame = ttk.LabelFrame(self.center_panel, text="Preview", padding=5)
        self.preview_frame.grid(row=1, column=1, sticky="nsew", padx=5, pady=5)
        
        self.navigation_frame = ttk.Frame(self.center_panel)
        self.navigation_frame.grid(row=2, column=0, columnspan=2, sticky="nsew", padx=5, pady=5)
        
    def show_progress(self, title ="GraceScan", text="Progressing"):
     #INDETERMINATE PROGRESS BAR
        self.progress_win = tk.Toplevel(self.pdf_win)
        self.progress_win.title("GraceScan")
        self.progress_win.geometry("350x120")
        self.progress_win.resizable(False, False)
        tk.Label(self.progress_win, text=text).pack(pady=10)
        self.progress = ttk.Progressbar(self.progress_win, mode="determinate", length=300, maximum=100)
        self.progress.pack(pady=10)
        self.progress["value"]=0
        self.progress_win.update()
        
    def update_progress(self, current, total):
        if total ==0:
            return
        percent = (current / total) * 100
        self.progress["value"] = percent
        self.progress_win.update()
        
    def browse_output_folder(self):
        folder = filedialog.askdirectory(title="Select Output Folder")
        if folder:
            display = os.path.basename(folder)
            self.output_folder = folder
            labeloutput="📂..\\" + display
            if len(display)>16:
                labeloutput="📂..\\" + display[-15:]
            self.output_folder_label.config(text=labeloutput)

    def on_scanner_selected(self, event=None):

        scanner = self.scanner_combo.get()

        self.scanner_status.config(
            text="Scanner Initializing...",
            foreground="blue"
        )

        if self.scanner_engine.connect_scanner(scanner):

            self.scanner_status.config(
                text="Scanner Ready",
                foreground="green"
            )

            self.scan_btn.config(state="normal")

        else:

            self.scanner_status.config(
                text="Connection Failed",
                foreground="red"
            )

            self.scan_btn.config(state="disabled")

        
    def scan_document(self):
        # Update scan settings from the UI
        self.scan_settings["scan_source"] = self.scan_source_combo.get()
        self.scan_settings["output_type"] = self.output_type_combo.get()
        self.scan_settings["dpi"] = int(self.dpi_combo.get())
        self.scan_settings["colour"] = self.colour_combo.get()
        self.scan_settings["document_size"] = self.document_size_combo.get()
        self.scan_settings["scan_type"] = self.scan_type_combo.get()

        print("Current Scan Settings:", self.scan_settings)
        print("A: Scan Button Clicked")
        self.scan_btn.config(state="disabled")
        if not self.veryify_selected_scanner():
            return
        try:
            scanner_name = self.scanner_combo.get()
            image_file = self.scanner_engine.scan_page(scanner_name=self.scanner_combo.get(), settings=self.scan_settings)
            if image_file:
                image_file = self.image_enhancer.autodetect_and_crop(image_file)
            scan_source = self.scan_settings["scan_source"]
            output_type = self.scan_settings["output_type"]
            dpi = self.scan_settings["dpi"]
            colour = self.scan_settings["colour"]
            document_size = self.scan_settings["document_size"]
            scan_type = self.scan_settings["scan_type"]
            
            if scanner_name =="" or scanner_name == "No Scanner Found":
                messagebox.showerror("GraceScan", "Scanner is not added\n Please click Refresh and select Scanner")
                return
            
            self.update_status("Opening Scanner...", "green")
            self.root.update_idletasks()
            
            #START SCANNING
            self.update_status("Scanner Initializing...","blue")
            self.root.update_idletasks()
            #source.RequestAcquire(0, 0)
            #handle = None
            #info = None
            #if scan_source=="Flatbed" and scan_type=="ID Card":
            #    self.processing_id_card(source)
            #    return
            #
            #try:
            #    self.update_status("Receiving Image...","blue")
            #    self.root.update_idletasks()
            #    
            #    while True:
            #        try:
            #            self.update_status(f"Scanning Page {self.page_count + 1}", "blue")
            #            self.root.update_idletasks()
            #            print("B: About to acquire image")
            #            handle, info = source.XferImageNatively()
            #        except Exception as e:
            #            print("TWAIN Error:", e)
            #            raise
            #        if not handle:
            #            break
            #        self.update_status("Saving Document...", "blue")
            #        self.root.update_idletasks()
            #        image = twain.DIBToBMFile(handle)
            #        temp_file = os.path.join(tempfile.gettempdir(), f"GraceScan_{time.time()}.jpg")
            #        with open(temp_file, "wb") as f:
            #            f.write(image)
            #        self.scanned_images.append(temp_file)
            #        self.page_count += 1
            #    self.update_status(f"{self.page_count} Documents Scanned", "green")
            #    self.root.update_idletasks()
            #    
            #except Exception as e:
            #    self.update_status("Scan Failed", "red")
            #    try:
            #        source.destroy()
            #    except:
            #        pass
            #    messagebox.showerror("GraceScan", "No Scanned Image Received.\n\nPlease Check Scanner or Place Document")
            #    return
            
            if image_file: 

                #Save according to the user's selected output
                final_file = self.save_scanned_file(image_file)
                self.scanned_images.append(final_file)
                self.page_count += 1
                self.update_status(f"{self.page_count} Document(s) Scanned", "green")
                self.scanner_status.config(text=f"{self.page_count} Document(s) Scanned",
                foreground="green")
        except Exception as e:
            import traceback
            messagebox.showerror("Scan Error", traceback.format_exc())
            self.update_status("Scan Failed", "red")
            
    #SEARCHING SCANNER DRIVER FILES FROM THE PRESENT SYSTEM
    
    def update_status(self, text, colour="green"):
        self.scanner_status.config(text=text, foreground=colour)


    def load_scanners(self):
        scanner_list = self.scanner_engine.detect_scanners()
        if scanner_list: 
            self.scanner_combo["values"] = scanner_list
            self.scanner_combo.current(0)
            self.on_scanner_selected()
            
        else:
            self.scanner_combo["values"] = ["No Scanner Found"]
            self.scanner_combo.current(0)
            self.scanner_status.config(
                text="No Scanner Found",
                foreground="red")

        return scanner_list


    def save_scanned_file(self, temp_file):
        try:
            print("===== SAVE SCANNED FILE =====")
            print("Temp File :", temp_file)
            print("Output Type :", self.scan_settings["output_type"])
            print("Output Folder :", self.output_folder)

            output_type = self.scan_settings["output_type"].lower()
            filename = f"GraceScan{self.page_count + 1}"

            if output_type == "pdf":

                final_file = os.path.join(
                    self.output_folder,
                    filename + ".pdf"
                )

                print("Opening image...")
                img = Image.open(temp_file)

                print("Image Mode:", img.mode)

                if img.mode != "RGB":
                    img = img.convert("RGB")

                print("Saving PDF:", final_file)
                img.save(final_file, "PDF")

            elif output_type in ("jpg", "jpeg"):

                final_file = os.path.join(
                    self.output_folder,
                    filename + ".jpg"
                )

                Image.open(temp_file).save(final_file, "JPEG")

            elif output_type == "png":

                final_file = os.path.join(
                    self.output_folder,
                    filename + ".png"
                )

                Image.open(temp_file).save(final_file, "PNG")

            elif output_type == "bmp":

                final_file = os.path.join(
                    self.output_folder,
                    filename + ".bmp"
                )

                shutil.copy2(temp_file, final_file)

            else:

                final_file = temp_file

            if os.path.exists(temp_file):
                os.remove(temp_file)

            print("Final File:", final_file)

            return final_file

        except Exception as e:
            import traceback
            print(traceback.format_exc())
            raise
    
     
    
    def processing_id_card(self, source):
        scan_source = self.scan_settings["scan_source"]
        scan_type = self.scan_settings["scan_type"]
        if scan_source=="Flatbed" and scan_type=="ID Card":
            front_image = self.acquire_image(source)
            result = messagebox.askokcancel("GraceScan", "Front side Scanned Successfully.\n\n" 
                                            "Please place the BACKSIDE of the ID Card on the scanner,\n"
                                            "then click OK to continue")
            if not result:
                return
            back_image = self.acquire_image(source)
            
    def acquire_image(self, source):
        print("ACQUIRE IMAGE SECTION REACHED")
        handle, info = source.XferImageNatively()
        image = twain.DIBToBMFile(handle)
        temp_file = os.path.join(tempfile.gettempdir(), f"GraceScan_{time.time()}.jpeg")
        with open(temp_file, "wb") as f:
            f.write(image)
        print("STEP 2:  Enhancing Image")
        #INVITING ENHANCER PROGRAM TO ENHANCE THE IMAGE
        image = cv2.imread(temp_file)
        image = ImageEnhancer.enhance_image(image)
        cv2.imwrite(temp_file, image)
        #SAVE A COPY TO THE SELECTED OUTPUT FOLDER
        filename = os.path.basename(temp_file)
        final_file = os.path.join(self.output_folder, filename)
        try:
            shutil.copy2(temp_file, final_file)
        except Exception:
            pass
        self.scanned_images.append(final_file)
        self.page_count += 1
        return temp_file
        
    def veryify_selected_scanner(self):
        scanner_name = self.scanner_combo.get().strip()
        if not scanner_name:
            messagebox.showwarning("GraceScan", "Please Select a Scanner")
            return False
        scanners = self.load_scanners()
        if scanner_name not in scanners:
            messagebox.showerror("Scanner Not Found", f"The Selected scanner\n\n'{scanner_name}'\n\n is not available,\n\nReconnect the scanner or select another scanner.")
            return False
        return True

    
    def close_progress(self):
        self.progress["value"]=100
        self.progress_win.update()
        time.sleep(0.5)
        self.progress_win.destroy()

    
if __name__=="__main__":
    root=tk.Tk()
    root.withdraw()
    GraceScan(root)
    root.mainloop()
