import streamlit as st
import os
import pandas as pd
import datetime
import shutil
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# --- CONFIGURATION ---
ADMIN_PASSWORD = "mysecretpassword" # <--- REMEMBER TO CHANGE THIS
SUBMISSIONS_FOLDER = "submissions"
DB_FILE = "client_requests.csv"
YOUTUBE_LINK = "https://www.youtube.com/watch?v=mt_aSLGYNRs" # <--- YOUR YOUTUBE LINK
LOGO_FILENAME = "logo.png"

st.set_page_config(page_title="Exolio Verification", layout="wide")

# --- CUSTOM CSS ---
st.markdown("""
<style>
    div.block-container {
        padding-top: 3rem; 
        padding-bottom: 1rem;
    }
    .main-header {font-size: 30px; font-weight: 800; text-align: center; margin-bottom: 20px; color: #111;}
    .sub-text {font-size: 16px; text-align: center; color: #555; margin-bottom: 20px;}
    .success-box {background-color: #d1fae5; color: #065f46; padding: 20px; border-radius: 5px; text-align: center; margin-top: 10px;}
    
    /* Trusted Explanation Box (Option 1) */
    .trust-box {
        background-color: #f0f8ff; 
        border-left: 5px solid #0078d7;
        padding: 15px;
        border-radius: 5px;
        margin-bottom: 25px;
    }
    .trust-title {
        color: #005a9e;
        font-weight: bold;
        font-size: 18px;
        margin-bottom: 5px;
    }
    
    .donate-header {
        font-size: 22px; 
        font-weight: bold; 
        text-align: center; 
        margin-top: 50px; 
        margin-bottom: 20px; 
        color: #222;
    }

    /* EXPANDER STYLING (The "Deep Dive" Box) */
    /* This targets the clickable header of the expander */
    div[data-testid="stExpander"] details summary {
        background-color: #f8f9fa !important;
        border: 2px solid #e0e0e0 !important;
        border-radius: 10px !important;
        padding: 1.5rem !important; /* Make the box taller/bigger */
    }
    
    /* This targets the text inside the header */
    div[data-testid="stExpander"] details summary p {
        font-size: 1.3rem !important; /* Make text bigger */
        font-weight: 700 !important;   /* Make text bold */
        color: #333 !important;
    }
    
    /* Hover effect for the box */
    div[data-testid="stExpander"] details summary:hover {
        background-color: #eef3f8 !important;
        border-color: #0078d7 !important;
    }
</style>
""", unsafe_allow_html=True)

# --- BACKEND LOGIC ---
if not os.path.exists(SUBMISSIONS_FOLDER):
    os.makedirs(SUBMISSIONS_FOLDER)

