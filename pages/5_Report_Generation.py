import os
import json
from datetime import datetime

import pandas as pd
import streamlit as st

from auth import require_login


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="CareWatch-AI | Report Generation",
    page_icon="📄",
    layout="wide"
)

require_login()


# =========================================================
# PATHS
# =========================================================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PATIENTS_FILE = os.path.join(BASE_DIR, "patients.csv")
PREDICTIONS_FILE = os.path.join(BASE_DIR, "prediction_results.csv")
ADMISSIONS_FILE = os.path.join(BASE_DIR, "admissions.csv")
DIAGNOSES_FILE = os.path.join(BASE_DIR, "diagnoses.csv")
BILLING_FILE = os.path.join(BASE_DIR, "billing.csv")
HOSPITALS_FILE = os.path.join(BASE_DIR, "hospitals.csv")


# =========================================================
# LOAD CSV SAFELY
# =========================================================

@st.cache_data
def load_csv(path):

    if not os.path.exists(path):
        return pd.DataFrame()

    try:
        return pd.read_csv(path)
    except Exception:
        return pd.DataFrame()


patients = load_csv(PATIENTS_FILE)
predictions = load_csv(PREDICTIONS_FILE)
admissions = load_csv(ADMISSIONS_FILE)
diagnoses = load_csv(DIAGNOSES_FILE)
billing = load_csv(BILLING_FILE)
hospitals = load_csv(HOSPITALS_FILE)


# =========================================================
# NORMALIZE COLUMN NAMES
# =========================================================

def normalize_columns(df):

    if df.empty:
        return df

    df = df.copy()

    df.columns = [
        str(c).strip().lower().replace(" ", "_")
        for c in df.columns
    ]

    return df


patients = normalize_columns(patients)
predictions = normalize_columns(predictions)
admissions = normalize_columns(admissions)
diagnoses = normalize_columns(diagnoses)
billing = normalize_columns(billing)
hospitals = normalize_columns(hospitals)


# =========================================================
# NORMALIZE IDs
# =========================================================

def normalize_id(value):

    if value is None:
        return ""

    return str(value).strip()


for df in [
    patients,
    predictions,
    admissions,
    diagnoses,
    billing,
    hospitals
]:

    if "patient_id" in df.columns:
        df["patient_id"] = df["patient_id"].astype(str).str.strip()

    if "admission_id" in df.columns:
        df["admission_id"] = df["admission_id"].astype(str).str.strip()


# =========================================================
# GET ROLE
# =========================================================

role = st.session_state.get("role", "")

if role not in ["Doctor", "Admin", "Patient"]:

    st.error("You are not authorized to generate reports.")
    st.stop()


# =========================================================
# PATIENT SELECTION
# =========================================================

st.title("📄 CareWatch-AI Report Generation")

st.caption(
    "Generate and download the patient's clinical AI prediction report."
)

st.markdown("---")


if role == "Patient":

    selected_patient = normalize_id(
        st.session_state.get("patient_id")
    )

    if not selected_patient:
        st.error("Patient ID could not be found.")
        st.stop()

    st.info(
        f"Patient Report: {selected_patient}"
    )

else:

    if patients.empty or "patient_id" not in patients.columns:

        st.error("Patient data could not be loaded.")
        st.stop()

    patient_ids = sorted(
        patients["patient_id"]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )

    if not patient_ids:

        st.error("No patients were found.")
        st.stop()

    selected_patient = st.selectbox(
        "Select Patient",
        patient_ids
    )


patient_id = normalize_id(selected_patient)


# =========================================================
# FIND PATIENT
# =========================================================

patient = None

if not patients.empty and "patient_id" in patients.columns:

    patient_rows = patients[
        patients["patient_id"] == patient_id
    ]

    if not patient_rows.empty:
        patient = patient_rows.iloc[0]


# =========================================================
# FIND LATEST PREDICTION
# =========================================================

def find_latest_prediction(patient_id):

    if predictions.empty:
        return None

    if "patient_id" not in predictions.columns:
        return None

    data = predictions.copy()

    data["patient_id"] = (
        data["patient_id"]
        .astype(str)
        .str.strip()
    )

    data = data[
        data["patient_id"] == patient_id
    ].copy()

    if data.empty:
        return None

    # Try to identify the newest prediction.
    date_columns = [
        "timestamp",
        "created_at",
        "prediction_date",
        "created_at_timestamp",
        "datetime"
    ]

    for column in date_columns:

        if column in data.columns:

            parsed = pd.to_datetime(
                data[column],
                errors="coerce"
            )

            if parsed.notna().any():

                data["_sort_date"] = parsed

                data = data.sort_values(
                    "_sort_date",
                    ascending=False
                )

                return data.iloc[0]

    # If no timestamp exists,
    # use the last stored prediction.
    return data.iloc[-1]


prediction = find_latest_prediction(patient_id)


# =========================================================
# IMPORTANT FIX
# =========================================================

