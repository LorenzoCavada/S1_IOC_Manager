import sqlite3
from utils.log_handler import logger

class IOCDB:
    def __init__(self):
        self.conn = sqlite3.connect(":memory:")
        self.conn.row_factory = sqlite3.Row 
        self.cursor = self.conn.cursor()

    def initialize_schema(self):
        self.cursor.execute("""
            CREATE TABLE iocs (
                num INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                description TEXT,                
                type TEXT,
                value TEXT,
                metadata TEXT,
                source TEXT,
                creationTime DATE,
                updatedAt DATE,
                validUntil DATE
            )
        """)

    def insert_ioc(self, name, description, ioc_type, value, metadata, source, creationTime, updatedAt, validUntil):
        self.cursor.execute("""
            INSERT INTO iocs (name, description, type, value, metadata, source, creationTime, updatedAt, validUntil)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (name, description, ioc_type, value, metadata, source, creationTime, updatedAt, validUntil))

    def search_ioc(self, value):
        self.cursor.execute("SELECT 1 FROM iocs WHERE value = ? LIMIT 1", (value,))
        return self.cursor.fetchone() is not None

    def fetch_all(self):
        self.cursor.execute("SELECT * FROM iocs")
        return self.cursor.fetchall()

    def fetch_filtered(self, search_value, filter_type):
        
        if(filter_type == "Value"):
            self.cursor.execute("SELECT * FROM iocs WHERE value LIKE ?", (f"{search_value}",))
        elif(filter_type =="Name"):
            self.cursor.execute("SELECT * FROM iocs WHERE name LIKE ?", (f"{search_value}",))
        elif(filter_type == "Description"):
            self.cursor.execute("SELECT * FROM iocs WHERE description LIKE ?", (f"{search_value}",))
        elif(filter_type == "User"):
            self.cursor.execute("SELECT * FROM iocs WHERE metadata LIKE ?", (f"{search_value}",))
        elif(filter_type == "Source"):
            self.cursor.execute("SELECT * FROM iocs WHERE source LIKE ?", (f"{search_value}",))

        return self.cursor.fetchall()
    
    def delete_all(self):
        logger.print_log(f"[WARNING] Dropping everything from the S1_IOC_manager internal DB. When starting the application is expected to see this line.")   
        self.cursor.execute("DROP TABLE iocs")
        self.initialize_schema()

    def close(self):
        self.conn.close()

IOC_DB = IOCDB()
IOC_DB.initialize_schema()