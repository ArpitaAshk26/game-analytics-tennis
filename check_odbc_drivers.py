import pyodbc

print("Available ODBC Drivers:")
print("="*50)
for driver in pyodbc.drivers():
    print(f"  - {driver}")
print("="*50)