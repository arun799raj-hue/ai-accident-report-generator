import streamlit as st
import google.generativeai as genai
from datetime import date
import tempfile
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import pandas as pd
import os
import matplotlib.pyplot as plt

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="AI Factory Accident Report Generator", layout="centered")

# -------- INDUSTRIAL DARK UI --------
st.markdown("""
<style>
[data-testid="stAppViewContainer"] {background-color:#0f172a;color:white;}
h1,h2,h3,h4 {color:#22c55e;}
.stButton>button {background:#22c55e;color:black;border-radius:8px;}
</style>
""", unsafe_allow_html=True)

st.title("AI Factory Accident Report Generator")
st.caption("Industrial Safety AI Dashboard")

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

injury_type = st.selectbox("Injury Type",["Burn","Slip","Cut","Fracture","Other"])
severity = st.selectbox("Injury Severity",["Minor","Major","Critical"])

st.subheader("Advanced Investigation Details")

role = st.selectbox("User Role",["Safety Officer","Supervisor","Manager"])
cause = st.selectbox("Accident Caused By",["Machine","Worker"])

# Role Based Compensation
if role == "Safety Officer":
    salary = st.number_input("Worker Monthly Salary",min_value=0)
    base_amount = st.number_input("Insurance Payable Amount",min_value=0)
else:
    st.info("Only Safety Officer can edit compensation.")
    salary = 0
    base_amount = 0

# Image Upload
uploaded_image = st.file_uploader("Upload Accident Image",type=["png","jpg","jpeg"])
temp_image_path = None
if uploaded_image:
    st.image(uploaded_image,caption="Accident Evidence",use_column_width=True)
    temp_img = tempfile.NamedTemporaryFile(delete=False)
    temp_img.write(uploaded_image.read())
    temp_image_path = temp_img.name

description = st.text_area("Describe what happened")

# ---------------- PDF CREATOR ----------------
def create_pdf(text,image_path=None):
    temp = tempfile.NamedTemporaryFile(delete=False,suffix=".pdf")
    c = canvas.Canvas(temp.name,pagesize=A4)

    c.setFont("Helvetica-Bold",14)
    c.drawString(50,800,"ABC INDUSTRIES PVT LTD")
    c.setFont("Helvetica",10)
    c.drawString(50,785,"Factory Accident Investigation Report")

    y = 760

    if image_path:
        try:
            c.drawImage(image_path,50,620,width=200,height=120)
            y = 580
        except:
            pass

    for line in text.split("\n"):
        if y < 50:
            c.showPage()
            y = 800
        c.drawString(50,y,line)
        y -= 14

    c.save()
    return temp.name

# ---------------- GENERATE BUTTON ----------------
generate = st.button("Generate Report")

