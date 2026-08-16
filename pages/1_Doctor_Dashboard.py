import streamlit as st
import pandas as pd
import os

from auth import require_role, logout


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="CareWatch-AI | Doctor Dashboard",
    page_icon="🩺",
    layout="wide"
)

require_role(["Doctor"])


# =========================================================
# PATH
# =========================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)


# =========================================================
# LOAD DATA
# =========================================================

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
admissions = load_csv("admissions.csv")
predictions = load_csv("prediction_results.csv")


# =========================================================
# NORMALIZE DATA
# =========================================================

if not patients.empty and "patient_id" in patients.columns:
    patients["patient_id"] = (
        patients["patient_id"]
        .astype(str)
        .str.strip()
    )

if not admissions.empty and "patient_id" in admissions.columns:
    admissions["patient_id"] = (
        admissions["patient_id"]
        .astype(str)
        .str.strip()
    )


# =========================================================
# HEADER
# =========================================================

header_col, logout_col = st.columns([6, 1])

with header_col:

    st.title("🩺 Doctor Dashboard")

    st.caption(
        "CareWatch-AI | Clinical Decision Support System"
    )

with logout_col:

    if st.button(
        "🚪 Logout",
        use_container_width=True
    ):

        logout()
        st.rerun()


st.markdown("---")


# =========================================================
# WELCOME
# =========================================================

doctor_name = st.session_state.get(
    "name",
    "Dr. CareWatch"
)

st.success(
    f"Welcome, {doctor_name}"
)


# =========================================================
# CLINICAL OVERVIEW
# =========================================================

st.header("📊 Clinical Overview")


patient_count = 0

if (
    not patients.empty
    and "patient_id" in patients.columns
):

    patient_count = patients[
        "patient_id"
    ].nunique()


admission_count = (
    len(admissions)
    if not admissions.empty
    else 0
)


high_count=moderate_count=low_count=0

if not predictions.empty and "risk_level" in predictions.columns:
    risk=predictions["risk_level"].astype(str).str.strip().str.lower()
    high_count=int(risk.str.contains("high",na=False).sum())
    moderate_count=int(risk.str.contains("moderate",na=False).sum())
    low_count=int(risk.str.contains("low",na=False).sum())


c1, c2, c3, c4, c5 = st.columns(5)

with c1:

    st.metric(
        "👥 Patients",
        f"{patient_count:,}"
    )

with c2:

    st.metric(
        "🏥 Admissions",
        f"{admission_count:,}"
    )

with c3:

    st.metric(
        "🔴 High Risk",
        high_count
    )

with c4:

    st.metric(
        "🟠 Moderate Risk",
        moderate_count
    )

with c5:

    st.metric(
        "🟢 Low Risk",
        low_count
    )


# =========================================================
# MAIN CLINICAL MODULES
# =========================================================

st.markdown("---")

st.header("⚡ Clinical Modules")


# ---------------------------------------------------------
# ROW 1
# ---------------------------------------------------------

col1, col2 = st.columns(2)

with col1:

    st.subheader("🧠 AI Prediction")

    st.write(
        "Run the 30-day hospital readmission "
        "risk prediction for a patient."
    )

    st.page_link(
        "pages/3_Prediction.py",
        label="🧠 Open AI Prediction",
        use_container_width=True
    )


with col2:

    st.subheader("📋 Electronic Health Record")

    st.write(
        "Review patient profile, admissions, "
        "diagnoses, billing and hospital information."
    )

    st.page_link(
        "pages/11_EHR.py",
        label="📋 Open EHR",
        use_container_width=True
    )


# ---------------------------------------------------------
# ROW 2
# ---------------------------------------------------------

st.write("")

col3, col4 = st.columns(2)

with col3:

    st.subheader("🔬 Explainable AI")

    st.write(
        "Understand the clinical and administrative "
        "factors influencing the AI prediction."
    )

    st.page_link(
        "pages/4_SHAP_Explainability.py",
        label="🔬 Open SHAP / XAI",
        use_container_width=True
    )


with col4:

    st.subheader("🔗 Blockchain Audit")

    st.write(
        "Verify the integrity of prediction and "
        "clinical audit records."
    )

    st.page_link(
        "pages/12_Blockchain.py",
        label="🔗 Open Blockchain Audit",
        use_container_width=True
    )


# =========================================================
# RECENT PREDICTIONS
# =========================================================

st.markdown("---")

st.header("🧠 Recent AI Predictions")


if predictions.empty:

    st.info(
        "No prediction records are available yet."
    )

else:

    recent = predictions.copy()

    display_columns = [
        "patient_id",
        "risk_level",
        "risk_probability",
        "timestamp"
    ]

    display_columns = [
        column
        for column in display_columns
        if column in recent.columns
    ]

    recent = recent[display_columns].copy()


    # -----------------------------------------------------
    # SORT BY TIME
    # -----------------------------------------------------

    if "timestamp" in recent.columns:

        recent["_sort_time"] = pd.to_datetime(
            recent["timestamp"],
            errors="coerce"
        )

        recent = recent.sort_values(
            "_sort_time",
            ascending=False
        )

        recent = recent.drop(
            columns=["_sort_time"]
        )


    # -----------------------------------------------------
    # FORMAT PROBABILITY
    # -----------------------------------------------------

    if "risk_probability" in recent.columns:

        probability = pd.to_numeric(
            recent["risk_probability"],
            errors="coerce"
        )

        valid = probability.dropna()

        if (
            not valid.empty
            and valid.max() <= 1
        ):

            probability = probability * 100

        recent["risk_probability"] = (
            probability.round(2).astype(str)
            + "%"
        )


    # -----------------------------------------------------
    # SHOW TABLE
    # -----------------------------------------------------

    st.dataframe(
        recent.head(10),
        use_container_width=True,
        hide_index=True
    )


# =========================================================
# CLINICAL WORKFLOW
# =========================================================

st.markdown("---")

st.header("🔄 Clinical Workflow")

st.markdown(
    """
**1️⃣ Patient Selection**

Doctor selects a patient from the AI Prediction module.

↓

**2️⃣ EHR Review**

Doctor reviews the patient's demographic, admission,
diagnosis, billing and hospital information.

↓

**3️⃣ AI Prediction**

CareWatch-AI calculates the probability of
30-day hospital readmission.

↓

**4️⃣ Risk Classification**

The system classifies the patient as:

🔴 **High Risk**  
🟠 **Moderate Risk**  
🟢 **Low Risk**

↓

**5️⃣ Explainable AI**

SHAP/XAI explains the important factors contributing
to the prediction.

↓

**6️⃣ Blockchain Audit**

The prediction is recorded in the blockchain audit
ledger and its integrity is verified.

↓

**7️⃣ EHR / Report**

The patient's clinical record and prediction can be
reviewed through the EHR and report workflow.
"""
)


# =========================================================
# SECURITY
# =========================================================

st.markdown("---")

st.info(
    "🔒 Clinical information is available only to authorized healthcare users."
)

st.caption(
    "CareWatch-AI | Doctor Portal | "
    "Clinical decisions should always be made by qualified healthcare professionals."
)
