import streamlit as st
import google.generativeai as genai
from fpdf import FPDF
st.set_page_config(page_title="AI Accident Report Generator", layout="centered")
st.title("AI Accident Report Generator")
api_key = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=api_key)
model = genai.GenerativeMdel("gemini-1.5-flash")
with st.form("accident_form"):
  worker_name = st.text_input("Worker Name")
  worker_id = st.text_input("Employee ID")
  date = st.date_input("Date of Accident")
  time = st.text_input("Time (HH:MM)")
  location = st.text_input("Location")
  machine = st.text_input("Machine / Equipment")
  injury_type = st.text_input("Injury Type")
  severity = st.selectbox("Severity", ["Minor", "Major", "Critical"])
  description = st.text_area("Accident Description")
  submit = st.form_submit_button("Generate Report")
  if submit:
    prompt = f"""
    You are an industrial safety officer AI.

    Generate a professional factory accident report.

    Worker Name: {worker_name}
    Employee ID: {worker_id}
    Date: {date}
    Time: {time}
    Location: {location}
    Machine: {machine}
    Injury Type: {injury_type}
    Severity:; {severity}
    Description: {description}

    Include:
    1. Summary
    2. Root Cause
    3. Corrective Actions
    4.Preventive Measures
    5.Risk Assessment
    """
    with st.spinner("Generating report..."):
      model = genai.GenerativeModel("gemini-1.5-flash")
      response = mdel.generate_content(prompt)
      report = response.text
      st.subheader("Accident Report")
      st.write(report)
      pdf = FPDF()
      pdf.add_page()
      pdf.set_font("Arial", size=11)
      for line in report.split("\n"):
        pdf.multi_cell(0, 8, line.encode("latin-1", "replace").decode("latin-1"))
        pdf_file = "AI_Accident_Report.pdf"
        pdf.output(pdf_file)
        with open(pdf_file, "rb") as f:
          st.download_button("Download PDF", f, file_name=pdf_file)
      