if prediction is None:

    st.warning(
        "No AI prediction is available for this patient."
    )

    st.info(
        "Complete the AI Readmission Prediction first. "
        "The report will automatically use the saved prediction "
        "from prediction_results.csv."
    )

    st.stop()


# =========================================================
# HELPER FUNCTIONS
# =========================================================

def get_value(row, possible_columns, default="N/A"):

    if row is None:
        return default

    for column in possible_columns:

        if column in row.index:

            value = row[column]

            if pd.isna(value):
                continue

            return value

    return default


def format_probability(value):

    try:

        number = float(value)

        # Handle either 0.154 or 15.4
        if number <= 1:
            number *= 100

        return f"{number:.2f}%"

    except Exception:

        return "N/A"


def risk_from_probability(probability):

    try:

        p = float(probability)

        if p <= 1:
            p *= 100

        if p >= 70:
            return "High Risk"

        if p >= 30:
            return "Moderate Risk"

        return "Low Risk"

    except Exception:

        return "Unknown"


# =========================================================
# PREDICTION VALUES
# =========================================================

probability = get_value(
    prediction,
    [
        "readmission_probability",
        "prediction_probability",
        "probability",
        "risk_probability",
        "readmission_prob",
        "predicted_probability"
    ],
    None
)

risk_level = get_value(
    prediction,
    [
        "risk_level",
        "risk",
        "risk_category",
        "prediction"
    ],
    None
)

if probability is not None:

    probability_display = format_probability(
        probability
    )

    if not risk_level:
        risk_level = risk_from_probability(
            probability
        )

else:

    probability_display = "N/A"

    if not risk_level:
        risk_level = "Unknown"


prediction_date = get_value(
    prediction,
    [
        "timestamp",
        "created_at",
        "prediction_date"
    ],
    datetime.now().strftime("%Y-%m-%d %H:%M:%S")
)


# =========================================================
# DISPLAY PREDICTION
# =========================================================

st.subheader("🤖 AI Readmission Prediction")

c1, c2, c3 = st.columns(3)

with c1:
    st.metric(
        "Patient ID",
        patient_id
    )

with c2:
    st.metric(
        "Risk Level",
        str(risk_level)
    )

with c3:
    st.metric(
        "Readmission Probability",
        probability_display
    )


st.success(
    "Saved AI prediction found successfully."
)


# =========================================================
# PATIENT INFORMATION
# =========================================================

st.markdown("---")

st.subheader("👤 Patient Information")

if patient is not None:

    patient_info = {}

    for column in [
        "patient_id",
        "age",
        "gender",
        "state",
        "insurance_type",
        "bpl_card",
        "comorbidity_count"
    ]:

        if column in patient.index:

            patient_info[column.replace("_", " ").title()] = (
                patient[column]
            )

    if patient_info:

        patient_df = pd.DataFrame(
            list(patient_info.items()),
            columns=["Information", "Value"]
        )

        st.dataframe(
            patient_df,
            use_container_width=True,
            hide_index=True
        )

else:

    st.info(
        "Patient demographic information was not found."
    )


# =========================================================
# ADMISSION SUMMARY
# =========================================================

st.markdown("---")

st.subheader("🏥 Admission Summary")

patient_admissions = pd.DataFrame()

if (
    not admissions.empty
    and "patient_id" in admissions.columns
):

    patient_admissions = admissions[
        admissions["patient_id"] == patient_id
    ].copy()


if not patient_admissions.empty:

    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric(
            "Total Admissions",
            len(patient_admissions)
        )

    with c2:

        if "los_days" in patient_admissions.columns:

            los = pd.to_numeric(
                patient_admissions["los_days"],
                errors="coerce"
            ).mean()

            st.metric(
                "Average Length of Stay",
                f"{los:.1f} days"
            )

        else:

            st.metric(
                "Average Length of Stay",
                "N/A"
            )

    with c3:

        if "prev_admissions" in patient.index:

            st.metric(
                "Previous Admissions",
                patient["prev_admissions"]
            )

        else:

            st.metric(
                "Previous Admissions",
                "N/A"
            )

else:

    st.info(
        "No admission history was found."
    )


# =========================================================
# CLINICAL SUMMARY
# =========================================================

st.markdown("---")

st.subheader("🧠 Clinical Summary")

risk_lower = str(risk_level).lower()

if "high" in risk_lower:

    summary = (
        "The AI model indicates a high risk of 30-day "
        "hospital readmission. Additional clinical "
        "monitoring and appropriate follow-up may be required."
    )

elif "moderate" in risk_lower:

    summary = (
        "The AI model indicates a moderate risk of 30-day "
        "hospital readmission. Additional clinical monitoring "
        "and follow-up may be appropriate."
    )

else:

    summary = (
        "The AI model indicates a lower risk of 30-day "
        "hospital readmission. Continue routine clinical "
        "monitoring and follow-up."
    )


st.info(summary)


