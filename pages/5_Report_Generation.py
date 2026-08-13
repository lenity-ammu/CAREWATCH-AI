import streamlit as st
import pandas as pd
import os
from datetime import datetime
from io import BytesIO

from auth import require_login

# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="CareWatch-AI | Reports",
    page_icon="📄",
    layout="wide"
)

require_login()

# ============================================================
# REPORTLAB
# ============================================================

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import (
        SimpleDocTemplate,
        Paragraph,
        Spacer,
        Table,
        TableStyle
    )
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib.enums import TA_CENTER

    REPORTLAB_AVAILABLE = True

except Exception:
    REPORTLAB_AVAILABLE = False


# ============================================================
# DATA
# ============================================================

BASE_DIR = os.path.dirname(os.path.dirname(__file__))


@st.cache_data
def load_csv(filename):

    path = os.path.join(BASE_DIR, filename)

    if not os.path.exists(path):
        return pd.DataFrame()

    try:
        return pd.read_csv(path)
    except Exception:
        return pd.DataFrame()


patients = load_csv("patients.csv")
predictions = load_csv("prediction_results.csv")

role = st.session_state.get("role", "")

# ============================================================
# HEADER
# ============================================================

st.title("📄 CareWatch-AI Report Generation")

if role == "Patient":
    st.caption(
        "Download your latest CareWatch-AI health assessment as a PDF."
    )
else:
    st.caption(
        "Generate a clinical PDF report for the selected patient."
    )

# ============================================================
# PATIENT SELECTION
# ============================================================

patient_id = st.session_state.get("patient_id")

if role in ["Doctor", "Admin"]:

    if patients.empty:

        st.error("Patient dataset is unavailable.")
        st.stop()

    patient_ids = (
        patients["patient_id"]
        .astype(str)
        .dropna()
        .unique()
        .tolist()
    )

    patient_id = st.selectbox(
        "Select Patient",
        sorted(patient_ids)
    )

elif role == "Patient":

    if not patient_id:
        st.error("No patient account is associated with this session.")
        st.stop()

    patient_id = str(patient_id).strip()

else:

    st.error("You are not authorized to generate reports.")
    st.stop()

# ============================================================
# GET PATIENT
# ============================================================

patient_rows = patients[
    patients["patient_id"].astype(str).str.strip() == str(patient_id)
]

if patient_rows.empty:

    st.error("Patient record was not found.")
    st.stop()

patient = patient_rows.iloc[0]

# ============================================================
# GET PREDICTION
# ============================================================

prediction = None

if not predictions.empty and "patient_id" in predictions.columns:

    rows = predictions[
        predictions["patient_id"].astype(str).str.strip()
        == str(patient_id)
    ].copy()

    if not rows.empty:

        if "timestamp" in rows.columns:

            rows["timestamp"] = pd.to_datetime(
                rows["timestamp"],
                errors="coerce"
            )

            rows = rows.sort_values("timestamp")

        prediction = rows.iloc[-1]

if prediction is None:

    st.warning(
        "No AI prediction is available for this patient."
    )

    st.info(
        "Complete the AI readmission prediction before generating the report."
    )

    st.stop()

# ============================================================
# PREDICTION VALUES
# ============================================================

risk_level = str(
    prediction.get(
        "risk_level",
        prediction.get("risk", "Low")
    )
)

probability = prediction.get(
    "readmission_probability",
    prediction.get("probability", 0)
)

try:
    probability = float(probability)
except Exception:
    probability = 0.0

if probability <= 1:
    probability_percent = probability * 100
else:
    probability_percent = probability

risk_lower = risk_level.lower()

if "high" in risk_lower:

    summary = (
        "The AI model indicates a higher risk of hospital "
        "readmission within 30 days."
    )

elif "moderate" in risk_lower or "medium" in risk_lower:

    summary = (
        "The AI model indicates a moderate risk of hospital "
        "readmission within 30 days. Additional clinical "
        "monitoring may be appropriate."
    )

else:

    summary = (
        "The AI model indicates a lower risk of 30-day "
        "hospital readmission."
    )

recommendations = [
    "Discuss the assessment with your doctor.",
    "Attend scheduled follow-up appointments.",
    "Continue regular health monitoring."
]

generated_time = datetime.now().strftime(
    "%Y-%m-%d %H:%M:%S"
)

# ============================================================
# PREVIEW
# ============================================================

st.markdown("---")

st.subheader("📋 Report Preview")

c1, c2, c3 = st.columns(3)

with c1:
    st.metric(
        "Patient ID",
        str(patient_id)
    )

with c2:
    st.metric(
        "Risk Level",
        risk_level
    )

with c3:
    st.metric(
        "30-Day Readmission Probability",
        f"{probability_percent:.2f}%"
    )

