import streamlit as st
import os
import pandas as pd
import datetime
import shutil

# --- CONFIGURATION ---
ADMIN_PASSWORD = "mysecretpassword"  # <--- REMEMBER TO CHANGE THIS
SUBMISSIONS_FOLDER = "submissions"
DB_FILE = "client_requests.csv"

st.set_page_config(page_title="Exolio Verification", layout="centered")

# --- CUSTOM CSS ---
st.markdown("""
<style>
    .main-header {font-size: 30px; font-weight: 800; text-align: center; margin-bottom: 20px; color: #111;}
    .sub-text {font-size: 16px; text-align: center; color: #555; margin-bottom: 30px;}
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

def create_zip(folder_path):
    shutil.make_archive(folder_path, 'zip', folder_path)
    return f"{folder_path}.zip"

# --- SIDEBAR ---
st.sidebar.title("Exolio Portal")
page = st.sidebar.radio("Menu", ["Verification Request", "Admin Login"])
st.sidebar.markdown("---")
st.sidebar.caption("System Status: Online")

# ==========================================
# PAGE 1: STUDENT SUBMISSION + DONATION
# ==========================================
if page == "Verification Request":
    st.markdown("<div class='main-header'>AI Verification Service</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub-text'>Upload your document. Our human expert team will manually verify it for AI patterns and email you a signed certificate of integrity.</div>", unsafe_allow_html=True)
    
    # --- FORM ---
    with st.form("submission_form"):
        col1, col2 = st.columns(2)
        with col1:
            email = st.text_input("Your Email", placeholder="student@uni.edu")
        with col2:
            notes = st.text_input("Special Notes", placeholder="e.g. Check Page 4")
            
        uploaded_files = st.file_uploader("Upload Documents (PDF/Docx)", accept_multiple_files=True)
        
        st.caption("🔒 All submissions are secure and confidential.")
        submitted = st.form_submit_button("Submit for Verification", type="primary")

    if submitted:
        if not email or "@" not in email:
            st.error("Please enter a valid email address.")
        elif not uploaded_files:
            st.error("Please upload at least one file.")
        else:
            with st.spinner("Encrypting and Queuing..."):
                save_submission(uploaded_files, email, notes)
                st.markdown("""
                <div class='success-box'>
                    ✅ <strong>Documents Received</strong><br>
                    You have successfully queued your files.<br>
                    Your integrity report will be sent to your email shortly.
                </div>
                """, unsafe_allow_html=True)

    # --- DONATION SECTION ---
    st.markdown("<div class='donate-header'>Please donate £5 to keep my new company Exolio AI going</div>", unsafe_allow_html=True)
    
    # Name Section (Directly on background, no box)
    st.markdown("<span class='label-black'>Account Holder</span>", unsafe_allow_html=True)
    st.code("Francisco George Booth", language=None)

    st.markdown("") # Tiny Spacer

    # Bank Numbers
    d_col1, d_col2 = st.columns(2)
    with d_col1:
        st.markdown("<span class='label-black'>🇬🇧 UK Sort Code</span>", unsafe_allow_html=True)
        st.code("23-14-70", language=None)
        
        st.markdown("<span class='label-black'>Account Number</span>", unsafe_allow_html=True)
        st.code("83139789", language=None)
    
    with d_col2:
        st.markdown("<span class='label-black'>🌍 International (IBAN)</span>", unsafe_allow_html=True)
        st.code("GB80 TRWI 2314 7083 1397 89", language=None)
        
        st.markdown("<span class='label-black'>BIC / SWIFT</span>", unsafe_allow_html=True)
        st.code("TRWIGB2LXXX", language=None)


# ==========================================
# PAGE 2: ADMIN PANEL
# ==========================================
elif page == "Admin Login":
    st.header("Admin Access")
    password = st.text_input("Password", type="password")
    
    if password == ADMIN_PASSWORD:
        st.success("Access Granted")
        
        if os.path.exists(DB_FILE):
            df = pd.read_csv(DB_FILE)
            if not df.empty:
                df = df.iloc[::-1] # Newest first
                
                st.dataframe(df[["Timestamp", "Email", "Notes", "File Count"]], use_container_width=True)
                
                st.markdown("### Download Submission")
                options = df.apply(lambda x: f"{x['Timestamp']} | {x['Email']}", axis=1).tolist()
                selected = st.selectbox("Choose student:", options)
                
                if selected:
                    row = df[df.apply(lambda x: f"{x['Timestamp']} | {x['Email']}", axis=1) == selected].iloc[0]
                    folder_name = row['Folder_Path']
                    full_path = os.path.join(SUBMISSIONS_FOLDER, folder_name)
                    
                    if os.path.exists(full_path):
                        zip_path = create_zip(full_path)
                        with open(zip_path, "rb") as fp:
                            st.download_button(
                                label=f"⬇️ Download {folder_name} (ZIP)",
                                data=fp,
                                file_name=f"{folder_name}.zip",
                                mime="application/zip",
                                type="primary"
                            )
                    else:
                        st.warning("⚠️ Files missing (The Cloud server may have reset).")
            else:
                st.info("No submissions yet.")
        else:
            st.info("No requests yet.")
    elif password:
        st.error("Access Denied")
