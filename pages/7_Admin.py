import streamlit as st
import os
import pandas as pd

from auth import require_role, logout
from config.theme import apply_theme

# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="CareWatch-AI | Analytics",
    page_icon="📊",
    layout="wide"
)

apply_theme()

# ============================================================
# ACCESS CONTROL
# ============================================================

require_role(["Admin"])

# ============================================================
# SESSION
# ============================================================

username = st.session_state.get(
    "username",
    "Admin"
)

# ============================================================
# HEADER
# ============================================================

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

st.title("📊 Admin Analytics Dashboard")

st.success(
    f"Welcome, {username.title()}!"
)

st.write(
    "Monitor patient risk, readmission predictions "
    "and healthcare analytics."
)

st.divider()

# ============================================================
# LOAD DATA
# ============================================================

result_file = "prediction_results.csv"

if not os.path.exists(result_file):

    st.warning(
        "No prediction data is available yet."
    )

    st.info(
        "Generate patient predictions first "
        "to populate the analytics dashboard."
    )

    st.stop()

# ============================================================
# READ CSV
# ============================================================

try:

    results = pd.read_csv(
        result_file
    )

except Exception as e:

    st.error(
        f"Unable to read prediction data: {e}"
    )

    st.stop()

# ============================================================
# CHECK REQUIRED COLUMN
# ============================================================

if "patient_id" not in results.columns:

    st.error(
        "patient_id column is missing "
        "from prediction_results.csv"
    )

    st.stop()

# ============================================================
# CLEAN DATA
# ============================================================

results["patient_id"] = (
    results["patient_id"]
    .astype(str)
    .str.strip()
)

# ============================================================
# RISK LEVEL CLEANING
# ============================================================

if "risk_level" in results.columns:

    results["risk_level"] = (
        results["risk_level"]
        .astype(str)
        .str.strip()
        .str.title()
    )

# ============================================================
# RISK PROBABILITY
# ============================================================

if "risk_probability" in results.columns:

    results["risk_probability"] = pd.to_numeric(
        results["risk_probability"],
        errors="coerce"
    )

# ============================================================
# USE LATEST PREDICTION PER PATIENT
# ============================================================

latest_results = (
    results
    .groupby(
        "patient_id",
        as_index=False
    )
    .tail(1)
    .reset_index(drop=True)
)

# ============================================================
# BASIC COUNTS
# ============================================================

total_patients = (
    latest_results["patient_id"]
    .nunique()
)

high_risk = 0
moderate_risk = 0
low_risk = 0

if "risk_level" in latest_results.columns:

    high_risk = (
        latest_results["risk_level"]
        .str.lower()
        .eq("high")
        .sum()
    )

    moderate_risk = (
        latest_results["risk_level"]
        .str.lower()
        .eq("moderate")
        .sum()
    )

    low_risk = (
        latest_results["risk_level"]
        .str.lower()
        .eq("low")
        .sum()
    )

# ============================================================
# AVERAGE PROBABILITY
# ============================================================

average_probability = 0.0

if "risk_probability" in latest_results.columns:

    average_probability = (
        latest_results["risk_probability"]
        .mean()
    )

    if pd.isna(average_probability):

        average_probability = 0.0

# ============================================================
# DASHBOARD METRICS
# ============================================================

st.header("📌 Key Healthcare Metrics")

c1, c2, c3, c4, c5 = st.columns(5)

with c1:

    st.metric(
        "👥 Total Patients",
        total_patients
    )

with c2:

    st.metric(
        "🔴 High Risk",
        high_risk
    )

with c3:

    st.metric(
        "🟡 Moderate Risk",
        moderate_risk
    )

with c4:

    st.metric(
        "🟢 Low Risk",
        low_risk
    )

with c5:

    st.metric(
        "📊 Avg Readmission Risk",
        f"{average_probability * 100:.2f}%"
    )

st.divider()

# ============================================================
# RISK DISTRIBUTION
# ============================================================

st.header("📊 Risk Distribution")

if "risk_level" in latest_results.columns:

    risk_counts = (
        latest_results["risk_level"]
        .value_counts()
    )

    risk_chart = pd.DataFrame(
        {
            "Risk Level": risk_counts.index,
            "Patients": risk_counts.values
        }
    )

    st.bar_chart(
        risk_chart.set_index(
            "Risk Level"
        )
    )

else:

    st.info(
        "Risk-level data is not available."
    )

st.divider()

# ============================================================
# DIAGNOSIS DISTRIBUTION
# ============================================================

st.header("🩺 Diagnosis Distribution")

