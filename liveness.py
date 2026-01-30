import numpy as np

def euclidean_dist(ptA, ptB):
    return np.linalg.norm(np.array(ptA) - np.array(ptB))

def eye_aspect_ratio(eye):
    # compute the euclidean distances between the two sets of
    # vertical eye landmarks (x, y)-coordinates
    A = euclidean_dist(eye[1], eye[5])
    B = euclidean_dist(eye[2], eye[4])

    # compute the euclidean distance between the horizontal
    # eye landmark (x, y)-coordinates
    C = euclidean_dist(eye[0], eye[3])

    if C == 0:
        return 0.0

    # compute the eye aspect ratio
    ear = (A + B) / (2.0 * C)

    # return the eye aspect ratio
    return ear

class LivenessDetector:
    def __init__(self, ear_threshold=0.25, consecutive_frames=3):
        self.ear_threshold = ear_threshold
        self.consecutive_frames = consecutive_frames
        self.blink_counter = 0
        self.total_blinks = 0
        self.eye_closed = False

    def check_liveness(self, face_landmarks):
        """
        updates blink status based on face landmarks.
        face_landmarks: dictionary of landmarks from face_recognition library.
        Returns: True if 'live' action (blink) is detected recently (cumulative), 
                 or simply current EAR for UI display.
        """
        
        # dlib/face_recognition landmarks:
        # left_eye: points 36-41 (indices in 0-67 range, but face_recognition returns dict)
        left_eye = face_landmarks['left_eye']
        right_eye = face_landmarks['right_eye']

        ear_left = eye_aspect_ratio(left_eye)
        ear_right = eye_aspect_ratio(right_eye)

        ear = (ear_left + ear_right) / 2.0

        is_blinking = False
        
        if ear < self.ear_threshold:
            self.blink_counter += 1
            self.eye_closed = True
        else:
            if self.eye_closed and self.blink_counter >= self.consecutive_frames:
                self.total_blinks += 1
                is_blinking = True
            
            self.blink_counter = 0
            self.eye_closed = False

        return ear, is_blinking, self.total_blinks
