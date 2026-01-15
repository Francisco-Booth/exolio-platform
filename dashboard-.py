import streamlit as st
import pandas as pd
import random
import time
import PyPDF2
import docx

# --- CONFIGURATION & STYLING ---
st.set_page_config(page_title="Academic Integrity Evidence Report", layout="centered")

st.markdown("""
<style>
    .report-container {
        background-color: white;
        padding: 30px;
        border-radius: 5px;
        border-top: 10px solid #000;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.1);
        font-family: 'Helvetica', 'Arial', sans-serif;
    }
    .header {
        font-size: 24px; font-weight: bold; text-transform: uppercase; 
        border-bottom: 2px solid #333; margin-bottom: 20px; padding-bottom: 10px;
    }
    .sub-header { font-size: 14px; color: #666; text-transform: uppercase; margin-bottom: 30px; }
    .metric-box { background-color: #f9f9f9; padding: 15px; border-left: 5px solid #333; margin-bottom: 10px; }
    .highlight { background-color: #fff9c4; padding: 2px 5px; border-radius: 3px; }
</style>
""", unsafe_allow_html=True)

# --- HELPER FUNCTIONS ---
def read_pdf(file):
    reader = PyPDF2.PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

def read_docx(file):
    doc = docx.Document(file)
    text = "\n".join([para.text for para in doc.paragraphs])
    return text

# --- SIDEBAR INPUTS ---
st.sidebar.header("Data Submission")
st.sidebar.info("Upload Student Assignment (PDF or Word)")

student_id = st.sidebar.text_input("Student ID (Anonymised)", "STU-88942-X")
assessment_title = st.sidebar.text_input("Assessment Title", "History of Artificial Intelligence")

# FILE UPLOADER
uploaded_file = st.sidebar.file_uploader("Drop document here", type=["pdf", "docx"])
analyze_btn = st.sidebar.button("GENERATE REPORT", type="primary")

text_input = ""
if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith('.pdf'):
            text_input = read_pdf(uploaded_file)
            st.sidebar.success(f"PDF Loaded: {len(text_input)} characters detected.")
        elif uploaded_file.name.endswith('.docx'):
            text_input = read_docx(uploaded_file)
            st.sidebar.success(f"Word Doc Loaded: {len(text_input)} characters detected.")
    except Exception as e:
        st.sidebar.error("Error reading file. Please ensure it is not encrypted.")

# --- MAIN REPORT LOGIC ---
if analyze_btn and text_input:
    # Mimic "Processing" time
    with st.spinner(f"Extracting text from {uploaded_file.name}... Analyzing Stylometry..."):
        time.sleep(2) 
    
    # --- SIMULATED RESULTS (The backend math goes here later) ---
    word_count = len(text_input.split())
    
    # Logic: Shorter texts in this demo get higher AI scores
    if word_count > 100: 
        ai_score = random.randint(65, 95) # High AI likely
        burstiness = "Low (Uniform)"
        perplexity = "12.4 (Very Predictable)"
        label = "High Likelihood"
    else:
        ai_score = random.randint(5, 30) # Human likely
        burstiness = "High (Varied)"
        perplexity = "65.8 (Complex)"
        label = "Low Likelihood"

    # --- REPORT RENDER ---
    st.markdown(f"""
    <div class='report-container'>
        <div class='header'>Academic Integrity Evidence Report</div>
        <div class='sub-header'>CONFIDENTIAL // FOR INTERNAL USE ONLY</div>
        <p><strong>Institution:</strong> University Forensic Dept</p>
        <p><strong>Student ID:</strong> {student_id}</p>
        <p><strong>Assessment:</strong> {assessment_title}</p>
        <p><strong>File Name:</strong> {uploaded_file.name}</p>
        <p><strong>Report Date:</strong> {time.strftime("%d %B %Y")}</p>
        <br>
    """, unsafe_allow_html=True)

    st.markdown("## 1. Executive Summary")
    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="Aggregated AI Probability", value=f"{ai_score}%", delta=label, delta_color="inverse")
    with col2:
        st.metric(label="Stylometric Deviation", value="Medium-High")

    # Page 2 visuals
    st.markdown("---")
    st.markdown("## 2. Stylometric Fingerprint")
    st.write("Analysis of Burstiness (sentence variation) and Perplexity (text predictability).")

    data = {
        "Metric": ["Perplexity", "Burstiness", "Vocab Richness", "Syntax Variance"],
        "Value": [perplexity, burstiness, "0.45 (Average)", "Low"],
        "Interpretation": ["Consistent with AI" if ai_score > 50 else "Human Range", 
                           "Machine Pattern" if ai_score > 50 else "Natural", 
                           "-", "Repetitive Structure"]
    }
    st.table(pd.DataFrame(data))

    # Page 3 Simulation
    st.markdown("---")
    st.markdown("## 3. Extracted Text & Signals")
    
    sentences = text_input.split('.')
    # Show first 1000 characters to keep report clean
    display_sample = text_input[:2000] 
    
    # Highlight simulation
    formatted_text = display_sample.replace(" AI ", " <span class='highlight'> AI </span> ") \
                                   .replace(" the ", " <span class='highlight'> the </span> ")
    
    st.markdown(f"""
    <div style='background-color:#eee; padding:15px; font-size:12px; font-family:monospace;'>
    {formatted_text}... <br><br> 
    (Showing first 2000 chars of extracted text)
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

else:
    # LANDING PAGE
    st.title("🛡️ Academic Integrity Portal")
    st.markdown(f"""
    **Upload Evidence.**
    
    1.  Drag & drop a **PDF** or **Word (.docx)** file into the left sidebar.
    2.  Click **Generate Report**.
    
    *Current System Status: Online*
    """)
