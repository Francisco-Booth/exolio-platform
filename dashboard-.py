import streamlit as st
import os
import pandas as pd
import datetime
import shutil

# --- CONFIGURATION ---
ADMIN_PASSWORD = "mysecretpassword"  # <--- REMEMBER TO CHANGE THIS
SUBMISSIONS_FOLDER = "submissions"
DB_FILE = "client_requests.csv"
YOUTUBE_LINK = "https://www.youtube.com/watch?v=dQw4w9WgXcQ" # <--- YOUR YOUTUBE LINK
LOGO_FILENAME = "logo.png"

st.set_page_config(page_title="Exolio Verification", layout="centered")

# --- CUSTOM CSS ---
st.markdown("""
<style>
    /* 1. FORCE LOGO HIGHER & LEFT */
    div.block-container {
        padding-top: 0.5rem; /* Moves everything up to the very top */
        padding-left: 1rem;  /* Reduces space on the left */
    }

    /* 2. Style Titles */
    .main-header {
        font-size: 30px; 
        font-weight: 800; 
        text-align: center; 
        margin-bottom: 20px; 
        color: #111;
        margin-top: -20px; /* Pulls title closer to the logo */
    }
    
    .sub-text {font-size: 16px; text-align: center; color: #555; margin-bottom: 20px;}
    .success-box {background-color: #d1fae5; color: #065f46; padding: 20px; border-radius: 5px; text-align: center; margin-top: 10px;}
    
    /* Donation Header Styling */
    .donate-header {
        font-size: 22px; 
        font-weight: bold; 
        text-align: center; 
        margin-top: 50px; 
        margin-bottom: 20px; 
        color: #222;
    }

    /* Custom style for the labels to be BLACK and BOLD */
    .label-black {
        color: black !important;
        font-weight: bold;
        font-size: 14px;
        margin-bottom: 5px;
        display: block;
    }
</style>
""", unsafe_allow_html=True)

# --- BACKEND LOGIC ---
if not os.path.exists(SUBMISSIONS_FOLDER):
    os.makedirs(SUBMISSIONS_FOLDER)

def save_submission(uploaded_files, email, notes):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    clean_email = email.split('@')[0].replace('.', '_')
    folder_name = f"{timestamp}_{clean_email}"
    user_folder = os.path.join(SUBMISSIONS_FOLDER, folder_name)
    os.makedirs(user_folder, exist_ok=True)
    
    saved_paths = []
    for uploaded_file in uploaded_files:
        file_path = os.path.join(user_folder, uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        saved_paths.append(file_path)

    new_data = {
        "Timestamp": timestamp,
        "Email": email,
        "File Count": len(uploaded_files),
        "Notes": notes,
        "Folder_Path": folder_name
    }
    
    # Save metadata to CSV
    if not os.path.exists(DB_FILE):
        df = pd.DataFrame([new_data])
        df.to_csv(DB_FILE, index=False)
    else:
        df = pd.DataFrame([new_data])
        df.to_csv(DB_FILE, mode='a', header=False, index=False)
        
    return user_folder

def create_zip(folder_path)
