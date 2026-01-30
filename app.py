import streamlit as st
import cv2
import numpy as np
from PIL import Image
from face_auth import FaceManager
from attendance import AttendanceLogger
import os

# Page Config
st.set_page_config(page_title="Face Attendance", page_icon="📸", layout="centered")

# Initialize Backend
if 'face_manager' not in st.session_state:
    st.session_state.face_manager = FaceManager()
if 'logger' not in st.session_state:
    st.session_state.logger = AttendanceLogger()

st.title("📸 AI Face Attendance")

# Tabs
tab1, tab2, tab3 = st.tabs(["🏠 Punch Attendance", "👤 Register", "📊 Logs"])

with tab1:
    st.header("Mark Attendance")
    
    # Camera Input
    img_file_buffer = st.camera_input("Take a photo to punch in/out")
    
    if img_file_buffer is not None:
        # Convert to OpenCV format
        bytes_data = img_file_buffer.getvalue()
        cv2_img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)
        
        # Display buttons
        col1, col2 = st.columns(2)
        with col1:
            if st.button("PUNCH IN", type="primary", use_container_width=True):
                with st.spinner("Identifying..."):
                    name, dist = st.session_state.face_manager.identify_face(cv2_img)
                    if name != "Unknown":
                        msg = st.session_state.logger.mark_attendance(name, "Punch In")
                        st.success(f"Welcome {name}! ({msg})")
                        st.balloons()
                    else:
                        st.error("Face not recognized. Please Register first.")
                        
        with col2:
            if st.button("PUNCH OUT", type="secondary", use_container_width=True):
                with st.spinner("Identifying..."):
                    name, dist = st.session_state.face_manager.identify_face(cv2_img)
                    if name != "Unknown":
                        msg = st.session_state.logger.mark_attendance(name, "Punch Out")
                        st.info(f"Goodbye {name}! ({msg})")
                    else:
                        st.error("Face not recognized.")

with tab2:
    st.header("New User Registration")
    new_name = st.text_input("Enter Name")
    
    reg_img_buffer = st.camera_input("Take a registration photo", key="reg_cam")
    
    if st.button("Register Face"):
        if not new_name:
            st.warning("Please enter a name.")
        elif reg_img_buffer is None:
            st.warning("Please take a photo.")
        else:
            # Convert
            bytes_data = reg_img_buffer.getvalue()
            cv2_img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)
            
            # Check Duplicate
            existing_name = st.session_state.face_manager.check_existing_face(cv2_img)
            old_name_to_del = None
            
            proceed = True
            if existing_name:
                st.info(f"Note: This face matched '{existing_name}'. Updating identity to '{new_name}'.")
                old_name_to_del = existing_name
            
            if proceed:
                success, msg = st.session_state.face_manager.register_face(cv2_img, new_name, old_name=old_name_to_del)
                if success:
                    st.success(f"Registered {new_name} successfully!")
                    st.session_state.logger.mark_attendance(new_name, "Registration")
                else:
                    st.error(msg)

with tab3:
    st.header("Attendance Logs")
    if st.button("Refresh Logs"):
        logs = st.session_state.logger.get_todays_logs()
        st.dataframe(logs, column_config={0: "Name", 1: "Action", 2: "Time"}, use_container_width=True)
