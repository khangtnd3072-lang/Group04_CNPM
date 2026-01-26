import pyodbc

class Database:
    def __init__(self):
        self.server = "PHUOCTRONG"
        self.database = "AttendanceSystem"
        self.username = "sa"
        self.password = "1234"

    def get_connection(self):
        try:
            return pyodbc.connect(
                "DRIVER={ODBC Driver 17 for SQL Server};"
                f"SERVER={self.server};"
                f"DATABASE={self.database};"
                f"UID={self.username};"
                f"PWD={self.password};"
                "TrustServerCertificate=yes;"
            )
        except Exception as e:
            print("❌ Lỗi kết nối SQL Server:", e)
            return None

db = Database()
