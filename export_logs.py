import sqlite3
import csv
from datetime import datetime

def export_to_csv(db_name="attendance.db"):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM attendance_logs")
    rows = cursor.fetchall()
    
    filename = f"exported_logs_{datetime.now().strftime('%Y-%m-%d')}.csv"
    
    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['ID', 'Name', 'Action', 'Timestamp', 'Date'])
        writer.writerows(rows)
    
    print(f"Successfully exported {len(rows)} records to {filename}")
    conn.close()

if __name__ == "__main__":
    export_to_csv()
