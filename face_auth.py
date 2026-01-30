from deepface import DeepFace
import cv2
import os
import numpy as np
import pickle

class FaceManager:
    def __init__(self, db_path="data"):
        self.db_path = db_path
        if not os.path.exists(self.db_path):
            os.makedirs(self.db_path)
            
        print(f"[INFO] Face DB at {self.db_path}")
        
        # Pre-load the model to ensure weights are downloaded BEFORE the UI starts
        # This prevents the "Not Responding" freeze on first Punch In
        print("[INFO] Loading AI Model (VGG-Face)... Please wait...")
        try:
            DeepFace.build_model("VGG-Face")
            print("[INFO] Model Loaded Successfully.")
        except Exception as e:
            print(f"[WARNING] Model load deferred: {e}")

    def check_existing_face(self, image):
        """
        Checks if the face in 'image' already exists in the DB under any name.
        Returns: (Name, Distance) if found, else None
        """
        try:
            if not os.listdir(self.db_path):
                return None

            # Search for the face
            dfs = DeepFace.find(img_path=image, db_path=self.db_path, model_name="VGG-Face", enforce_detection=True, silent=True, threshold=0.40)
            
            if len(dfs) > 0:
                df = dfs[0]
                if not df.empty:
                    # Found a match
                    full_path = df.iloc[0]["identity"]
                    filename = os.path.basename(full_path)
                    existing_name = os.path.splitext(filename)[0]
                    # Clean up name (remove numbers if we handle multiple pics per user later)
                    return existing_name
            return None
        except Exception as e:
            return None

    def register_face(self, image, name):
        """
        Registers a new face.
        """
        try:
            DeepFace.extract_faces(img_path=image, enforce_detection=True)
        except:
             return False, "No face detected."
        
        # Save image
        filename = f"{name}.jpg"
        filepath = os.path.join(self.db_path, filename)
        
        # If the file for THIS name exists, we are simply updating that user's photo.
        cv2.imwrite(filepath, image)
        
        # Remove pickl to force refresh
        pkl_path = os.path.join(self.db_path, "representations_vgg_face.pkl")
        if os.path.exists(pkl_path):
            os.remove(pkl_path)
            
        return True, f"User {name} registered."

    def identify_face(self, image):
        """
        Identifies a face.
        """
        try:
            if not os.listdir(self.db_path):
                return "Unknown", 0.0

            dfs = DeepFace.find(img_path=image, db_path=self.db_path, model_name="VGG-Face", enforce_detection=False, silent=True)
            
            if len(dfs) > 0:
                df = dfs[0]
                if not df.empty:
                    full_path = df.iloc[0]["identity"]
                    filename = os.path.basename(full_path)
                    name = os.path.splitext(filename)[0]
                    distance = df.iloc[0]["distance"]
                    return name, distance
            
            return "Unknown", 0.0
        except:
            return "Unknown", 0.0
