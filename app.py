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
st.subheader("Advanced Investigation Details")

# Role Based Access
role = st.selectbox(
    "User Role",
    ["Safety Officer", "Supervisor", "Manager"]
)

# Accident Cause
cause = st.selectbox(
    "Accident Caused By",
    ["Machine", "Worker"]
)

# Insurance Details
salary = st.number_input("Worker Monthly Salary", min_value=0)
base_amount = st.number_input(
    "Insurance Payable Amount (Editable)",
    min_value=0
)

# Image Upload
uploaded_image = st.file_uploader(
    "Upload Accident Image (Optional)",
    type=["png","jpg","jpeg"]
)

if uploaded_image:
    st.image(uploaded_image, caption="Accident Evidence", use_column_width=True)

description = st.text_area("Describe what happened")
def create_pdf(text):
    temp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    c = canvas.Canvas(temp.name, pagesize=A4)

    # Company Header
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, 800, "ABC INDUSTRIES PVT LTD")
    c.setFont("Helvetica", 10)
    c.drawString(50, 785, "Factory Accident Investigation Report")

    y = 760
    for line in text.split("\n"):
        if y < 50:
            c.showPage()
            y = 800
        c.drawString(50, y, line)
        y -= 14

    c.save()
    return temp.name

# ---------------- REPORT GENERATION ----------------
generate = st.button("Generate Report")

if generate:

    if not worker_name or not description:
        st.warning("Please fill all required fields.")
    else:

        # ---------- INSURANCE LOGIC ----------
        insurance_text = ""

        if cause == "Machine":

            if severity == "Minor":
                insurance_text = f"""
Company Compensation:
- Payable Amount: {base_amount}
- 1 Month Salary: {salary}
- Medical Expenses Covered
"""

            elif severity == "Major":
                insurance_text = f"""
Company Compensation:
- Payable Amount: {base_amount}
- Medical Expenses Covered
"""

            elif severity == "Critical":
                insurance_text = f"""
Company Compensation:
- Huge Compensation: {base_amount}
- Medical Expenses Covered
- Job opportunity for one family member
"""
             
        else:
            insurance_text = """
Worker Responsibility:
- Safety training required
- Awareness program required
"""

        if cause == "Worker":
                 insurance_text = """
Worker Responsibility:
- Safety training to be provided to the worker
- Mandatory safety protocol re-training
- Awareness and PPE compliance program
"""
        # ---------- AI PROMPT ----------
        prompt = f"""
You are an industrial safety officer AI.

Generate a professional factory accident report using the details below.

User Role: {role}
Accident Caused By: {cause}
Insurance Decision:
{insurance_text}
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

            pdf_file = create_pdf(report)

            with open(pdf_file, "rb") as f:
                st.download_button(
                    "Download PDF Report",
                    f,
                    file_name="Accident_Report.pdf"
                )

        except Exception as e:
            st.error(f"Error generating report: {e}")