if generate:

    if not worker_name or not description:
        st.warning("Please fill all required fields.")
    else:

        # ---------- INSURANCE LOGIC ----------
        if cause == "Machine":
            if severity == "Minor":
                insurance_text=f"""
Company Compensation:
- Payable Amount: {base_amount}
- 1 Month Salary: {salary}
- Medical Expenses Covered
"""
            elif severity == "Major":
                insurance_text=f"""
Company Compensation:
- Payable Amount: {base_amount}
- Medical Expenses Covered
"""
            else:
                insurance_text=f"""
Company Compensation:
- Huge Compensation: {base_amount}
- Medical Expenses Covered
- Job opportunity for one family member
"""
        else:
            insurance_text="""
Worker Responsibility:
- Safety training to be provided
- Mandatory safety protocol re-training
- Awareness and PPE compliance program
"""

        # -------- RISK SCORE ENGINE --------
        risk_score=0
        if severity=="Minor": risk_score+=20
        elif severity=="Major": risk_score+=60
        elif severity=="Critical": risk_score+=90

        if cause=="Machine": risk_score+=10
        else: risk_score+=30

        st.metric("⚠️ Predicted Risk Score",f"{risk_score}%")

        # ---------- AI PROMPT ----------
        prompt=f"""
You are an industrial safety officer AI.

User Role: {role}
Accident Caused By: {cause}
Insurance Decision:
{insurance_text}
Worker Name: {worker_name}
Employee ID: {worker_id}
Date: {accident_date}
Time: {accident_time}
Location: {location}
Machine: {machine}
Injury Type: {injury_type}
Severity: {severity}
Incident Description: {description}

Generate a structured professional industrial accident report.
"""

        try:
            response=model.generate_content(prompt)
            report=response.text

            st.success("Accident Report Generated")
            st.markdown("---")
            st.markdown(report)

            # TXT DOWNLOAD
            st.download_button("Download Report TXT",report,file_name="accident_report.txt")

            # PDF DOWNLOAD
            pdf_file=create_pdf(report,temp_image_path)
            with open(pdf_file,"rb") as f:
                st.download_button("Download PDF Report",f,file_name="Accident_Report.pdf")

            # -------- SAVE TO EXCEL DATABASE --------
            new_record={
                "Worker Name":worker_name,
                "Employee ID":worker_id,
                "Date":accident_date,
                "Time":accident_time,
                "Location":location,
                "Machine":machine,
                "Injury Type":injury_type,
                "Severity":severity,
                "Cause":cause,
                "Risk Score":risk_score
            }

            file_path="accident_database.xlsx"

            if os.path.exists(file_path):
                df=pd.read_excel(file_path)
            else:
                df=pd.DataFrame()

            updated_df=pd.concat([df,pd.DataFrame([new_record])],ignore_index=True)
            updated_df.to_excel(file_path,index=False)

            st.success("Record Saved to Industrial Database")

            # =====================================
            # INDUSTRIAL ANALYTICS DASHBOARD
            # =====================================
            st.markdown("---")
            st.subheader("📊 Industrial Safety Dashboard")

            total_accidents=len(updated_df)
            critical_cases=len(updated_df[updated_df["Severity"]=="Critical"])
            machine_faults=len(updated_df[updated_df["Cause"]=="Machine"])

            col1,col2,col3=st.columns(3)
            col1.metric("Total Accidents",total_accidents)
            col2.metric("Critical Cases",critical_cases)
            col3.metric("Machine Faults",machine_faults)

            # PIE 1
            st.markdown("### Severity Distribution")
            fig1,ax1=plt.subplots()
            updated_df["Severity"].value_counts().plot.pie(autopct='%1.1f%%',ax=ax1)
            st.pyplot(fig1)

            # PIE 2
            st.markdown("### Cause Analysis")
            fig2,ax2=plt.subplots()
            updated_df["Cause"].value_counts().plot.pie(autopct='%1.1f%%',ax=ax2)
            st.pyplot(fig2)

            # TREND GRAPH
            st.markdown("### Accident Trend Over Time")
            trend_df=updated_df.copy()
            trend_df["Date"]=pd.to_datetime(trend_df["Date"])
            trend_count=trend_df.groupby("Date").size()

            fig3,ax3=plt.subplots()
            trend_count.plot(ax=ax3)
            ax3.set_ylabel("Number of Accidents")
            st.pyplot(fig3)

        except Exception as e:
            st.error(f"Error generating report: {e}")

# =====================================
# 📂 VIEW INDUSTRIAL ACCIDENT DATABASE
# =====================================

st.markdown("---")
st.subheader("📂 Previous Accident Records (Industrial Database)")

file_path = "accident_database.xlsx"

if os.path.exists(file_path):

    db_df = pd.read_excel(file_path)

    # Show Table
    st.dataframe(db_df, use_container_width=True)

    # Download Full Database
    with open(file_path, "rb") as f:
        st.download_button(
            "⬇ Download Full Accident Database (Excel)",
            f,
            file_name="accident_database.xlsx"
        )

else:
    st.info("No accident records saved yet.")
