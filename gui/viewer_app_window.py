import tkinter as tk
import customtkinter as ctk

from gui.viewer_table_frame import ViewerTableFrame
from gui.uploader_app_window import UploaderAppWindow

from data import get_s1_ioc, get_s1_filtered_ioc
from utils.log_handler import logger 

ctk.set_default_color_theme("dark-blue")  # Optional theme enhancement
ctk.set_appearance_mode("light")         # Adapts to user's light/dark mode


class ViewerAppWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("S1 IOC Viewer v1")
        logger.print_log(f"[INFO] Generating the canvas. Screen size [{self.winfo_screenwidth()}x{self.winfo_screenheight()}]")

        self.geometry(f'{self.winfo_screenwidth()}x{self.winfo_screenheight()}')

        # Create main search_frame
        search_frame = ctk.CTkFrame(self, fg_color="transparent")
        search_frame.pack(side=ctk.TOP, fill="x", padx=10, pady=10)

        # Left side: Upload button
        left_frame = ctk.CTkFrame(search_frame, fg_color="transparent")
        left_frame.pack(side=tk.LEFT, anchor=tk.W)

        self.upload_button = ctk.CTkButton(left_frame, text="Upload IOC 📝", width=200, command=self.uplaod_ioc)
        self.upload_button.pack(side=tk.LEFT)

        # Right side: Search UI
        right_frame = ctk.CTkFrame(search_frame, fg_color="transparent")
        right_frame.pack(side=tk.RIGHT, anchor=tk.E)

        self.search_entry = ctk.CTkEntry(right_frame, placeholder_text="Filter Value", width=300)
        self.search_entry.pack(side=tk.LEFT, padx=5)

        self.search_type = ctk.CTkOptionMenu(right_frame, values=["Value", "User", "Name", "Description"], width=130)
        self.search_type.pack(side=tk.LEFT, padx=5)

        self.search_button = ctk.CTkButton(right_frame, text="Search 🔍", width=80, command=self.search_ioc)
        self.search_button.pack(side=tk.LEFT)

        logger.print_log("[INFO] Preparing the first IOC table.")
        self.table = ViewerTableFrame(self, get_s1_ioc())
        self.table.pack(side=ctk.TOP, pady=10, padx=10, expand=True, fill="both")

        self.get_ioc_button = ctk.CTkButton(self, text="Grab some fresh IOC ✊", command=self.show_table)
        self.get_ioc_button.pack(side=ctk.BOTTOM, pady=10)

        self.maxsize(1800, 900)

    def show_table(self):
        logger.print_log("[INFO] Updating the IOC table.")

        # destroying the table to refresh it
        if self.table:
            self.table.destroy()
        
        self.table = ViewerTableFrame(self, get_s1_ioc())
        self.table.pack(side=ctk.TOP, pady=10, padx=10, expand=True, fill="both")

    # method handle the search for a specific IOC
    def search_ioc(self):
        search_value = self.search_entry.get()
        search_type = self.search_type.get()

        logger.print_log(f"[INFO] Updating the IOC table filtered for value: [{search_value}].")

        if(self.search_entry.get() == ""):
            logger.print_log(f"[WARNING] User input not found, printing the full table again.")
            self.show_table()
        else:
            if self.table:
                self.table.destroy()
            self.table = ViewerTableFrame(self, get_s1_filtered_ioc(search_value, search_type))
            self.table.pack(side=ctk.TOP, pady=10, padx=10, expand=True, fill="both")

    
    def uplaod_ioc(self):
        logger.print_log("[INFO] S1_IOC_Uploader v.2")
        uploader_window = UploaderAppWindow(self)
        uploader_window.show()