if "primary_diagnosis" in latest_results.columns:

    diagnosis_counts = (
        latest_results[
            "primary_diagnosis"
        ]
        .fillna("Not specified")
        .astype(str)
        .value_counts()
        .head(10)
    )

    diagnosis_chart = pd.DataFrame(
        {
            "Diagnosis": diagnosis_counts.index,
            "Patients": diagnosis_counts.values
        }
    )

    st.bar_chart(
        diagnosis_chart.set_index(
            "Diagnosis"
        )
    )

else:

    st.info(
        "Diagnosis data is not available."
    )

st.divider()

# ============================================================
# STATE DISTRIBUTION
# ============================================================

st.header("📍 Patient Distribution by State")

if "state" in latest_results.columns:

    state_counts = (
        latest_results["state"]
        .fillna("Not specified")
        .astype(str)
        .value_counts()
    )

    state_chart = pd.DataFrame(
        {
            "State": state_counts.index,
            "Patients": state_counts.values
        }
    )

    st.bar_chart(
        state_chart.set_index(
            "State"
        )
    )

else:

    st.info(
        "State information is not available."
    )

st.divider()

# ============================================================
# RISK PROBABILITY DISTRIBUTION
# ============================================================

st.header("📈 Readmission Probability")

if "risk_probability" in latest_results.columns:

    probability_data = (
        latest_results[
            [
                "patient_id",
                "risk_probability"
            ]
        ]
        .copy()
    )

    probability_data[
        "risk_probability"
    ] = (
        probability_data[
            "risk_probability"
        ] * 100
    ).round(2)

    probability_data = (
        probability_data
        .sort_values(
            "risk_probability",
            ascending=False
        )
        .head(20)
    )

    probability_data = (
        probability_data
        .set_index("patient_id")
    )

    st.bar_chart(
        probability_data[
            "risk_probability"
        ]
    )

else:

    st.info(
        "Readmission probability data "
        "is not available."
    )

st.divider()

# ============================================================
# HIGH-RISK PATIENTS
# ============================================================

st.header("🔴 High-Risk Patients")

if "risk_level" in latest_results.columns:

    high_risk_patients = latest_results[
        latest_results["risk_level"]
        .str.lower()
        .eq("high")
    ].copy()

    if not high_risk_patients.empty:

        columns_to_show = [
            "patient_id",
            "age",
            "gender",
            "state",
            "risk_level",
            "risk_probability",
            "primary_diagnosis"
        ]

        available_columns = [
            column
            for column in columns_to_show
            if column in high_risk_patients.columns
        ]

        high_display = (
            high_risk_patients[
                available_columns
            ]
            .copy()
        )

        if "risk_probability" in high_display.columns:

            high_display[
                "risk_probability"
            ] = (
                high_display[
                    "risk_probability"
                ] * 100
            ).round(2)

            high_display = (
                high_display
                .rename(
                    columns={
                        "risk_probability":
                        "Readmission Risk (%)"
                    }
                )
            )

        st.dataframe(
            high_display,
            use_container_width=True,
            hide_index=True
        )

    else:

        st.success(
            "No high-risk patients currently identified."
        )

else:

    st.info(
        "Risk-level information is unavailable."
    )

st.divider()

# ============================================================
# COMPLETE PATIENT TABLE
# ============================================================

st.header("📋 Patient Risk Overview")

columns_to_show = [
    "patient_id",
    "age",
    "gender",
    "state",
    "risk_level",
    "risk_probability",
    "primary_diagnosis",
    "primary_category",
    "charlson_index",
    "previous_admissions"
]

available_columns = [
    column
    for column in columns_to_show
    if column in latest_results.columns
]

overview = (
    latest_results[
        available_columns
    ]
    .copy()
)

if "risk_probability" in overview.columns:

    overview[
        "risk_probability"
    ] = (
        overview[
            "risk_probability"
        ] * 100
    ).round(2)

    overview = overview.rename(
        columns={
            "risk_probability":
            "Readmission Risk (%)"
        }
    )

st.dataframe(
    overview,
    use_container_width=True,
    hide_index=True
)

st.divider()

# ============================================================
# DATASET SUMMARY
# ============================================================

st.header("📄 Dataset Summary")

c1, c2, c3 = st.columns(3)

with c1:

    st.metric(
        "Prediction Records",
        len(results)
    )

with c2:

    st.metric(
        "Unique Patients",
        total_patients
    )

with c3:

    st.metric(
        "Available States",
        (
            latest_results["state"]
            .nunique()
            if "state"
            in latest_results.columns
            else 0
        )
    )

# ============================================================
# ADMIN NOTICE
# ============================================================

st.divider()

st.warning(
    "⚠️ Analytics are generated from the available "
    "prediction data. These statistics are intended "
    "for healthcare system monitoring and decision "
    "support and should not be interpreted as "
    "independent clinical decisions."
)