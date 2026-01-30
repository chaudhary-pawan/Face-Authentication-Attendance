import cv2
import face_recognition
import numpy as np
from face_auth import FaceManager
from attendance import AttendanceLogger
from liveness import LivenessDetector

def main():
    # Initialize components
    face_manager = FaceManager()
    logger = AttendanceLogger()
    liveness_detector = LivenessDetector()

    # Open Webcam
    video_capture = cv2.VideoCapture(0)
    
    if not video_capture.isOpened():
        print("Error: Could not open video source.")
        return

    print("Starting System...")
    print("Controls:")
    print("  'r' - Register a new face (Console input required)")
    print("  'i' - Punch IN")
    print("  'o' - Punch OUT")
    print("  'q' - Quit")
    
    # State variables
    message = "System Ready"
    message_color = (0, 255, 0)
    message_timer = 0
    
    while True:
        ret, frame = video_capture.read()
        if not ret:
            break

        # Small frame for faster processing
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

        # Detect faces for recognition
        face_locations = face_recognition.face_locations(rgb_small_frame, model="hog")
        
        # We need landmarks for liveness. 
        # face_recognition.face_landmarks uses the full image or the face location.
        # It's better to use the original frame or scaled up locations for better precision if needed, 
        # but for speed we might use the small one or just the face ROI.
        # face_landmarks expects the image and the face locations (list of tuples).
        
        # Scaling locations back up for drawing/full resolution processing
        scaled_locations = []
        for (top, right, bottom, left) in face_locations:
            top *= 4
            right *= 4
            bottom *= 4
            left *= 4
            scaled_locations.append((top, right, bottom, left))

        # Get landmarks for liveness on the ORIGINAL frame using the scaled up locations
        # Note: face_landmarks takes a list of face locations.
        face_landmarks_list = face_recognition.face_landmarks(frame, scaled_locations)
        
        current_name = "Unknown"
        liveness_status = "Checks: 0"
        is_live = False

        # If faces found
        if scaled_locations:
             # Just process the first face for this assignment to keep it simple
            top, right, bottom, left = scaled_locations[0]
            
            # Identify
            # cropping the face from the small frame for encoding is faster?
            # Actually we already have the full small frame.
            # face_auth.identify_face takes an image. We can pass the full frame but that re-detects.
            # Let's optimize: use the direct encoding from here if possible, 
            # Or just call identify_face which re-runs detection. 
            # To be efficient, we should expose 'encode_face' in manage, but `identify_face` is cleaner for separation.
            # For real-time, let's just use identify_face on the CROPPED face or the whole frame?
            # identify_face re-runs detection. That's slow.
            # Let's do encoding here since we already have locations.
            
            encodings = face_recognition.face_encodings(rgb_small_frame, [face_locations[0]])
            if encodings:
                encoding = encodings[0]
                # Compare
                name = "Unknown"
                if face_manager.known_face_encodings:
                    matches = face_recognition.compare_faces(face_manager.known_face_encodings, encoding)
                    dists = face_recognition.face_distance(face_manager.known_face_encodings, encoding)
                    best_idx = np.argmin(dists)
                    if matches[best_idx]:
                        name = face_manager.known_face_names[best_idx]
                current_name = name

            # Liveness
            if face_landmarks_list:
                ear, blinked, total_blinks = liveness_detector.check_liveness(face_landmarks_list[0])
                liveness_status = f"Blinks: {total_blinks} (EAR: {ear:.2f})"
                if total_blinks > 0:
                    is_live = True

            # Draw Box
            color = (0, 0, 255) # Red for unknown
            if current_name != "Unknown":
                color = (0, 255, 0) # Green for known
            
            cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
            cv2.rectangle(frame, (left, bottom - 35), (right, bottom), color, cv2.FILLED)
            cv2.putText(frame, f"{current_name}", (left + 6, bottom - 6), cv2.FONT_HERSHEY_DUPLEX, 0.8, (255, 255, 255), 1)

            # Draw Liveness info
            liveness_color = (0, 255, 0) if is_live else (0, 0, 255)
            cv2.putText(frame, liveness_status, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, liveness_color, 1)


        # Interface Overlay
        cv2.putText(frame, "Face Auth System", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(frame, message, (10, 470), cv2.FONT_HERSHEY_SIMPLEX, 0.7, message_color, 2)
        
        # Decrement message timer
        if message_timer > 0:
            message_timer -= 1
        else:
            message = "Ready"
            message_color = (255, 255, 255)

        cv2.imshow('Attendance System', frame)

        # Key Handling
        key = cv2.waitKey(1) & 0xFF
        
        if key == ord('q'):
            break
        
        elif key == ord('r'):
            # Register Face
            # Pause video?
            current_frame_copy = frame.copy()
            # We need to ask for name.
            # CV2 doesn't have a good input box.
            # We will use console input.
            print("\n--- REGISTRATION ---")
            new_name = input("Enter name for the face (or press Enter to cancel): ").strip()
            if new_name:
                success, msg = face_manager.register_face(current_frame_copy, new_name)
                message = msg
                message_color = (0, 255, 0) if success else (0, 0, 255)
                message_timer = 50
                print(f"Result: {msg}")
            print("--- RESUMING ---\n")

        elif key == ord('i'):
            # Punch In
            if current_name != "Unknown":
                if is_live:
                    msg = logger.mark_attendance(current_name, "Punch In")
                    message = msg
                    message_color = (0, 255, 0)
                else:
                    message = "Liveness Check Failed! Blink to verify."
                    message_color = (0, 0, 255)
            else:
                message = "Unknown Face!"
                message_color = (0, 0, 255)
            message_timer = 50

        elif key == ord('o'):
            # Punch Out
            if current_name != "Unknown":
                if is_live:
                    msg = logger.mark_attendance(current_name, "Punch Out")
                    message = msg
                    message_color = (0, 255, 0)
                else:
                    message = "Liveness Check Failed! Blink to verify."
                    message_color = (0, 0, 255)
            else:
                message = "Unknown Face!"
                message_color = (0, 0, 255)
            message_timer = 50

    video_capture.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
