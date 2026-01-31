import cv2
import numpy as np

class LivenessDetector:
    def __init__(self, ear_threshold=None, consecutive_frames=3):
        # Thresholds irrelevant for Haar, we count frames where eyes are NOT detected
        self.consecutive_frames = consecutive_frames
        self.blink_counter = 0
        self.total_blinks = 0
        self.eyes_closed = False
        
        # Load Haar Cascades
        try:
            self.eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
        except AttributeError:
             print("Error loading Haar Cascades.")
             self.eye_cascade = None

    def check_liveness(self, frame, face_roi_coords=None):
        """
        Checks for blinks using Haar Cascade Eye detection.
        If eyes are NOT detected in the face region, we assume closed (blink).
        frame: The full video frame.
        face_roi_coords: (x, y, w, h) of the face. If None, it tries to find one or skips.
        """
        if self.eye_cascade is None:
            return 0.0, False, 0
            
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # If no ROI provided, we can't reliably check eyes (might find random eyes in bg)
        if face_roi_coords is None:
            return 0.0, False, self.total_blinks
            
        (x, y, w, h) = face_roi_coords
        roi_gray = gray[y:y+h, x:x+w]
        
        # Detect eyes
        # scaleFactor=1.1, minNeighbors=5-10 implies reliable detection
        eyes = self.eye_cascade.detectMultiScale(roi_gray, scaleFactor=1.1, minNeighbors=10, minSize=(20, 20))
        
        is_blinking = False
        num_eyes = len(eyes)
        
        # Logic: Normal = 2 eyes. Blink = 0 eyes.
        # We need to be careful of "Missed detection" vs "Blink".
        # We assume if face is stable and eyes disappear, it's a blink.
        
        if num_eyes < 1: # Eyes closed
            self.blink_counter += 1
            self.eyes_closed = True
        else:
            # Eyes open
            if self.eyes_closed and self.blink_counter >= 1: # Was closed for at least 1 frame
                self.total_blinks += 1
                is_blinking = True
            
            self.blink_counter = 0
            self.eyes_closed = False

        # Return "EAR" as 0.0 or 1.0 just for UI
        fake_ear = 0.3 if num_eyes >= 1 else 0.0
        
        return fake_ear, is_blinking, self.total_blinks

    def get_eye_status(self, frame, face_roi_coords):
        """
        Stateless check for eye openness. Used for Web App snapshots.
        Returns: 'Open' or 'Closed'
        """
        if self.eye_cascade is None or face_roi_coords is None:
             return "Unknown"
             
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        (x, y, w, h) = face_roi_coords
        roi_gray = gray[y:y+h, x:x+w]
        
        eyes = self.eye_cascade.detectMultiScale(roi_gray, scaleFactor=1.1, minNeighbors=10, minSize=(20, 20))
        
        if len(eyes) >= 2:
            return "Open" # Both eyes must be visible (Stricter)
        else:
            return "Closed" # 0 or 1 eye not enough (Could be blink or quirk)
