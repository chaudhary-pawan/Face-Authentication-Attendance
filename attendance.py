import sqlite3
import os
from datetime import datetime

class AttendanceLogger:
    def __init__(self, db_name="attendance.db"):
        self.db_name = db_name
        self._init_db()

    def _init_db(self):
        """Initialize the SQLite database and create table if not exists."""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        # Create table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS attendance_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                action TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                date_str TEXT NOT NULL
            )
        ''')
        
        conn.commit()
        conn.close()

    def mark_attendance(self, name, action):
        """
        Marks attendance in the SQLite Query.
        """
        now = datetime.now()
        time_str = now.strftime("%H:%M:%S")
        date_str = now.strftime("%Y-%m-%d")
        
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            # Insert record
            cursor.execute('''
                INSERT INTO attendance_logs (name, action, timestamp, date_str)
                VALUES (?, ?, ?, ?)
            ''', (name, action, now.strftime("%Y-%m-%d %H:%M:%S"), date_str))
            
            conn.commit()
            conn.close()
            
            # --- DUAL LOGGING START ---
            # Also write to CSV for easy viewing
            log_dir = "logs"
            if not os.path.exists(log_dir):
                os.makedirs(log_dir)
            csv_path = os.path.join(log_dir, f"attendance_{date_str}.csv")
            
            # Check if header needed
            needs_header = not os.path.exists(csv_path)
            
            import csv
            with open(csv_path, "a", newline="") as f:
                writer = csv.writer(f)
                if needs_header:
                    writer.writerow(["Name", "Action", "Time", "Date"])
                writer.writerow([name, action, time_str, date_str])
            # --- DUAL LOGGING END ---

            return f"{action} Logged (DB+CSV) at {time_str}"
            
        except sqlite3.Error as e:
            return f"DB Error: {e}"

    def get_todays_logs(self):
        """Fetch logs for today to show in UI."""
        date_str = datetime.now().strftime("%Y-%m-%d")
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('SELECT name, action, timestamp FROM attendance_logs WHERE date_str = ? ORDER BY id DESC', (date_str,))
        rows = cursor.fetchall()
        conn.close()
        return rows
