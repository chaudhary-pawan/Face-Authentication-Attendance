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

    def register_face(self, image, name):
        """
        Registers a new face by saving the image to the data directory.
        DeepFace will automatically pick it up next time or we can force it.
        """
        # Check if face is present using extract_faces (fast check)
        try:
            # We enforce detection here to ensure a face exists
            DeepFace.extract_faces(img_path=image, enforce_detection=True)
        except:
             return False, "No face detected or poor quality."
        
        # Save image
        filename = f"{name}.jpg"
        filepath = os.path.join(self.db_path, filename)
        
        # Handle duplicates
        if os.path.exists(filepath):
            # Allow overwrite or append timestamp
            return False, f"User {name} already exists."

        cv2.imwrite(filepath, image)
        
        # Remove representation pickle if deepface created one, to force refresh
        pkl_path = os.path.join(self.db_path, "representations_vgg_face.pkl")
        if os.path.exists(pkl_path):
            os.remove(pkl_path)
            
        return True, f"User {name} registered."

    def identify_face(self, image):
        """
        Identifies a face.
        Returns: name (or "Unknown"), confidence (distance)
        """
        # DeepFace.find is powerful but can be slow for every frame.
        # We'll try to just compare against the DB.
        
        try:
            # Check if directory is empty
            if not os.listdir(self.db_path):
                return "Unknown", 0.0

            # Run search
            # silent=True to avoid console spam
            dfs = DeepFace.find(img_path=image, db_path=self.db_path, model_name="VGG-Face", enforce_detection=False, silent=True)
            
            if len(dfs) > 0:
                df = dfs[0]
                if not df.empty:
                    # df results: identity, distance, source_x, source_y...
                    # identity is the absolute path
                    full_path = df.iloc[0]["identity"]
                    filename = os.path.basename(full_path)
                    name = os.path.splitext(filename)[0]
                    distance = df.iloc[0]["distance"]
                    return name, distance
            
            return "Unknown", 0.0
            
        except Exception as e:
            # print(f"Error in identify: {e}") 
            return "Unknown", 0.0
