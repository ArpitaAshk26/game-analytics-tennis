from database.db_connection import DatabaseConnection

def test_connection():
    try:
        db = DatabaseConnection()
        conn = db.get_pyodbc_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT @@VERSION")
        row = cursor.fetchone()
        print("✓ Database connection successful!")
        print(f"SQL Server Version: {row[0][:50]}...")
        conn.close()
    except Exception as e:
        print(f"✗ Connection failed: {e}")

if __name__ == "__main__":
    test_connection()