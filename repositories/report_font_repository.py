import sqlite3
from MODELS.report_font_settings import ReportFontSettings

class ReportFontRepository:
    def __init__(self, db_path):
        self.db_path = db_path
    
    def get_connection(self):
        return sqlite3.connect(self.db_path)
    
    def get_settings(self):
        pass