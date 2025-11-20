import streamlit as st
import PyPDF2
import re
import hashlib
import google.generativeai as genai
import os
from dotenv import load_dotenv

# ----------------- Setup -----------------
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
st.set_page_config(page_title="Mental Health Risk Predictor", layout="centered")

# ----------------- Questions -----------------
questions = [
    "Do you often feel hopeless or down?",
    "Do you have trouble sleeping or experience nightmares?",
    "Have you had thoughts of self-harm or suicide recently?",
    "Do you feel isolated or withdrawn from others?",
    "Do you experience sudden mood swings or aggression?",
    "Are you currently taking any medications for mental health?",
    "Do you feel anxious or panicked regularly?"
]

# ----------------- Session State Init -----------------
if "submitted" not in st.session_state:
    st.session_state["submitted"] = False
if "responses" not in st.session_state:
    st.session_state["responses"] = [None] * len(questions)
if "file_hash" not in st.session_state:
    st.session_state["file_hash"] = None

# ----------------- Utility -----------------
def get_file_hash(file):
    return hashlib.md5(file.read()).hexdigest()

def extract_text_from_pdf(uploaded_file):
    uploaded_file.seek(0)
    reader = PyPDF2.PdfReader(uploaded_file)
    return " ".join([page.extract_text() for page in reader.pages if page.extract_text()])

def clean_text(text):
    return re.sub(r'\s+', ' ', text.strip())

def extract_counselor_section(text):
    match = re.search(r'--- COUNSELOR REPORT ---(.+)', text, re.IGNORECASE | re.DOTALL)
    return match.group(1).strip() if match else ""

def get_gemini_risk_score(text):
    prompt = f"""
Analyze this counselor note and return a risk score (0–3):
- 0 = No signs of suicidal thoughts
- 1 = Mild distress
- 2 = Concerning signs
- 3 = Suicidal ideation

Counselor Notes: '''{text}'''
ONLY return the number.
"""
    model = genai.GenerativeModel(model_name="gemini-pro")
    try:
        response = model.generate_content(prompt)
        return min(3, max(0, int(response.text.strip())))
    except:
        return 1

def evaluate_medical_section(text):
    score = 0
    if match := re.search(r'Blood Pressure:\s*(\d{2,3})/(\d{2,3})', text):
        if int(match.group(1)) > 140 or int(match.group(2)) > 90:
            score += 1
    if match := re.search(r'Cortisol Level:\s*(\d+)', text):
        if int(match.group(1)) > 20:
            score += 1
    if "Serotonin Level: Low" in text:
        score += 1
    if match := re.search(r'Heart Rate:\s*(\d+)', text):
        if int(match.group(1)) > 100:
            score += 1
    return score

def calculate_final_score(medical, counselor, questionnaire):
    return (medical * 0.3 + counselor * 0.4 + questionnaire * 0.3) / 4 * 100

def reset_questionnaire():
    for i in range(1, len(questions)+1):
        st.session_state.pop(f"q{i}", None)
    st.session_state["responses"] = [None] * len(questions)
    st.session_state["submitted"] = False

# ----------------- UI Starts -----------------
st.markdown("""
    <h1 style='text-align: center; color: #800080;'>🧠 Suicide Risk Predictor</h1>
    <h4 style='text-align: center; color: #444;'>PDF Report + Gemini AI + Mental Health Questionnaire</h4>
""", unsafe_allow_html=True)

st.markdown("<h4 style='text-align:center;'>📄 Upload Combined Medical + Counselor Report (PDF)</h4>", unsafe_allow_html=True)
uploaded_file = st.file_uploader("Choose a PDF file", type=["pdf"])

# ----------------- Detect New File & Reset -----------------
if uploaded_file:
    uploaded_file.seek(0)
    new_hash = get_file_hash(uploaded_file)

    if new_hash != st.session_state["file_hash"]:
        reset_questionnaire()
        st.session_state["file_hash"] = new_hash
        st.rerun()

# ----------------- Proceed If File Exists -----------------
if uploaded_file:
    uploaded_file.seek(0)
    raw_text = extract_text_from_pdf(uploaded_file)
    cleaned_text = clean_text(raw_text)
    counselor_text = extract_counselor_section(cleaned_text)

    med_score = evaluate_medical_section(cleaned_text)
    st.markdown("### 🩺 <span style='color:#2E8B57;'>Physical Health Evaluation</span>", unsafe_allow_html=True)
    st.markdown(f"<b>Medical Score:</b> <span style='color:#00008B'>{med_score}/4</span>", unsafe_allow_html=True)

    st.markdown("### 🧠 <span style='color:#8B008B;'>Gemini Counselor Risk Analysis</span>", unsafe_allow_html=True)
    with st.spinner("Analyzing counselor notes..."):
        counselor_score = get_gemini_risk_score(counselor_text)
    st.markdown(f"<b>Gemini Counselor Score:</b> <span style='color:#00008B'>{counselor_score}/3</span>", unsafe_allow_html=True)

    # ----------------- Questionnaire -----------------
    st.markdown("""
        <style>
        .question-card {
            border: 1px solid #ddd;
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 10px;
            background-color: #f8f9fa;
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("### 📝 <span style='color:#DAA520;'>Mental Health Questionnaire</span>", unsafe_allow_html=True)
    for idx, q in enumerate(questions, 1):
        with st.container():
            st.markdown(f"<div class='question-card'><strong>Q{idx}:</strong> {q}</div>", unsafe_allow_html=True)
            st.session_state["responses"][idx - 1] = st.radio("Select an answer:", ["Yes", "No"], index=None, key=f"q{idx}")

    if st.button("Submit"):
        if None in st.session_state["responses"]:
            st.warning("⚠️ Please answer all questions before submitting.")
        else:
            st.session_state["submitted"] = True
            st.rerun()

    if st.session_state["submitted"]:
        q_score = sum(1 for r in st.session_state["responses"] if r == "Yes")
        q_score = min(q_score, 4)
        st.markdown(f"<b>Questionnaire Score:</b> <span style='color:#00008B'>{q_score}/4</span>", unsafe_allow_html=True)

        final_score = calculate_final_score(med_score, counselor_score, q_score)
        st.markdown(f"""
            <div style='margin-top: 20px; padding: 15px; background-color: #e0e0ff; border-radius: 12px;'>
                <h3 style='color: #4B0082;'>📊 Final Suicidal Risk Estimate</h3>
                <p style='font-size: 26px; color: #FF4500;'><b>{final_score:.2f}% Risk</b></p>
            </div>
        """, unsafe_allow_html=True)

        if final_score >= 70:
            st.markdown("""<div style="padding: 15px; background-color: #ffe6e6; border-radius: 10px; border: 2px solid red;">🔴 <strong>High Risk Detected</strong><br>Immediate professional help is strongly recommended.</div>""", unsafe_allow_html=True)
        elif final_score >= 40:
            st.markdown("""<div style="padding: 15px; background-color: #fff3cd; border-radius: 10px; border: 2px solid #ffcc00;">🟠 <strong>Moderate Risk Detected</strong><br>Caution advised. Talk to someone you trust.</div>""", unsafe_allow_html=True)
        else:
            st.markdown("""<div style="padding: 15px; background-color: #d4edda; border-radius: 10px; border: 2px solid #28a745;">🟢 <strong>Low Risk Detected</strong><br>You're doing well. Keep going! 💪</div>""", unsafe_allow_html=True)

       