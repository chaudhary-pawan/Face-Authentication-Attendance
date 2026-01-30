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
            return f"{action} Logged (DB) at {time_str}"
            
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
