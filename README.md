# Face Authentication Attendance System

A robust, Python-based Face Authentication System for tracking attendance. It features real-time face recognition, liveness detection to prevent photo spoofing, and a modern GUI.

## 🚀 Features
- **Two Interface Modes**:
  - **Desktop App**: Modern Dark Mode GUI (via `CustomTkinter`) for high-performance, real-time logging.
  - **Web Dashboard**: Lightweight Web App (via `Streamlit`) for easy access and mobile testing.
- **Face Recognition**: Uses **VGG-Face** (Deep Learning) for high-accuracy identification.
- **Liveness Detection**: Blink detection to ensure the user is present (prevents holding up a photo).
- **Attendance Logging**: Automatically logs "Punch In" and "Punch Out" events with timestamps to CSV.
- **One-Shot Registration**: Instantly register new users without re-training the model.

## 🛠️ Technology Stack
- **Language**: Python 3.12+
- **Computer Vision**: OpenCV (Haar Cascades)
- **AI Model**: VGG-Face (via `deepface`)
- **GUI**: CustomTkinter
- **Web Framework**: Streamlit

## 📦 Installation

1.  **Clone the Repository** and enter the directory.
2.  **Create a Virtual Environment** (Recommended):
    ```bash
    python -m venv venv
    # Windows:
    .\venv\Scripts\activate
    # Mac/Linux:
    source venv/bin/activate
    ```
3.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

## 🖥️ Usage

### Option 1: Desktop Application (Recommended)
This is the main application with real-time video feedback and blink counting.

```bash
python main.py
```

**Controls:**
- **Register Face**: Enter a name in the text box and click "Register Face".
- **Punch In**: Click the Green button. (Requires looking at the camera and blinking).
- **Punch Out**: Click the Red button.
- **Logs**: View recent logs instantly in the text panel.

### Option 2: Web Application
A browser-based version suitable for quick checks or remote access.

```bash
python -m streamlit run app.py
```

## 📄 Documentation
For a detailed technical explanation of the models, algorithms, and failure cases, please refer to the **[Technical Report (PDF)](REPORT.pdf)** included in this repository.

## 📂 Project Structure
- `main.py`: Entry point for the Desktop GUI App.
- `app.py`: Entry point for the Streamlit Web App.
- `face_auth.py`: Core logic for Face Recognition (DeepFace).
- `liveness.py`: Logic for Blink Detection.
- `data/`: Stores registered face embeddings.
- `logs/`: Stores daily CSV attendance logs.
