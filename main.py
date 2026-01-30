import cv2
import numpy as np
import threading
from face_auth import FaceManager
from attendance import AttendanceLogger
from liveness import LivenessDetector
from deepface import DeepFace

def main():
    face_manager = FaceManager()
    logger = AttendanceLogger()
    liveness_detector = LivenessDetector()

    # Load face cascade for main detection
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    video_capture = cv2.VideoCapture(0)
    
    print("Starting System (DeepFace + OpenCV Liveness)...")
    print("Controls:")
    print("  'r' - Register (Terminal Input)")
    print("  'i' - Punch IN")
    print("  'o' - Punch OUT")
    print("  'q' - Quit")
    
    message = "System Ready"
    message_color = (0, 255, 0)
    message_timer = 0
    
    while True:
        ret, frame = video_capture.read()
        if not ret:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)
        
        # State vars for this frame
        current_face_roi = None
        face_coords = None
        
        if len(faces) > 0:
            # Take largest face
            faces = sorted(faces, key=lambda f: f[2]*f[3], reverse=True)
            (x, y, w, h) = faces[0]
            face_coords = (x, y, w, h)
            current_face_roi = frame[y:y+h, x:x+w] # For DeepFace
            
            # Draw Box
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
            
            # Liveness Check
            fake_ear, is_blinking, total_blinks = liveness_detector.check_liveness(frame, face_coords)
            
            # Draw Liveness info
            liveness_msg = f"Blinks: {total_blinks}"
            color = (0, 255, 0) if total_blinks > 0 else (0, 0, 255)
            cv2.putText(frame, liveness_msg, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        else:
            total_blinks = 0 # Reset or keep memory? Keep memory usually better but for safety lets keep 0 if no face
            # actually logic handles it inside liveness but we need to display it
            pass

        # UI Overlay
        cv2.putText(frame, message, (10, frame.shape[0] - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, message_color, 2)
        if message_timer > 0:
            message_timer -= 1
        else:
            message = "Ready"
            message_color = (255, 255, 255)

        cv2.imshow('Face Auth System', frame)

        key = cv2.waitKey(1) & 0xFF
        
        if key == ord('q'):
            break
        
        elif key == ord('r'):
            if current_face_roi is not None:
                print("\n--- REGISTER ---")
                name = input("Enter Name: ").strip()
                if name:
                    # Pass the full frame but cropped is better? 
                    # DeepFace enforce_detection=True might fail on crop if too small? 
                    # Let's pass the full frame but we assume 1 face.
                    # Actually face_manager.register_face expects path or numpy array
                    success, msg = face_manager.register_face(frame, name)
                    message = msg
                    message_color = (0, 255, 0) if success else (0, 0, 255)
                    message_timer = 100
                print("--- RESUMED ---\n")
            else:
                 message = "No face detected for registration."
                 message_color = (0, 0, 255)
                 message_timer = 50
            
        elif key in [ord('i'), ord('o')]:
            action = "Punch In" if key == ord('i') else "Punch Out"
            
            if liveness_detector.total_blinks == 0:
                message = "Blink to verify liveness first!"
                message_color = (0, 0, 255)
                message_timer = 50
                continue
            
            message = "Identifying..."
            cv2.imshow('Face Auth System', frame)
            cv2.waitKey(1)
            
            if current_face_roi is not None:
                 # We can pass cropped ROI to identify_face to be faster/specific
                 # But identify_face uses DeepFace.find which expects image.
                 name, dist = face_manager.identify_face(frame) # Searching full frame again?
                 # ideally pass ROI but DeepFace.find needs context or disable detector
                 # Let's pass frame.
                 
                 if name != "Unknown":
                    res = logger.mark_attendance(name, action)
                    message = f"Welcome {name}! ({res})"
                    message_color = (0, 255, 0)
                 else:
                    message = "Face not recognized."
                    message_color = (0, 0, 255)
            else:
                 message = "No face to identify."
                 message_color = (0, 0, 255)
            message_timer = 100

    video_capture.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
