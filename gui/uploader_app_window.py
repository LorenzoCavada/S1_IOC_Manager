import validators, json
import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime

from utils.log_handler import logger 
from config.config_loader import config

from gui.custom_messagebox import YesNoDialogBox, InfoDialogBox, ErrorDialogBox

from data.S1_IOC_interactor import upload_ioc_to_s1, get_s1_ioc_by_value

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("green")

class UpdateIOCDialogBox(ctk.CTkToplevel):
    def __init__(self, parent, data):
        super().__init__(parent)
        self.title("IOC Already uploaded on S1")

        self.geometry(f"500x450")
        self.resizable(False, False)

        self.wait_visibility()
        self.grab_set()  # Make it modal

        # Message
        self.label = ctk.CTkLabel(self, text="The IOC is already available on S1 with the following value. Do you want to update it?", justify="center")
        self.label.pack(side=tk.TOP, fill="both", padx=5)

        self.json_box = ctk.CTkTextbox(self, state="disabled", text_color="black", font=("Consolas", 10), fg_color="light grey")
        self.json_box.pack(side=tk.TOP, expand=True, fill="both", padx=10, pady=10)

        self.json_box.configure(state="normal") # Temporarily enable
        self.json_box.insert("end", text=f"{data}")
        self.json_box.configure(state="disabled")

        # Buttons frame
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(pady=(0,20))

        self.choice = None
        yes_btn = ctk.CTkButton(btn_frame, text="Update", width=80, command=self._on_yes)
        yes_btn.pack(side="left", padx=10)
        no_btn = ctk.CTkButton(btn_frame, text="Cancel", width=80, command=self._on_no)
        no_btn.pack(side="right", padx=10)

        self.protocol("WM_DELETE_WINDOW", self._on_no)  # Treat window-close as No

    def _on_yes(self):
        self.choice = True
        self.destroy()

    def _on_no(self):
        self.choice = False
        self.destroy()

    def show(self):
        self.wait_window()
        return self.choice

class UserInputFrame(ctk.CTkFrame):
    def __init__(self, master, title:str, example:str):
        super().__init__(master)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure((0,1), weight=1)

        self.label = ctk.CTkLabel(self, text=title, fg_color="transparent")
        self.label.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="ew")

        self.field = ctk.CTkEntry(self, placeholder_text=example)
        self.field.grid(row=1, column=0, padx=10, pady=(10, 0), sticky="ew")

