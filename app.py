import streamlit as st
import google.generativeai as genai
from datetime import date, time

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="AI Factory Accident Report Generator",
    layout="centered"
)

st.title("AI Factory Accident Report Generator")
st.caption("Generate professional industrial accident reports using AI")

# ---------------- API CONFIG ----------------
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
model = genai.GenerativeModel("gemini-flash-latest")

# ---------------- FORM INPUTS ----------------
st.subheader("Accident Details")

worker_name = st.text_input("Worker Name")
worker_id = st.text_input("Employee ID")

accident_date = st.date_input("Date of Accident", value=date.today())
accident_time = st.time_input("Time of Accident")

location = st.text_input("Accident Location")
machine = st.text_input("Machine / Equipment Involved")

injury_type = st.selectbox(
    "Injury Type",
    ["Burn", "Slip", "Cut", "Fracture", "Other"]
)

severity = st.selectbox(
    "Injury Severity",
    ["Minor", "Major", "Critical"]
)

description = st.text_area("Describe what happened")

generate = st.button("Generate Report")

# ---------------- REPORT GENERATION ----------------
if generate:
    if not worker_name or not description:
        st.warning("Please fill all required fields.")
    else:
        prompt = f"""
You are an industrial safety officer AI.

Generate a professional factory accident report using the details below.

Worker Name: {worker_name}
Employee ID: {worker_id}
Date: {accident_date}
Time: {accident_time}
Location: {location}
Machine/Equipment: {machine}
Injury Type: {injury_type}
Severity: {severity}
Incident Description: {description}

The report must include:
1. Accident Summary
2. Employee Details
3. Incident Description
4. Root Cause Analysis
5. Safety Violations (if any)
6. Immediate Actions Taken
7. Corrective Actions
8. Preventive Measures
9. Risk Level Assessment
10. Conclusion

Use clear, formal, professional language.
"""

        try:
            response = model.generate_content(prompt)
            report = response.text

            st.success("Accident Report Generated")
            st.markdown("---")
            st.markdown(report)

            st.download_button(
                label="Download Report",
                data=report,
                file_name="accident_report.txt"
            )

        except Exception as e:
            st.error(f"Error generating report: {e}")
