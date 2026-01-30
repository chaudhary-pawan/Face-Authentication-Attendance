import csv
import os
from datetime import datetime

class AttendanceLogger:
    def __init__(self, log_dir="logs"):
        self.log_dir = log_dir
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        # Create a new file for today's attendance
        self.date_str = datetime.now().strftime("%Y-%m-%d")
        self.file_path = os.path.join(self.log_dir, f"attendance_{self.date_str}.csv")
        
        self._ensure_file_exists()

    def _ensure_file_exists(self):
        if not os.path.exists(self.file_path):
            with open(self.file_path, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["Name", "Action", "Time", "Date"])

    def mark_attendance(self, name, action):
        """
        Marks attendance.
        Action: 'Punch In' or 'Punch Out'
        Returns: message indicating success or already punched (if you strictly want to enforce one type).
        For this simplified assignment, we just log every event.
        """
        now = datetime.now()
        time_str = now.strftime("%H:%M:%S")
        
        with open(self.file_path, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([name, action, time_str, self.date_str])
        
        return f"{action} marked for {name} at {time_str}"
