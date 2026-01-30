import face_recognition
import cv2
import os
import numpy as np
import pickle

class FaceManager:
    def __init__(self, storage_path="data/encodings.pkl"):
        self.storage_path = storage_path
        self.known_face_encodings = []
        self.known_face_names = []
        self.load_encodings()

    def load_encodings(self):
        """Loads face encodings from disk if available."""
        if os.path.exists(self.storage_path):
            with open(self.storage_path, "rb") as f:
                data = pickle.load(f)
                self.known_face_encodings = data["encodings"]
                self.known_face_names = data["names"]
            print(f"[INFO] Loaded {len(self.known_face_names)} encodings.")
        else:
            print("[INFO] No existing encodings found. Starting fresh.")

    def save_encodings(self):
        """Saves current encodings to disk."""
        data = {"encodings": self.known_face_encodings, "names": self.known_face_names}
        with open(self.storage_path, "wb") as f:
            pickle.dump(data, f)
        print("[INFO] Encodings saved.")

    def register_face(self, image, name):
        """
        Registers a new face.
        Returns (True, message) if successful, (False, message) otherwise.
        """
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        boxes = face_recognition.face_locations(rgb_image, model="hog")
        
        if len(boxes) == 0:
            return False, "No face detected."
        if len(boxes) > 1:
            return False, "Multiple faces detected. Please ensure only one person is in frame."

        encodings = face_recognition.face_encodings(rgb_image, boxes)
        if not encodings:
             return False, "Could not encode face."

        # Check if already registered (optional, but good practice)
        # simplistic check: if name exists, update it? Or duplicate names? 
        # For this assignment, assuming unique names or allowing updates.
        
        self.known_face_encodings.append(encodings[0])
        self.known_face_names.append(name)
        self.save_encodings()
        return True, f"User {name} registered successfully."

    def identify_face(self, image):
        """
        Identifies a face in the image.
        Returns: name (or "Unknown"), confidence (distance)
        """
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        boxes = face_recognition.face_locations(rgb_image, model="hog")
        encodings = face_recognition.face_encodings(rgb_image, boxes)

        name = "Unknown"
        min_dist = 1.0 # High value initially
        
        if not encodings:
            return None, None

        # Logic for the primary face (largest face or only face)
        # We'll just take the first one found for now.
        encoding = encodings[0]
        
        if self.known_face_encodings:
            matches = face_recognition.compare_faces(self.known_face_encodings, encoding)
            face_distances = face_recognition.face_distance(self.known_face_encodings, encoding)
            
            best_match_index = np.argmin(face_distances)
            if matches[best_match_index]:
                name = self.known_face_names[best_match_index]
                min_dist = face_distances[best_match_index]
        
        return name, min_dist
