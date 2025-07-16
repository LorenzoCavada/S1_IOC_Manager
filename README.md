# S1_IOC_Manager

**S1_IOC_Manager** is an enhanced and lightweight Python-based GUI tool (currently under active development) that interfaces with the **SentinelOne** API to manage IOCs (Indicators of Compromise). Bare in mind that everything is made at Account level, not at site/group level.
This tool provide full IOC management capabilities—allowing users to **view**, **add**, **update**, and **delete** IOCs with ease.

The tool features an intuitive table-based interface displaying all available IOCs. By clicking on any entry, users can quickly access its details or remove it. Additionally, a dedicated upload button launches a guided GUI for creating new IOCs, making IOC management efficient and user-friendly.

---

## 🚀 Features

- ⚙️ **It Works! (Most of the Time)**  
  Still under development—but already functional!

- ✅ **Full IOC Management**  
  Perform all key operations with IOCs via the GUI:
  - **View** all IOCs in a structured table
  - **Add** new IOCs (supports multiple, comma-separated values)
  - **Update** existing IOCs
  - **Delete** individual IOCs with a single click

- 🔌 **Automatic IOC Retrieval**  
  - On startup, the tool connects to the SentinelOne API and fetches all IOCs at the account level. These are cached locally for improved performance and reduce API calls.
  - Click the **"Grab the IOC ✊"** button to re-fetch the latest IOC data from SentinelOne.

- 🧐 **IOC Detail Viewer with Delete Option**  
  Double click on any IOC in the table to view its full `JSON` structure and optionally delete it from SentinelOne.

- 📤 **IOC Upload with Validation**  
  Add new IOCs using a dedicated GUI:
  - Inputs are validated before submission
  - Default threat score: **100** (maximum confidence)
  - Validity duration: **30 days** (configurable in `config.yml`)
  - IOCs are submitted to **SentinelOne Threat Intelligence** at the **account level**, covering all sites and groups

- 🔍 **Advanced Filtering and Wildcard Search**  
  Filter IOCs based on:
  - IOC **value**
  - Uploading **user**
  - **Name**
  - **Description**  
  Wildcards (`%`) are supported for partial matches (e.g. `%malware%`)

- 🪵 **Extensive Logging**  
  Activity logs are saved to:
  - The console, and  
  - A log file named `S1_IOC_manager.log`, created automatically at runtime.

---

## ⚙️ Requirements

- Python **3.7+**
- Dependencies listed in `requirements.txt`

To install the required packages:

```bash
pip install -r requirements.txt
```

---

## 🧪 How to Run

First of all, remember to edit the `config.yml` file in the config folder. An example is available here `config\config.example.yml`

Make sure Python 3 is installed, then simply launch the tool with:

```bash
python3 S1_IOC_manager.py
```

---

## 📦 Project Structure

```bash
├── config/                         # Configuration files and loader
│   ├── config_loader.py            # Loads parameters from config.yml and makes them accessible throughout the app
│   ├── config.example.yml          # Example configuration file with expected parameters (e.g., API key)
│   └── config.yml                  # Actual configuration file (e.g., API key, defaults)
│
├── data/                           # API interaction and data handling
│   ├── db_handler.py               # Manages interaction with the local SQLite database storing IOCs
│   └── S1_IOC_interactor.py        # Handles communication with the SentinelOne API (download/upload)
│
├── gui/                            # GUI components for the application
│   ├── custom_messagebox .py       # Set of message boxes made to match the general UI
│   ├── item_window.py              # Displays the details of a specific IOC
│   ├── uploader_app_window.py      # GUI for uploading new IOCs
│   ├── uploader_app_item.py        # GUI for updating an existing IOC
│   ├── viewer_app_window.py        # Main application window
│   └── viewer_table_frame.py       # Builds and manages the IOC table view
│
├── utils/                          # Utility functions
│   └── log_handler.py              # Handles logging throughout the app
│
├── S1_IOC_manager.py               # Application entry point
└── S1_IOC_manager.log               # Automatically generated log file
```

---

## 🛠 Under Development
🚧 Please note that S1_IOC_manager is a work in progress:

Only the `.py` version is currently available

Additional features and packaging (e.g., .exe, config GUI, advanced export) are being explored.

