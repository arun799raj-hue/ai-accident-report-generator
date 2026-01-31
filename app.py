import streamlit as st
import google.generativeai as genai
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import tempfile
import os
st.set_page_config(page_title="AI Accident Report Generator", layout="centered")
st.caption("Generate prfessional industrial accident reports using AI")
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
model = genai.GenerativeModel("models/gemini-1.5-flash")
response = model.generate_content(prompt)
report = response.text
with st.form("accident_form"):
    st.subheader("Accident Details")
    worker_name = st.text_input("Worker Name")
    worker_id = st.text_input("Worker ID")
    date = st.date_input("Date of Accident")
    time = st.time_input("Time of Accident")
    location = st.text_input("Accident Location")
    machine = st.text_input("Machine / Equipment Involved")
    injury_type = st.text_input("Injury Type (burn, slip, cut, etc..)")
    severity = st.selectbox("Injury Severity", ["Minor", "Major", "Critical"])
    description = st.text_area("Describe what happened")
    generate = st.form_submit_button("Generate Report")
    if generate:
      if not worker_name or not description:
        st.warning("Please fill all required fields.")
      else:
        with st.spinner("Generating report using AI..."):
          prompt = f"""
          You are an industrial safety officer AI.

          Generate a professional factory accident report using details below.

          Worker Name: {worker_name}
          Employee ID: {worker_id}
          Date: {date}
          Time: {time}
          Location: {location}
          Machine/Equipment: {machine}
          Injury Type: {injury_type}
          Severity: {severity}
          Description: {description}

          The report must include:
          1. Accident Summary
          2. Employee Details
          3. Incident Description
          4. Root cause Analysis
          5. Safety Violation(if any)
          6. Immediate Actions Taken
          7. Corrective Actions
          8. Preventive Measures
          9. Risk level Assessment
          10. Conclusion

          Use clear, formal, professional language.
          """
          try:
              response = model.generate_content(prompt)
              report = response.text
              st.success("Accident Report Generated")
              st.markdown("---")
              st.markdown(report)
              def create_pdf(text):
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
                c = Canvas(temp_file.name, pagesize= A4)
                y = height - 40
                for line in text.split("\n"):
                  if y < 40:
                    c.showPage()
                    y = height - 40
                    c.drawString(40, y, line)
                    y -= 14
                    c.save()
                    return temp_file.name
              pdf_path = create_pdf(report)
              with open(pdf_path, "rb") as pdf_file:
                 st.download_button(label="Download Report as PDF", data=pdf_file, file_name="Accident_Report.pdf", mime="application/pdf")
                 os.remove(pdf_path)
          except Exception as e:
                 st.error(f"Error generating report: {e}")
                      
          
                            