st.markdown("### 👤 Patient Information")

patient_display = {
    "Patient ID": patient_id,
    "Age": patient.get("age", "N/A"),
    "Gender": patient.get("gender", "N/A"),
    "State": patient.get("state", "N/A"),
    "Insurance": patient.get("insurance_type", "N/A"),
    "BPL Card": patient.get("bpl_card", "N/A"),
    "Comorbidity Count": patient.get(
        "comorbidity_count",
        "N/A"
    ),
    "Previous Admissions": patient.get(
        "prev_admissions",
        "N/A"
    )
}

st.table(
    pd.DataFrame(
        list(patient_display.items()),
        columns=["Field", "Value"]
    )
)

st.markdown("### 🧠 Medical Summary")

st.info(summary)

st.markdown("### 💡 Recommendations")

for recommendation in recommendations:
    st.success(f"✅ {recommendation}")

# ============================================================
# PDF GENERATOR
# ============================================================

def create_pdf():

    if not REPORTLAB_AVAILABLE:
        return None

    buffer = BytesIO()

    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    styles = getSampleStyleSheet()

    title_style = styles["Title"]
    title_style.alignment = TA_CENTER

    heading_style = styles["Heading2"]
    body_style = styles["BodyText"]

    story = []

    story.append(
        Paragraph(
            "CAREWATCH-AI",
            title_style
        )
    )

    story.append(
        Paragraph(
            "Patient Health & AI Readmission Risk Report",
            styles["Heading2"]
        )
    )

    story.append(Spacer(1, 20))

    patient_table = [
        ["Patient ID", str(patient_id)],
        ["Age", str(patient.get("age", "N/A"))],
        ["Gender", str(patient.get("gender", "N/A"))],
        ["State", str(patient.get("state", "N/A"))],
        [
            "Insurance",
            str(patient.get("insurance_type", "N/A"))
        ],
        [
            "BPL Card",
            str(patient.get("bpl_card", "N/A"))
        ],
        [
            "Comorbidity Count",
            str(patient.get("comorbidity_count", "N/A"))
        ],
        [
            "Previous Admissions",
            str(patient.get("prev_admissions", "N/A"))
        ]
    ]

    table = Table(
        patient_table,
        colWidths=[170, 300]
    )

    table.setStyle(
        TableStyle([
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("BACKGROUND", (0, 0), (0, -1), colors.lightgrey),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("RIGHTPADDING", (0, 0), (-1, -1), 8),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6)
        ])
    )

    story.append(table)

    story.append(Spacer(1, 20))

    story.append(
        Paragraph(
            "AI Readmission Risk Assessment",
            heading_style
        )
    )

    risk_table = [
        ["Risk Level", risk_level],
        [
            "30-Day Readmission Probability",
            f"{probability_percent:.2f}%"
        ]
    ]

    risk_table_obj = Table(
        risk_table,
        colWidths=[220, 250]
    )

    risk_table_obj.setStyle(
        TableStyle([
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("BACKGROUND", (0, 0), (0, -1), colors.lightgrey),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("RIGHTPADDING", (0, 0), (-1, -1), 8),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6)
        ])
    )

    story.append(risk_table_obj)

    story.append(Spacer(1, 20))

    story.append(
        Paragraph(
            "Medical Summary",
            heading_style
        )
    )

    story.append(
        Paragraph(
            summary,
            body_style
        )
    )

    story.append(Spacer(1, 20))

    story.append(
        Paragraph(
            "Recommendations",
            heading_style
        )
    )

    for item in recommendations:

        story.append(
            Paragraph(
                "• " + item,
                body_style
            )
        )

        story.append(Spacer(1, 5))

    story.append(Spacer(1, 20))

    story.append(
        Paragraph(
            f"Generated: {generated_time}",
            body_style
        )
    )

    story.append(Spacer(1, 10))

    story.append(
        Paragraph(
            "Confidential Patient Health Information",
            body_style
        )
    )

    story.append(Spacer(1, 10))

    story.append(
        Paragraph(
            "Clinical decisions should always be made by qualified healthcare professionals.",
            body_style
        )
    )

    document.build(story)

    buffer.seek(0)

    return buffer.getvalue()


# ============================================================
# DOWNLOAD
# ============================================================

st.markdown("---")

if not REPORTLAB_AVAILABLE:

    st.error(
        "PDF generation requires ReportLab. "
        "Please install it in the active healthcare environment."
    )

else:

    pdf_bytes = create_pdf()

    filename = (
        f"CareWatch_AI_Report_{patient_id}.pdf"
    )

    st.download_button(
        label="📥 Download PDF Report",
        data=pdf_bytes,
        file_name=filename,
        mime="application/pdf",
        use_container_width=True
    )

    st.success(
        "PDF report is ready for download."
    )