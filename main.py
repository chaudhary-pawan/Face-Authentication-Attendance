import customtkinter as ctk
from PIL import Image, ImageTk
import cv2
import threading
import tkinter as tk
# from tkinter import messagebox # Deprecated
from CTkMessagebox import CTkMessagebox # Modern MessageBox
from face_auth import FaceManager
from attendance import AttendanceLogger
from liveness import LivenessDetector
    # import mediapipe as mp # Removed due to incompatibility
    
# Theme Settings
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class AttendanceApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("Face Auth Attendance System")
        self.geometry("1100x700")
        
        # Logic Modules
        self.face_manager = FaceManager()
        self.logger = AttendanceLogger()
        self.liveness_detector = LivenessDetector()
        
        # --- SWITCH: Use OpenCV Haar Cascade ---
        # self.mp_face_detection = mp.solutions.face_detection # Removed
        # self.face_detection = self.mp_face_detection.FaceDetection(...) # Removed
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        
        # State
        self.video_capture = None
        self.is_running = True
        self.current_frame = None
        self.detected_name = "Unknown"
        self.liveness_status = "Waiting..."
        
        self._setup_ui()
        self._start_camera()
        
        # Start Background Identification Thread
        threading.Thread(target=self._auto_identify_loop, daemon=True).start()
        
    def _auto_identify_loop(self):
        """Runs heavy AI identification in background to keep UI smooth."""
        import time
        while self.is_running:
            # We need a copy of the frame safely
            if self.current_frame is not None:
                # Reuse MediaPipe result if possible, or just re-run identification on the whole frame
                # DeepFace has its own detection, but we can pass the cropped face if we want.
                # For simplicity in this thread, let DeepFace handle it but use a faster backend like ssd if possible,
                # OR just rely on the main thread's detection signal.
                
                # To avoid lag, we only Identify. Detection is done in UI thread for visuals.
                
                # Double check presence (Fast check)
                small_frame = cv2.resize(self.current_frame, (0,0), fx=0.25, fy=0.25)
                # rgb_small = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB) # Not needed for Haar
                gray_small = cv2.cvtColor(small_frame, cv2.COLOR_BGR2GRAY)
                
                # results = self.face_detection.process(rgb_small) # Removed
                faces = self.face_cascade.detectMultiScale(gray_small, 1.1, 4)
                
                if len(faces) > 0:
                    # Face Present -> Identify
                    name, dist = self.face_manager.identify_face(self.current_frame)
                    self.detected_name = name
                    
                    # Update UI from main thread
                    if name != "Unknown":
                        self.lbl_name.configure(text=f"Name: {name}", text_color="green")
                    else:
                        self.lbl_name.configure(text=f"Name: Unknown", text_color="white")
                else:
                    self.detected_name = "Unknown"
            
            # Check every 0.5 seconds
            time.sleep(0.5)

    def _setup_ui(self):
        # Grid Layout
        self.grid_columnconfigure(0, weight=1) # Left: Camera
        self.grid_columnconfigure(1, weight=0) # Right: Controls
        self.grid_rowconfigure(0, weight=1)
        
        # --- Left Frame (Camera) ---
        self.camera_frame = ctk.CTkFrame(self)
        self.camera_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        
        self.video_label = ctk.CTkLabel(self.camera_frame, text="Loading Camera...", text_color="gray")
        self.video_label.pack(expand=True, fill="both")
        
        # --- Right Frame (Controls) - SCROLLABLE ---
        self.controls_frame = ctk.CTkScrollableFrame(self, width=300, label_text="Control Panel")
        self.controls_frame.grid(row=0, column=1, padx=(0, 20), pady=20, sticky="nsew")
        
        # Header (Logo moved to label_text or inside)
        # self.logo_label = ctk.CTkLabel(self.controls_frame, text="Attendance System", font=("Arial", 24, "bold"))
        # self.logo_label.pack(pady=30)
        
        # Status Box
        self.status_frame = ctk.CTkFrame(self.controls_frame, fg_color="#333333")
        self.status_frame.pack(pady=10, padx=20, fill="x")
        
        self.lbl_name = ctk.CTkLabel(self.status_frame, text="Name: Unknown", font=("Arial", 16))
        self.lbl_name.pack(pady=5)
        
        self.lbl_liveness = ctk.CTkLabel(self.status_frame, text="Liveness: Waiting", font=("Arial", 14), text_color="orange")
        self.lbl_liveness.pack(pady=5)
        
        # Actions
        self.btn_punch_in = ctk.CTkButton(self.controls_frame, text="PUNCH IN", height=50, fg_color="green", hover_color="darkgreen", command=self.action_punch_in)
        self.btn_punch_in.pack(pady=10, padx=20, fill="x")
        
        self.btn_punch_out = ctk.CTkButton(self.controls_frame, text="PUNCH OUT", height=50, fg_color="red", hover_color="darkred", command=self.action_punch_out)
        self.btn_punch_out.pack(pady=10, padx=20, fill="x")
        
        # Registration Section
        ctk.CTkLabel(self.controls_frame, text="New User Registration").pack(pady=(20, 5))
        self.entry_name = ctk.CTkEntry(self.controls_frame, placeholder_text="Enter Name")
        self.entry_name.pack(padx=20, fill="x")
        
        self.btn_register = ctk.CTkButton(self.controls_frame, text="Register Face", command=self.action_register)
        self.btn_register.pack(pady=10, padx=20, fill="x")
        
        # Log View
        self.log_textbox = ctk.CTkTextbox(self.controls_frame, height=120)
        self.log_textbox.pack(pady=20, padx=20, fill="x")
        self.log_textbox.insert("0.0", "System Ready...\n")

        # Quit Button
        self.btn_quit = ctk.CTkButton(self.controls_frame, text="QUIT APP", height=40, fg_color="darkred", hover_color="red", command=self.on_closing)
        self.btn_quit.pack(pady=(10, 30), padx=20, fill="x")

    def _start_camera(self):
        self.video_capture = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        self._update_camera()

    def _update_camera(self):
        if not self.is_running:
            return

        ret, frame = self.video_capture.read()
        if ret:
            frame = cv2.flip(frame, 1) # Mirror effect
            self.current_frame = frame.copy()
            
            # --- OpenCV Haar Detection ---
            # rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) # Not needed for Haar
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # results = self.face_detection.process(rgb_frame) # Removed
            faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
            
            face_coords = None
            
            if len(faces) > 0:
                # Get the largest face (closest)
                # faces returns (x, y, w, h)
                faces = sorted(faces, key=lambda f: f[2]*f[3], reverse=True)
                (x, y, w, h) = faces[0]
                
                face_coords = (x, y, w, h)
                
                # Draw
                color = (0, 255, 0) if self.detected_name != "Unknown" else (0, 0, 255)
                cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
                
                # Check Liveness (using new coords)
                fake_ear, is_blinking, total_blinks = self.liveness_detector.check_liveness(frame, face_coords)
                self.lbl_liveness.configure(text=f"Blinks: {total_blinks}", text_color="green" if total_blinks > 0 else "orange")
            else:
                 self.lbl_liveness.configure(text="No Face", text_color="red")
                 self.detected_name = "Unknown"

            # Convert to ImageTk
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) # Needed for Display
            img = Image.fromarray(rgb_frame)
            
            ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(800, 600))
            self.video_label.configure(image=ctk_img, text="")
        
        # Schedule next update in 10ms (100 FPS cap)
        self.after(10, self._update_camera)

    def action_register(self):
        name = self.entry_name.get().strip()
        if not name:
             CTkMessagebox(title="Input Error", message="Please enter a name first.", icon="warning")
             return
             
        if self.current_frame is None:
             CTkMessagebox(title="Camera Error", message="No camera availability.", icon="cancel")
             return
        
        # Need coordinates for registration to be accurate?
        # FaceManager extracts internally via DeepFace, so raw frame is fine.

        # Smart Duplicate Check
        existing_name = self.face_manager.check_existing_face(self.current_frame)
        registration_type = "Registration (New)"
        old_name_to_delete = None
        
        if existing_name:
            # Found a match!
            if existing_name.lower() == name.lower():
                 # Same name
                 registration_type = "Registration (Update Photo)"
                 msg = CTkMessagebox(title="Update Photo", message=f"User '{existing_name}' already exists.\nUpdate their photo?", icon="question", option_1="Yes", option_2="No")
            else:
                 # Duplicate Face
                 registration_type = f"Registration (Overwrite {existing_name})"
                 old_name_to_delete = existing_name # Mark for deletion
                 msg = CTkMessagebox(title="Duplicate Face", message=f"This face currently belongs to '{existing_name}'.\nAre you sure you want to register as '{name}'?\nThis will overwrite the name.", icon="question", option_1="Yes", option_2="No")
            
            if msg.get() != "Yes":
                return

        # Proceed
        success, msg = self.face_manager.register_face(self.current_frame, name, old_name=old_name_to_delete)
        if success:
             # SUCCESS ICON (Checkmark) 
             CTkMessagebox(title="Success", message=msg, icon="check")
             
             # LOGGING THE REGISTRATION
             log_msg = self.logger.mark_attendance(name, registration_type)
             
             self.log_textbox.insert("0.0", f"{log_msg}\n")
        else:
             CTkMessagebox(title="Error", message=msg, icon="cancel")

    def action_punch_in(self):
        self._handle_attendance("Punch In")

    def action_punch_out(self):
        self._handle_attendance("Punch Out")

    def _handle_attendance(self, action):
        if self.current_frame is None: return
        
        # Check Liveness First
        if self.liveness_detector.total_blinks == 0:
             CTkMessagebox(title="Security Alert", message="Please blink your eyes to prove you are human!", icon="warning", option_1="OK")
             return
        
        # Identify
        self.log_textbox.insert("0.0", "Identifying...\n")
        
        # Run identification in main thread (might freeze slightly, better in thread ideally)
        name, dist = self.face_manager.identify_face(self.current_frame)
        
        if name != "Unknown":
            res = self.logger.mark_attendance(name, action)
            self.lbl_name.configure(text=f"Name: {name}")
            self.log_textbox.insert("0.0", f"{res}\n")
            # SUCCESS ICON (Checkmark)
            CTkMessagebox(title=f"Welcome {name}", message=f"{action} Successful", icon="check", option_1="OK")
        else:
            CTkMessagebox(title="Access Denied", message="Face not recognized. Please Register.", icon="cancel")

    def on_closing(self):
        self.is_running = False
        self.destroy()

if __name__ == "__main__":
    app = AttendanceApp()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()
