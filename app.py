import streamlit as st
import google.generativeai as genai
st.set_page_config(page_title="AI Accident Report Generator", layout="centered")
st.title("AI Factory Accident Report Generator")
st.write("Generate professional industrial accident reports using AI.")
api_key = st.secrets.get("GEMINI_API_KEY")
if not api_key:
  st.error("API Key not found")
  st.stop()
  genai.configure(api_key=api_key)
  model = genai.GenerativeModel("gemini-1.5-flash")
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
    submit = st.form_submit_button("Generate Accident Report")
    if submit:
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
              st.download_button("Download Report", file_name="Accident_Report.txt")
          except Exception as e:
              st.error(f"Error generating report: {e}")
                      
          
                            