# --- EMAIL NOTIFICATION FUNCTION ---
def send_notification_email(student_email, file_count, notes):
    try:
        sender_email = st.secrets["email"]["sender_email"]
        sender_password = st.secrets["email"]["sender_password"]
        receiver_email = st.secrets["email"]["receiver_email"]

        subject = f"🔔 Submission from: {student_email}"
        
        body = f"""
        New Exolio Upload!
        
        STUDENT: {student_email}
        FILES: {file_count}
        NOTES: {notes}
        
        ---------------------------------------
        Simply hit 'Reply' to email this student.
        ---------------------------------------
        
        Download files here: https://share.streamlit.io/
        """

        msg = MIMEMultipart()
        msg['From'] = f"Exolio Bot <{sender_email}>"
        msg['To'] = receiver_email
        msg['Subject'] = subject
        msg['Reply-To'] = student_email 

        msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        text = msg.as_string()
        server.sendmail(sender_email, receiver_email, text)
        server.quit()
        return True
    except Exception as e:
        print(f"Email failed: {e}")
        return False

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
    
    # 1. LOGO
    if os.path.exists(LOGO_FILENAME):
        st.image(LOGO_FILENAME, width=200) 
    
    # 2. COLUMNS
    spacer_left, main_content, spacer_right = st.columns([1, 2, 1])

    with main_content:
        st.markdown("<div class='main-header'>AI Verification Service</div>", unsafe_allow_html=True)
        st.markdown("<div class='sub-text'>Upload your document. Our human expert team will manually verify it for AI patterns and email you a signed certificate of integrity.</div>", unsafe_allow_html=True)
        
        # --- VIDEO ---
        st.video(YOUTUBE_LINK)
        st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)

        # --- OPTION 1: SIMPLE TRUST BOX ---
        st.markdown("""
        <div class='trust-box'>
            <div class='trust-title'>🛡️ How our scores are calculated</div>
            Exolio does not "guess." Our detection engine runs on a custom-trained neural network that has studied over 
            24,000 parallel examples of Human writing vs. AI writing.<br><br>
            Unlike a simple plagiarism checker, we analyze the <strong>mathematical probability</strong> of your sentence structure. 
            AI models are statistically predictable; human writing is complex, messy, and creative ("bursty"). 
            Our system detects these subtle, invisible signatures to verify that your work is authentically yours.
        </div>
        """, unsafe_allow_html=True)

        # --- FORM ---
        with st.form("submission_form"):
            col1, col2 = st.columns(2)
            with col1:
                email = st.text_input("Your Email", placeholder="student@uni.edu")
            with col2:
                notes = st.text_input("Special Notes", placeholder="e.g. Check Page 4")
            
            # Info box regarding processing time
            st.info("""
            **Estimated Processing Times (Based on Total Word Count):**
            *   **Less than 1,000 words:** Max 24 hours to return
            *   **Between 1,000 and 5,000 words:** Max 48 hours to return
            *   **Between 5,000 and 10,000 words:** Max 72 hours to return
            *   **10,000+ words:** Max 1 Week to return
            """)
                
            uploaded_files = st.file_uploader("Upload Documents (PDF/Docx)", accept_multiple_files=True)
            
            st.caption("🔒 All submissions are secure and confidential.")
            submitted = st.form_submit_button("Submit for Verification", type="primary")

        if submitted:
            if not email or "@" not in email:
                st.error("Please enter a valid email address.")
            elif not uploaded_files:
                st.error("Please upload at least one file.")
            else:
                with st.spinner("Encrypting, Queuing & Notifying..."):
                    # 1. Save
                    save_submission(uploaded_files, email, notes)
                    # 2. Notify
                    email_success = send_notification_email(email, len(uploaded_files), notes)
                    
                    st.markdown("""
                    <div class='success-box'>
                        ✅ <strong>Documents Received</strong><br>
                        You have successfully queued your files.<br>
                        Your integrity report will be sent to your email shortly.
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if not email_success:
                        st.warning("(Note: Files saved, but Admin alert failed.)")

        # --- OPTION 2: DEEP DIVE (BIG BOX, NO EMOJI) ---
        # Emoji removed from text below
        with st.expander("Deep Dive: Read the Science & Logic behind Exolio", expanded=False):
            st.markdown("### Is the AI detection score random?")
            st.write("""
            No. Our scores are derived from a deep-learning forensic analysis. Here is exactly what happens when you upload a file:
            
            1.  **Contextual Analysis (The "Brain"):** Your document is scanned by a specific Neural Network (based on Transformer architecture) that we finetuned on thousands of academic and creative texts. It doesn't just read words; it recognizes the distinct "tone" and rigid patterns used by models like ChatGPT and Claude.
            
            2.  **Measuring Perplexity:** AI generators function like sophisticated "autocomplete"—they constantly choose the most mathematically probable next word. This results in "Low Perplexity" (high predictability). Humans often use unexpected word choices ("High Perplexity"). Our engine measures this deviation.
            
            3.  **Measuring Burstiness:** AI writing tends to be monotonous in sentence rhythm. Humans write with "Burstiness"—we mix short sentences with very long, complex ones.
            
            We combine these metrics into a confidence percentage. If Exolio says you are human, it’s because your writing contains the unique, chaotic creativity that algorithms cannot easily replicate.
            """)

        # DONATION
        st.markdown("<div class='donate-header'>Please donate £5 to keep my new company Exolio AI going</div>", unsafe_allow_html=True)
        st.link_button("👉 Click here to Pay securely via Starling Bank", "https://settleup.starlingbank.com/francisco-booth-88544a", type="primary", use_container_width=True)


# ==========================================
# PAGE 2: ADMIN PANEL
# ==========================================
elif page == "Admin Login":
    spacer_left, admin_content, spacer_right = st.columns([1, 2, 1])
    
    with admin_content:
        st.header("Admin Access")
        password = st.text_input("Password", type="password")
        
        if password == ADMIN_PASSWORD:
            st.success("Access Granted")
            
            if os.path.exists(DB_FILE):
                df = pd.read_csv(DB_FILE)
                if not df.empty:
                    df = df.iloc[::-1]
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
                            st.warning("⚠️ Files missing.")
                else:
                    st.info("No submissions yet.")
            else:
                st.info("No requests yet.")
        elif password:
            st.error("Access Denied")
