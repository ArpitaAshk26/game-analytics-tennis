import pyodbc
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os
import urllib

load_dotenv()

class DatabaseConnection:
    def __init__(self):
        self.server = os.getenv('DB_SERVER', 'DESKTOP-FHO99H5\\SQLEXPRESS')
        self.database = os.getenv('DB_NAME', 'TennisAnalytics')
        
    def get_pyodbc_connection(self):
        """Get pyodbc connection for direct SQL execution"""
        conn_str = (
            'DRIVER={SQL Server};'
            f'SERVER={self.server};'
            f'DATABASE={self.database};'
            'Trusted_Connection=yes;'
        )
        print(f"Connecting to: {self.server}/{self.database}")
        return pyodbc.connect(conn_str)
    
    def get_sqlalchemy_engine(self):
        """Get SQLAlchemy engine for pandas integration"""
        # Method 1: Using URL-encoded connection string (RECOMMENDED)
        connection_string = (
            'DRIVER={SQL Server};'
            f'SERVER={self.server};'
            f'DATABASE={self.database};'
            'Trusted_Connection=yes;'
        )
        
        params = urllib.parse.quote_plus(connection_string)
        engine_url = f'mssql+pyodbc:///?odbc_connect={params}'
        
        print(f"SQLAlchemy connecting to: {self.server}/{self.database}")
        return create_engine(engine_url, fast_executemany=True)