class UploaderAppWindow(ctk.CTkToplevel):
    ip_list:[str]
    domain_list:[str]
    hash_list:[str]
    url_list:[str]

    def __init__(self, parent):
        super().__init__(parent)
        self.title("S1 IOC Uploader")

        self.geometry("500x650")

        self.wait_visibility()
        self.grab_set()  # Make it modal

        self.grid_columnconfigure((0,1), weight=1)
        self.grid_rowconfigure((0,8), weight=1)

        self.title_label = ctk.CTkLabel(self, text="IOC Title*", fg_color="transparent")
        self.title_label.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="sew", columnspan=2)
        self.title_field = ctk.CTkEntry(self, placeholder_text="Example: Malicious IP")
        self.title_field.grid(row=1, column=0, padx=10, pady=(10, 0), sticky="ew", columnspan=2)

        self.description_label = ctk.CTkLabel(self, text="IOC Description*", fg_color="transparent")
        self.description_label.grid(row=2, column=0, padx=10, pady=(10, 0), sticky="ew", columnspan=2)
        self.description_field = ctk.CTkEntry(self, placeholder_text="Example: This IP is known to be associated with malware")
        self.description_field.grid(row=3, column=0, padx=10, pady=(10, 0), sticky="ew", columnspan=2)

        self.ip_address_frame = UserInputFrame(self, "IP", "0.0.0.0")
        self.ip_address_frame.grid(row=4, column=0, padx=10, pady=(10, 0), sticky="nsew")

        self.domain_frame = UserInputFrame(self, "Domain", "www.example.org")
        self.domain_frame.grid(row=4, column=1, padx=10, pady=(10, 0), sticky="nsew")

        self.url_frame = UserInputFrame(self, "URL", "https://malware.org")
        self.url_frame.grid(row=5, column=0, padx=10, pady=(10, 0), sticky="nsew")

        self.hash_frame = UserInputFrame(self, "SHA1", "44D88612FEA8A8F36DE82E1278ABB02F")
        self.hash_frame.grid(row=5, column=1, padx=10, pady=(10, 0), sticky="nsew")

        self.generate_button = ctk.CTkButton(self, text="Validate input", command=self.onclick_generate_button)
        self.generate_button.grid(row=6, column=0, padx=10, pady=10, sticky="ews", columnspan=2)

        self.log_box = ctk.CTkTextbox(self)
        self.log_box.grid(row=7, padx=10, pady=10, sticky="ew", columnspan=2)
        self.log_box.configure(state="disabled", text_color="black", font=("Consolas", 8), fg_color="light grey")  # configure textbox to be read-only
        self.log_box.tag_config('debug_text', foreground='midnight blue')
        self.log_box.tag_config('error_text', foreground='firebrick4')
        self.log_box.tag_config('success_text', foreground='dark green')

        self.s1_button = ctk.CTkButton(self, text="Send to S1", command=self.onclick_upload_ioc, state="disabled")
        self.s1_button.grid(row=8, column=0, padx=10, pady=10, sticky="ews", columnspan=2)

        self.print_log("[INFO] Canvas generated.")

    def show(self):
        self.wait_window()  
        return None
    
    def print_log(self, message):
        logger.print_log(message)

        if("DEBUG" in message):
            self.log_box.configure(state="normal") # Temporarily enable
            self.log_box.insert("end", text=f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {message}\n", tags=("debug_text"))
            self.log_box.configure(state="disabled")
        elif("ERROR" in message):
            self.log_box.configure(state="normal") # Temporarily enable
            self.log_box.insert("end", text=f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {message}\n", tags=("error_text"))
            self.log_box.configure(state="disabled")
        elif("SUCCESS" in message):
            self.log_box.configure(state="normal") # Temporarily enable
            self.log_box.insert("end", text=f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {message}\n", tags=("success_text"))
            self.log_box.configure(state="disabled")
        else:
            self.log_box.configure(state="normal") # Temporarily enable
            self.log_box.insert("end", text=f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {message}\n")
            self.log_box.configure(state="disabled")

    # Handles the validation of the user input, does not check the actual values but only if the fields are populated
    def _verify_user_input(self):
        # Debug message indicating the start of title/description validation
        self.print_log("[INFO] Checking title and description inputs.")
        
        # Check if either the title or description fields are empty
        if not(self.title_field.get() != "" and self.description_field.get() != ""):
            # Show error message if validation fails
            ErrorDialogBox(self, title="Title/Description Error", message="Please provide a valid title and description. These fields cannot be empty.").show()
            self.print_log("[ERROR] Title or description field is empty.")
            return False
        
        # Debug message indicating title/description validation passed
        self.print_log("[INFO] Title and description inputs are valid.")

        # Debug message indicating the start of domain/IP/hash/URL validation
        self.print_log("[INFO] Checking domain, IP, hash, and URL inputs.")
        
        # Check if all of the domain, IP, hash, and URL fields are empty
        if self.domain_frame.field.get() == "" and self.ip_address_frame.field.get() == "" and self.hash_frame.field.get() == "" and self.url_frame.field.get() == "":
            # Show error message if validation fails
            ErrorDialogBox(self, title="Input Error", message="Input fields (Hash, IP, Domain, or URL) cannot all be empty.").show()
            self.print_log("[INFO] All input fields (Hash, IP, Domain, or URL) are empty.")
            return False

        self.print_log("[INFO] Domain, IP, hash, and URL inputs are populated.")
        return True

    @staticmethod
    def _get_input_value_list(values:str, validator):
        # Same logic as domain list+
        result_list = []
        if values != "":
            value_list = values.replace(" ", "")
            value_list = value_list.split(",")
            for value in value_list:
                if validator(value):
                    result_list.append(value)
                    result_list = list(dict.fromkeys(result_list))
                else:
                    self.print_log(f"[ERROR] Error: [{value}] is not a valid IOC. This IOC will be ignored.")
                    ErrorDialogBox(self, title="IOC checking Error", message=f"[{value}]: is not a valid IOC. This IOC will be ignored.").show()
            
            return result_list
        else:
            return []


    def onclick_generate_button(self):
        # Function which handle the generation of file 

        # Start input validation
        self.print_log("[INFO] Validating user input.")
        
        # Proceed only if validation passes
        if self._verify_user_input():
            # Extract data from user input fields
            self.ip_list = self._get_input_value_list(self.ip_address_frame.field.get(), validators.ip_address.ipv4)
            self.domain_list = self._get_input_value_list(self.domain_frame.field.get(), validators.domain)
            self.hash_list = self._get_input_value_list(self.hash_frame.field.get(), validators.hashes.sha1)
            self.url_list = self._get_input_value_list(self.url_frame.field.get(), validators.url)

            # Log that the input has been validated and the UI will be updated
            self.print_log("[SUCCESS] User input has been validated. Enabling lower buttons.")

            # Enable SentinelOne upload button only if any of the IOC lists are populated
            if(len(self.ip_list) > 0 or len(self.domain_list) > 0 or len(self.hash_list) > 0 or len(self.url_list) > 0):
                self.s1_button.configure(state="normal")
            else:
                self.s1_button.configure(state="disabled")

    def _check_ioc_presence(self, ioc_value):
        self.print_log(f"[INFO] Checking if IOC [{ioc_value}] is already uploaded on SentinelOne.")

        ioc_value = get_s1_ioc_by_value(ioc_value)

        if ioc_value != None:
            self.print_log(f"[INFO] The IOC is already uploaded on SentinelOne. Asking if an update is needed.")
            ioc_value = json.dumps(ioc_value, indent=2)
            user_choice = UpdateIOCDialogBox(self, data=ioc_value)
            user_choice = user_choice.show()

            if user_choice:
                self.print_log(f"[INFO] User choose to update the IOC. Moving on with the upload.")
                return True
            else:
                self.print_log(f"[INFO] User choose to not update the IOC. Aborting the upload.")
                return False
        
        self.print_log(f"[INFO] The IOC is new. Moving on with the upload.")
        return True


    def onclick_upload_ioc(self):
        self.print_log("[INFO] Uploading the IOCs to SentinelOne.")
        self.print_log("[INFO] Opening the request body for S1 IOC upload.")

        # IOC types to handle
        ioc_sources = [
            ("IPV4", self.ip_list, config.ip_retention, "IP"),
            ("DNS", self.domain_list, config.dns_retention, "domain"),
            ("SHA1", self.hash_list, config.sha1_retention, "SHA1"),
            ("URL", self.url_list, config.url_retention, "URL")
        ]

        # each ioc list (if not empty) the values will be uploaded to S1.
        for ioc_type, ioc_list, retention_days, label in ioc_sources:
            if ioc_list != [""]:
                for ioc_value in ioc_list:
                    self.print_log(f"[INFO] Preparing to upload {label} [{ioc_value}]. Asking for confirmation.")
        
                    user_choice = YesNoDialogBox(self, title="S1 IOC Upload", message=f"Do you want to upload the {label} [{ioc_value}] to SentinelOne?")
                    user_choice = user_choice.show()

                    if user_choice:
                        if self._check_ioc_presence(ioc_value):
                            # True means that the IOC is new or the user want to refresh it
                            self.print_log(f"[INFO] User confirmation received. Ready to upload {label} [{ioc_value}].")
                            result = upload_ioc_to_s1(ioc_value, ioc_type, int(retention_days), self.title_field.get(), self.description_field.get())

                            if result != None:
                                if result.status_code == 200:
                                    self.print_log(f"[SUCCESS] The {label} [{ioc_value}] has been successfully uploaded.")
                                    InfoDialogBox(self, title="S1 IOC Uploaded", message=f"The {label} [{ioc_value}] has been successfully uploaded. Remember to update the main table!").show()
                                else:
                                    ErrorDialogBox(self, title="S1 IOC Not Uploaded", message=f"The {label} [{ioc_value}] could not be uploaded. Status code: {result.status_code}.").show()
                                    self.print_log(f"[ERROR] The {label} [{ioc_value}] could not be uploaded. Status code: {result.status_code}.")
                            else:
                                ErrorDialogBox(self, title="S1 IOC Not Uploaded", message=f"The {label} [{ioc_value}] could not be uploaded. Exception raised while performing the upload.").show()
                                self.print_log(f"[ERROR] The {label} [{ioc_value}] could not be uploaded. Exception raised while performing the upload.")
                        else:
                            self.print_log(f"[INFO] Upload canceled. {label.capitalize()} [{ioc_value}] will not be uploaded.")
                        
                    

        