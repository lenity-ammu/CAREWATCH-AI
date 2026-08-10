import streamlit as st
import os
import pandas as pd
import json
from datetime import datetime

from auth import require_role, logout
from config.theme import apply_theme


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="CareWatch-AI | Doctor Dashboard",
    page_icon="👨‍⚕️",
    layout="wide"
)

apply_theme()


# =========================================================
# DOCTOR ACCESS
# =========================================================

require_role(["Doctor"])


# =========================================================
# SESSION
# =========================================================

username = st.session_state.get(
    "username",
    "Doctor"
)


# =========================================================
# HEADER
# =========================================================

col1, col2 = st.columns([5, 1])

with col1:

    st.title("🏥 CareWatch-AI")

    st.caption(
        "AI-Based Clinical Decision Support System"
    )

with col2:

    if st.button(
        "Logout",
        use_container_width=True
    ):
        logout()


st.divider()


# =========================================================
# DOCTOR WELCOME
# =========================================================

st.title("👨‍⚕️ Doctor Dashboard")

st.success(
    f"Welcome, Dr. {str(username).title()}!"
)

st.write(
    "View patient information and AI-based "
    "30-day hospital readmission risk assessments."
)


st.divider()


# =========================================================
# LOAD PREDICTION DATA
# =========================================================

result_file = "prediction_results.csv"


if not os.path.exists(result_file):

    st.warning(
        "No prediction data is currently available."
    )

    st.info(
        "Please generate a patient prediction "
        "from the Patient Readmission Prediction page."
    )

    st.stop()


# =========================================================
# READ PREDICTION CSV
# =========================================================

try:

    results = pd.read_csv(
        result_file
    )

except Exception as e:

    st.error(
        f"Unable to read prediction data: {e}"
    )

    st.stop()


# =========================================================
# CHECK PATIENT ID
# =========================================================

if "patient_id" not in results.columns:

    st.error(
        "patient_id column is missing from prediction_results.csv"
    )

    st.stop()


# =========================================================
# CLEAN PATIENT IDs
# =========================================================

results["patient_id"] = (
    results["patient_id"]
    .astype(str)
    .str.strip()
)


# =========================================================
# REMOVE EMPTY IDs
# =========================================================

results = results[
    results["patient_id"].notna()
]

results = results[
    results["patient_id"] != ""
]


if results.empty:

    st.info(
        "No patient prediction records are available."
    )

    st.stop()


# =========================================================
# PATIENT SELECTION
# =========================================================

st.header("👥 Patient Selection")

patient_ids = sorted(
    results["patient_id"]
    .unique()
    .tolist()
)


selected_patient = st.selectbox(
    "Select Patient",
    patient_ids
)


# =========================================================
# SELECT PATIENT
# =========================================================

patient_rows = results[
    results["patient_id"]
    == selected_patient
]


if patient_rows.empty:

    st.warning(
        "No information found for this patient."
    )

    st.stop()


# =========================================================
# LATEST PREDICTION
# =========================================================

patient = patient_rows.iloc[-1]


# =========================================================
# PATIENT INFORMATION
# =========================================================

st.divider()

st.header(
    "👤 Patient Information"
)


c1, c2, c3, c4 = st.columns(4)


with c1:

    st.metric(
        "Patient ID",
        selected_patient
    )


with c2:

    st.metric(
        "Age",
        str(
            patient.get(
                "age",
                "N/A"
            )
        )
    )


with c3:

    st.metric(
        "Gender",
        str(
            patient.get(
                "gender",
                "N/A"
            )
        )
    )


with c4:

    st.metric(
        "State",
        str(
            patient.get(
                "state",
                "N/A"
            )
        )
    )


# =========================================================
# CLINICAL INFORMATION
# =========================================================

st.subheader(
    "🩺 Clinical Information"
)


c1, c2, c3 = st.columns(3)


with c1:

    st.info(
        f"**Primary Diagnosis:** "
        f"{patient.get('primary_diagnosis', 'N/A')}"
    )


with c2:

    st.info(
        f"**Disease Category:** "
        f"{patient.get('primary_category', 'N/A')}"
    )


with c3:

    st.info(
        f"**Charlson Index:** "
        f"{patient.get('charlson_index', 'N/A')}"
    )


c1, c2, c3 = st.columns(3)


with c1:

    st.info(
        f"**Comorbidity Count:** "
        f"{patient.get('comorbidity_count', 'N/A')}"
    )


with c2:

    st.info(
        f"**Previous Admissions:** "
        f"{patient.get('previous_admissions', 'N/A')}"
    )


with c3:

    st.info(
        f"**Admission Type:** "
        f"{patient.get('admission_type', 'N/A')}"
    )


# =========================================================
# RISK ASSESSMENT
# =========================================================

st.divider()

st.header(
    "🤖 AI Readmission Risk Assessment"
)


risk_level = str(
    patient.get(
        "risk_level",
        "Unknown"
    )
)


try:

    probability = float(
        patient.get(
            "risk_probability",
            0
        )
    )

except Exception:

    probability = 0.0


# =========================================================
# RISK DISPLAY
# =========================================================

if risk_level.lower() == "high":

    st.error(
        "🔴 HIGH RISK OF 30-DAY READMISSION"
    )