# =========================================================
# RECOMMENDATIONS
# =========================================================

st.subheader("💡 Recommendations")

recommendations = [
    "Discuss the assessment with the treating doctor.",
    "Attend scheduled follow-up appointments.",
    "Continue regular health monitoring.",
    "Use clinical judgement when interpreting the AI prediction."
]

for item in recommendations:
    st.write(f"✅ {item}")


# =========================================================
# PDF GENERATION
# =========================================================

def generate_pdf():

    try:

        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.lib.enums import TA_CENTER
        from reportlab.platypus import (
            SimpleDocTemplate,
            Paragraph,
            Spacer,
            Table,
            TableStyle
        )

    except ImportError:

        return None, (
            "ReportLab is not installed. "
            "Add `reportlab` to requirements.txt."
        )

    import io

    buffer = io.BytesIO()

    doc = SimpleDocTemplate(
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
    normal_style = styles["BodyText"]

    story = []

    # -----------------------------------------------------
    # TITLE
    # -----------------------------------------------------

    story.append(
        Paragraph(
            "CAREWATCH-AI",
            title_style
        )
    )

    story.append(
        Paragraph(
            "AI-Based Clinical Decision Support System",
            styles["Heading3"]
        )
    )

    story.append(Spacer(1, 15))

    story.append(
        Paragraph(
            "Patient Clinical Report",
            styles["Heading2"]
        )
    )

    story.append(Spacer(1, 10))

    # -----------------------------------------------------
    # PATIENT
    # -----------------------------------------------------

    patient_table = [
        ["Patient ID", patient_id],
        [
            "Age",
            str(
                patient.get("age", "N/A")
                if patient is not None
                else "N/A"
            )
        ],
        [
            "Gender",
            str(
                patient.get("gender", "N/A")
                if patient is not None
                else "N/A"
            )
        ],
        [
            "State",
            str(
                patient.get("state", "N/A")
                if patient is not None
                else "N/A"
            )
        ]
    ]

    table = Table(
        patient_table,
        colWidths=[150, 330]
    )

    table.setStyle(
        TableStyle([
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("BACKGROUND", (0, 0), (0, -1), colors.lightgrey),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("PADDING", (0, 0), (-1, -1), 6)
        ])
    )

    story.append(table)

    story.append(Spacer(1, 20))

    # -----------------------------------------------------
    # PREDICTION
    # -----------------------------------------------------

    story.append(
        Paragraph(
            "AI Readmission Prediction",
            heading_style
        )
    )

    prediction_table = [
        ["Risk Level", str(risk_level)],
        ["Readmission Probability", probability_display],
        ["Prediction Date", str(prediction_date)]
    ]

    table = Table(
        prediction_table,
        colWidths=[180, 300]
    )

    table.setStyle(
        TableStyle([
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("BACKGROUND", (0, 0), (0, -1), colors.lightgrey),
            ("PADDING", (0, 0), (-1, -1), 6)
        ])
    )

    story.append(table)

    story.append(Spacer(1, 20))

    # -----------------------------------------------------
    # CLINICAL SUMMARY
    # -----------------------------------------------------

    story.append(
        Paragraph(
            "Clinical Summary",
            heading_style
        )
    )

    story.append(
        Paragraph(
            summary,
            normal_style
        )
    )

    story.append(Spacer(1, 15))

    # -----------------------------------------------------
    # RECOMMENDATIONS
    # -----------------------------------------------------

    story.append(
        Paragraph(
            "Recommendations",
            heading_style
        )
    )

    for recommendation in recommendations:

        story.append(
            Paragraph(
                "• " + recommendation,
                normal_style
            )
        )

        story.append(Spacer(1, 5))

    story.append(Spacer(1, 15))

    # -----------------------------------------------------
    # DISCLAIMER
    # -----------------------------------------------------

    story.append(
        Paragraph(
            "Clinical decisions should always be made by "
            "qualified healthcare professionals. "
            "The AI prediction is intended as clinical "
            "decision support and not as a replacement "
            "for professional medical judgement.",
            normal_style
        )
    )

    story.append(Spacer(1, 15))

    story.append(
        Paragraph(
            "Generated by CareWatch-AI",
            styles["Italic"]
        )
    )

    doc.build(story)

    buffer.seek(0)

    return buffer.getvalue(), None


# =========================================================
# DOWNLOAD PDF
# =========================================================

st.markdown("---")

st.subheader("📄 Download Patient Report")

if st.button(
    "Generate PDF Report",
    type="primary",
    use_container_width=True
):

    pdf_bytes, error = generate_pdf()

    if error:

        st.error(error)

    else:

        filename = (
            f"CareWatch-AI_Report_{patient_id}.pdf"
        )

        st.download_button(
            label="⬇️ Download PDF Report",
            data=pdf_bytes,
            file_name=filename,
            mime="application/pdf",
            use_container_width=True
        )

        st.success(
            "PDF report generated successfully."
        )