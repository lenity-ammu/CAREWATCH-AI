import streamlit as st
from fpdf import FPDF
from datetime import datetime
import os

from auth import require_role

require_role(["Doctor"])

st.set_page_config(
    page_title="AI Report Generation",
    page_icon="📄",
    layout="wide"
)

st.title("📄 AI Hospital Report")

# -------------------------------------------------
# Check whether prediction exists
# -------------------------------------------------

if "patient_info" not in st.session_state:

    st.warning("Please perform Patient Prediction first.")

    st.stop()

patient = st.session_state.get("patient_info", {})
prediction = st.session_state.get("prediction", 0)
probability = st.session_state.get("probability", 0)

conditions = st.session_state.get("conditions", [])
risk = st.session_state.get("risk_factors", [])
recommendations = st.session_state.get("recommendations", [])
summary = st.session_state.get("clinical_summary", "")
risk_level = st.session_state.get("risk_level", "Low")

# -------------------------------------------------
# Preview Report
# -------------------------------------------------

st.header("📋 Report Preview")

st.subheader("Patient Information")

st.json(patient)

st.subheader("Prediction")

if prediction == 1:
    st.error("🔴 High Risk")
else:
    st.success("🟢 Low Risk")

st.metric("Probability", f"{probability*100:.2f}%")

st.subheader("Detected Conditions")

if len(conditions)==0:

    st.info("No conditions detected")

else:

    for i in conditions:

        st.write("✔",i)

st.subheader("Readmission Risk Factors")

if len(risk)==0:

    st.info("None")

else:

    for i in risk:

        st.write("⚠",i)

st.subheader("AI Recommendations")

if len(recommendations)==0:

    st.info("None")

else:

    for i in recommendations:

        st.write("✅",i)

st.subheader("AI Clinical Summary")

st.success(summary)

st.divider()

# -------------------------------------------------
# Generate PDF
# -------------------------------------------------

if st.button("📥 Download Complete AI Report", use_container_width=True):

    pdf = FPDF()

    pdf.add_page()

    pdf.set_font("Arial","B",18)

    pdf.cell(190,10,"CAREWATCH-AI",ln=True,align="C")

    pdf.set_font("Arial","",12)

    pdf.cell(190,8,"AI Powered Hospital Readmission Prediction Report",ln=True,align="C")

    pdf.ln(5)

    pdf.set_font("Arial","B",14)

    pdf.cell(190,8,"Patient Information",ln=True)

    pdf.set_font("Arial","",11)

    for k,v in patient.items():

        pdf.cell(190,7,f"{k} : {v}",ln=True)

    pdf.ln(4)

    pdf.set_font("Arial","B",14)

    pdf.cell(190,8,"Prediction",ln=True)

    pdf.set_font("Arial","",11)

    pdf.cell(190,7,f"Risk Level : {risk_level}",ln=True)

    pdf.cell(190,7,f"Probability : {probability*100:.2f}%",ln=True)

    pdf.ln(4)

    pdf.set_font("Arial","B",14)

    pdf.cell(190,8,"Detected Conditions",ln=True)

    pdf.set_font("Arial","",11)

    if len(conditions)==0:

        pdf.cell(190,7,"None",ln=True)

    else:

        for c in conditions:

            pdf.cell(190,7,"- "+c,ln=True)

    pdf.ln(4)

    pdf.set_font("Arial","B",14)

    pdf.cell(190,8,"Readmission Risk Factors",ln=True)

    pdf.set_font("Arial","",11)

    if len(risk)==0:

        pdf.cell(190,7,"None",ln=True)

    else:

        for r in risk:

            pdf.cell(190,7,"- "+r,ln=True)

    pdf.ln(4)

    pdf.set_font("Arial","B",14)

    pdf.cell(190,8,"AI Recommendations",ln=True)

    pdf.set_font("Arial","",11)

    if len(recommendations)==0:

        pdf.cell(190,7,"None",ln=True)

    else:

        for rec in recommendations:

            pdf.multi_cell(190,7,"- "+rec)

    pdf.ln(4)

    pdf.set_font("Arial","B",14)

    pdf.cell(190,8,"AI Clinical Summary",ln=True)

    pdf.set_font("Arial","",11)

    pdf.multi_cell(190,7,summary)

    pdf.ln(4)

    pdf.set_font("Arial","B",12)

    pdf.cell(190,8,f"Generated : {datetime.now().strftime('%d-%m-%Y %H:%M')}",ln=True)
    
    # ============================================================
    # SAVE REPORT DATA FOR THE PATIENT
    # ============================================================

    patient_id = st.session_state.get("patient_id", None)

    if patient_id:

        report_data = {
            "patient_id": patient_id,
            "patient": patient,
            "prediction": int(prediction),
            "probability": float(probability),
            "risk_level": risk_level,
            "conditions": conditions,
            "risk_factors": risk,
            "recommendations": recommendations,
            "clinical_summary": summary,
            "generated_at": datetime.now().strftime(
                "%d-%m-%Y %H:%M"
            )
        }

        st.session_state["patient_report"] = report_data
        
        # ============================================================
        # SAVE REPORT PERSISTENTLY
        # ============================================================

        import json

        report_file = "patient_reports.json"

        # Load existing reports
        if os.path.exists(report_file):

            try:
                with open(report_file, "r", encoding="utf-8") as f:
                    all_reports = json.load(f)

            except (json.JSONDecodeError, FileNotFoundError):

                all_reports = {}

        else:

            all_reports = {}

        # Save report using patient ID
        all_reports[str(patient_id)] = report_data

        with open(report_file, "w", encoding="utf-8") as f:

            json.dump(
                all_reports,
                f,
                indent=4,
                ensure_ascii=False
            )

    filename="CareWatch_AI_Report.pdf"

    pdf.output(filename)

    with open(filename,"rb") as f:

        st.download_button(

            "⬇ Download PDF",

            f,

            file_name=filename,

            mime="application/pdf"

        )

    os.remove(filename)