elif risk_level.lower() == "moderate":

    st.warning(
        "🟡 MODERATE RISK OF 30-DAY READMISSION"
    )

else:

    st.success(
        "🟢 LOW RISK OF 30-DAY READMISSION"
    )


st.metric(
    "Readmission Probability",
    f"{probability * 100:.2f}%"
)


# =========================================================
# CLINICAL SUMMARY
# =========================================================

st.subheader(
    "🧠 Clinical Summary"
)


summary = patient.get(
    "clinical_summary",
    "No clinical summary available."
)


st.info(
    str(summary)
)


# =========================================================
# ADDITIONAL DETAILS
# =========================================================

st.divider()

st.header(
    "📋 Additional Patient Details"
)


columns_to_show = [

    "los_days",
    "ward_type",
    "discharge_type",
    "num_procedures",
    "hba1c",
    "creatinine",
    "haemoglobin",
    "systolic_bp",
    "insurance_type",
    "total_cost_inr",
    "govt_subsidy_inr",
    "out_of_pocket_inr",
    "cost_category",
    "tier",
    "beds",
    "teaching"

]


details = {}


for column in columns_to_show:

    if column in patient.index:

        details[column] = patient[column]


if details:

    detail_df = pd.DataFrame(
        {
            "Feature":
                list(details.keys()),

            "Value":
                list(details.values())
        }
    )


    st.dataframe(
        detail_df,
        use_container_width=True,
        hide_index=True
    )

else:

    st.info(
        "No additional patient details available."
    )


# =========================================================
# PREDICTION HISTORY
# =========================================================

st.divider()

st.header(
    "📈 Prediction History"
)


history = patient_rows.copy()


if len(history) > 1:

    display_columns = [

        column

        for column in [

            "patient_id",
            "risk_level",
            "risk_probability",
            "clinical_summary"

        ]

        if column in history.columns

    ]


    history_display = history[
        display_columns
    ].copy()


    if "risk_probability" in history_display.columns:

        history_display[
            "risk_probability"
        ] = (

            history_display[
                "risk_probability"
            ].astype(float)

            * 100

        ).round(2)


        history_display = (
            history_display.rename(
                columns={
                    "risk_probability":
                    "Risk Probability (%)"
                }
            )
        )


    st.dataframe(
        history_display,
        use_container_width=True,
        hide_index=True
    )

else:

    st.info(
        "This patient has only one prediction."
    )


# =========================================================
# PATIENT REPORT
# =========================================================

st.divider()

st.header(
    "📄 Patient Report"
)


st.write(
    "Generate and save a clinical risk report "
    "for the selected patient."
)


# =========================================================
# REPORT RECOMMENDATIONS
# =========================================================

if risk_level.lower() == "high":

    recommendations = [

        "Discuss the readmission risk assessment with the patient.",

        "Arrange appropriate follow-up care.",

        "Continue close monitoring of the patient's condition."

    ]

elif risk_level.lower() == "moderate":

    recommendations = [

        "Review the patient's risk factors.",

        "Ensure scheduled follow-up appointments.",

        "Continue regular health monitoring."

    ]

else:

    recommendations = [

        "Continue following the healthcare plan.",

        "Attend scheduled follow-up appointments.",

        "Maintain regular health monitoring."

    ]


# =========================================================
# REPORT PREVIEW
# =========================================================

with st.expander(
    "👁️ Preview Report"
):

    st.write(
        f"**Patient ID:** {selected_patient}"
    )

    st.write(
        f"**Risk Level:** {risk_level}"
    )

    st.write(
        f"**Readmission Probability:** "
        f"{probability * 100:.2f}%"
    )

    st.write(
        f"**Clinical Summary:** {summary}"
    )

    st.write(
        "**Recommendations:**"
    )

    for recommendation in recommendations:

        st.write(
            f"✅ {recommendation}"
        )


# =========================================================
# GENERATE REPORT
# =========================================================

if st.button(
    "📄 Generate & Save Patient Report",
    use_container_width=True
):

    report_file = "patient_reports.json"


    # -----------------------------------------------------
    # LOAD EXISTING REPORTS
    # -----------------------------------------------------

    if os.path.exists(report_file):

        try:

            with open(
                report_file,
                "r",
                encoding="utf-8"
            ) as f:

                all_reports = json.load(f)

        except Exception:

            all_reports = {}

    else:

        all_reports = {}


    # -----------------------------------------------------
    # CREATE REPORT
    # -----------------------------------------------------

    report = {

        "patient_id":
            selected_patient,

        "generated_at":
            datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            ),

        "risk_level":
            risk_level,

        "probability":
            probability,

        "clinical_summary":
            str(summary),

        "recommendations":
            recommendations

    }


    # -----------------------------------------------------
    # SAVE REPORT
    # -----------------------------------------------------

    all_reports[
        str(selected_patient)
    ] = report


    with open(
        report_file,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            all_reports,
            f,
            indent=4,
            ensure_ascii=False
        )


    st.success(
        "✅ Patient report generated and saved successfully."
    )


# =========================================================
# DOCTOR NOTICE
# =========================================================

st.divider()

st.warning(
    "⚠️ AI predictions are clinical decision-support "
    "information only. The final clinical decision "
    "must be made by a qualified healthcare professional."
)