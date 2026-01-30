# Face Authentication Attendance System

A Python-based Face Authentication System for tracking attendance, featuring real-time face recognition and liveness detection.

## Features
- **Face Registration**: Capture and save user face encodings.
- **Face Identification**: Real-time recognition of registered users.
- **Liveness Detection**: Blink detection to prevent basic photo spoofing.
- **Attendance Logging**: Punch-in/Punch-out with timestamps saved to CSV.

## Requirements
- Python 3.8+
- Webcam

## Installation

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
   *Note: `face_recognition` depends on `dlib`. If installation fails on Windows, you may need to install `cmake` and Visual Studio C++ compilers or use a pre-built wheel for `dlib`.*

## Usage

1. Run the application:
   ```bash
   python main.py
   ```

2. **Controls**:
   - `r`: **Register** a new face. (Look at the camera, press 'r', then enter name in the terminal).
   - `i`: **Punch In**. (Marks attendance if face is recognized and "live").
   - `o`: **Punch Out**.
   - `q`: **Quit**.

## System Details

### Model & Approach
- **Face Detection**: Uses HOG (Histogram of Oriented Gradients) via `dlib` (wrapped in `face_recognition`). 
- **Face Encoding**: A ResNet-34 based deep metric learning model that outputs a 128-d vector (embedding) for each face.
- **Matching**: Calculates Euclidean distance between embeddings. If distance < 0.6 (default threshold), a match is declared.
- **Liveness**: Uses Eye Aspect Ratio (EAR) based on facial landmarks (68-point model). A user must blink (EAR drops below threshold) to verify they are "live".

### Training Process
- The system uses a **pre-trained** model (trained on ~3 million faces from standard datasets like Labeled Faces in the Wild). No custom training is required for basic usage. 
- "Registration" simply means saving the 128-d embedding of a new user to `data/encodings.pkl`.

### Accuracy Expectations
- **LFW Benchmark**: The underlying model has ~99.38% accuracy on the LFW benchmark.
- **Real-world**: Highly accurate for frontal faces. Accuracy decreases with extreme angles, occlusions (masks/glasses), or poor lighting.

### Known Failure Cases
- **Lighting**: Strong backlighting or very low light can fail detection.
- **Angles**: Side profiles (>45 degrees) may not be detected.
- **Spoofing**: High-quality video replays might bypass the blink detector (replay attack). Advanced liveness (depth sensors, texture analysis) would be needed for higher security.
