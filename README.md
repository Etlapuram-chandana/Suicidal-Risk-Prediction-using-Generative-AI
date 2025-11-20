# Suicidal Risk Prediction Using Generative AI

This project provides an AI-powered system to analyze medical reports, counselor notes, and psychological questionnaire responses to estimate suicidal risk. It leverages Generative AI (Gemini-Pro), PDF parsing, and rule-based medical scoring to produce a combined, weighted risk prediction.

# Features

Extracts and preprocesses text from uploaded PDF reports.

Evaluates physical health indicators (BP, cortisol, heart rate, serotonin).

Uses Gemini AI to analyze counselor notes and classify risk levels.

Implements a mental health questionnaire for self-assessment.

Generates a final weighted suicidal risk score (%).

Displays dynamic risk indicators (Low / Moderate / High).

Automatically resets questionnaire when a new PDF is uploaded.

Provides a clean, interactive UI using Streamlit.

# Requirements
Python Version

Python 3.8+

# Libraries

streamlit

PyPDF2

google-generativeai

python-dotenv

re (built-in)

hashlib (built-in)

os (built-in)

# Steps

Clone this repository:

git clone https://github.com/your-repo-name/suicidal-risk-prediction.git


Install dependencies:

pip install -r requirements.txt


Create a .env file and add your Gemini API key:

GOOGLE_API_KEY=your_gemini_api_key


Run the Streamlit application:

streamlit run app.py

# Usage
1. Upload PDF Report

Upload a combined medical + counselor PDF file containing:

Blood pressure

Cortisol level

Serotonin level

Heart rate

Counselor evaluation / notes

The system will automatically extract and clean the text.

2. AI-Based Counselor Risk Analysis (Gemini)

Internally:

counselor_score = get_gemini_risk_score(counselor_text)


Gemini returns:

0 – No suicidal signs

1 – Mild distress

2 – Concerning signs

3 – Suicidal ideation

3. Medical Risk Evaluation

The system automatically detects and scores:

Blood pressure

Cortisol

Serotonin

Heart rate

Score range: 0–4

4. Mental Health Questionnaire

Users answer 7 yes/no psychological questions, converted to:

Score range: 0–4 (normalized)

5. Final Risk Score

Calculated as:

Final Score = (0.3 * Medical + 0.4 * Counselor + 0.3 * Questionnaire) / 4 * 100


Outputs include:

Risk %

Low / Moderate / High Risk categories

Color-coded alerts

# Outputs

Medical Score (0–4)

Gemini Counselor Score (0–3)

Questionnaire Score (0–4)

Final Suicidal Risk Percentage

Status Indicator:

🟢 Low Risk

🟠 Moderate Risk

🔴 High Risk

# Dataset Description

The model does not require a dataset to train. It uses:

PDF-based medical values (regex extraction)

Counselor notes analyzed via Generative AI

User questionnaire responses

Extracted sections include:

Physical Health Metrics

Counselor Observations

Symptom Patterns & Behavioral Clues

# Model Details
Algorithms Used

Gemini-Pro (Generative AI)

Interprets counselor notes

Classifies suicidal tendencies

Rule-Based Scoring System:

Extracts vitals and medical indicators

Assigns risk weights

Weighted Aggregation Model

Combines Medical + Counselor + Questionnaire into a final score

# Evaluation Metrics

Although this is not a predictive ML model, it uses:

Pattern-based extraction accuracy

Counselor note classification reliability

Weighted scoring stability

# Contribution

Contributions are welcome!
Feel free to submit issues, improve the UI, or enhance scoring logic.
Pull requests are appreciated.

# License

This project is licensed under the MIT License.
