import streamlit as st
import spacy
import re
import os
import pandas as pd

from auth import require_role

# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="CareWatch-AI | AI Clinical Assistant",
    page_icon="🧠",
    layout="wide"
)

# ============================================================
# ACCESS CONTROL
# ============================================================

require_role(["Doctor"])

# ============================================================
# NLP MODEL
# ============================================================

@st.cache_resource
def load_nlp_model():

    nlp = spacy.blank("en")

    if "sentencizer" not in nlp.pipe_names:
        nlp.add_pipe("sentencizer")

    return nlp


nlp = load_nlp_model()

# ============================================================
# PAGE TITLE
# ============================================================

st.title("🧠 AI Clinical Assistant")

st.write(
    "Analyze clinical notes to identify documented medical "
    "conditions, readmission risk factors and generate "
    "follow-up recommendations."
)

st.info(
    "⚠️ This assistant provides rule-based clinical "
    "decision-support information only. It does not replace "
    "professional medical judgment."
)

st.divider()

# ============================================================
# LOAD PATIENT DATA
# ============================================================

result_file = "prediction_results.csv"

if not os.path.exists(result_file):

    st.warning(
        "No patient prediction data is available yet."
    )

    st.info(
        "Please generate a patient prediction first."
    )

    st.stop()

# ============================================================
# READ CSV
# ============================================================

try:

    results = pd.read_csv(result_file)

except Exception as e:

    st.error(
        f"Unable to read patient data: {e}"
    )

    st.stop()

# ============================================================
# CHECK PATIENT ID
# ============================================================

if "patient_id" not in results.columns:

    st.error(
        "patient_id column is missing from "
        "prediction_results.csv"
    )

    st.stop()

# Clean patient IDs

results["patient_id"] = (
    results["patient_id"]
    .astype(str)
    .str.strip()
)

# ============================================================
# PATIENT SELECTION
# ============================================================

st.header("👤 Patient Selection")

patient_ids = sorted(
    results["patient_id"]
    .unique()
    .tolist()
)

if not patient_ids:

    st.info(
        "No patients are available."
    )

    st.stop()

selected_patient = st.selectbox(
    "Select Patient",
    patient_ids
)

# ============================================================
# GET SELECTED PATIENT
# ============================================================

patient_rows = results[
    results["patient_id"] == selected_patient
]

if patient_rows.empty:

    st.warning(
        "No data found for the selected patient."
    )

    st.stop()

# Latest prediction

patient = patient_rows.iloc[-1]

st.divider()

# ============================================================
# PATIENT INFORMATION
# ============================================================

st.header("👤 Selected Patient")

c1, c2, c3, c4 = st.columns(4)

with c1:

    st.metric(
        "Patient ID",
        selected_patient
    )

with c2:

    st.metric(
        "Age",
        str(patient.get("age", "N/A"))
    )

with c3:

    st.metric(
        "Gender",
        str(patient.get("gender", "N/A"))
    )

with c4:

    st.metric(
        "Risk Level",
        str(patient.get("risk_level", "N/A"))
    )

# ============================================================
# BASIC CLINICAL INFORMATION
# ============================================================

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
        f"**Previous Admissions:** "
        f"{patient.get('previous_admissions', 'N/A')}"
    )

st.divider()

# ============================================================
# DEFAULT CLINICAL NOTES
# ============================================================

diagnosis = str(
    patient.get(
        "primary_diagnosis",
        ""
    )
)

category = str(
    patient.get(
        "primary_category",
        ""
    )
)

comorbidity = str(
    patient.get(
        "comorbidity_count",
        ""
    )
)

previous_admissions = str(
    patient.get(
        "previous_admissions",
        ""
    )
)

existing_summary = str(
    patient.get(
        "clinical_summary",
        ""
    )
)

default_notes = f"""
Primary diagnosis: {diagnosis}.
Disease category: {category}.
Comorbidity count: {comorbidity}.
Previous admissions: {previous_admissions}.
Previous AI clinical summary: {existing_summary}
"""

# ============================================================
# CLINICAL NOTES
# ============================================================

st.header("📝 Clinical Notes")

st.write(
    "Review or edit the clinical notes before analysis."
)

notes = st.text_area(
    "Enter Clinical Notes",
    value=default_notes.strip(),
    height=250,
    placeholder="""
Example:

Patient has uncontrolled diabetes.

Known CKD stage III.

Previous admission due to heart failure.

HbA1c remains elevated.

Poor medication adherence.

Complains of shortness of breath.
"""
)

analyze = st.button(
    "🔍 Analyze Clinical Notes",
    use_container_width=True
)

# ============================================================
# MEDICAL KNOWLEDGE DATABASE
# ============================================================

MEDICAL_DB = {

    "Diabetes": {

        "keywords": [
            "diabetes",
            "diabetic",
            "glucose",
            "hba1c",
            "hyperglycemia"
        ],

        "recommendations": [
            "Monitor HbA1c and blood glucose regularly.",
            "Review diabetes medication adherence.",
            "Provide appropriate diabetic diet counselling."
        ]
    },

    "Chronic Kidney Disease": {

        "keywords": [
            "ckd",
            "chronic kidney disease",
            "kidney disease",
            "renal disease",
            "renal",
            "creatinine"
        ],

        "recommendations": [
            "Monitor renal function and serum creatinine.",
            "Consider nephrology follow-up.",
            "Review medications for renal safety."
        ]
    },

    "Heart Failure": {

        "keywords": [
            "heart failure",
            "cardiac failure",
            "congestive heart failure"
        ],

        "recommendations": [
            "Schedule cardiology follow-up.",
            "Monitor weight and fluid status.",
            "Review heart-failure medication adherence."
        ]
    },

    "Hypertension": {

        "keywords": [
            "hypertension",
            "high blood pressure",
            "blood pressure"
        ],

        "recommendations": [
            "Monitor blood pressure regularly.",
            "Review antihypertensive medication adherence."
        ]
    },

    "COPD": {

        "keywords": [
            "copd",
            "chronic obstructive pulmonary disease",
            "chronic obstructive"
        ],

        "recommendations": [
            "Monitor oxygen saturation.",
            "Review inhaler compliance.",
            "Consider pulmonary follow-up."
        ]
    },

    "Pneumonia": {

        "keywords": [
            "pneumonia",
            "lung infection"
        ],

        "recommendations": [
            "Review treatment response.",
            "Monitor respiratory status."
        ]
    },

    "Sepsis": {

        "keywords": [
            "sepsis",
            "septic"
        ],

        "recommendations": [
            "Monitor vital signs and infection markers.",
            "Review response to antimicrobial treatment."
        ]
    }
}

# ============================================================
# CONDITION DETECTION
# ============================================================

def detect_conditions(text):

    text = text.lower()

    detected = []
    recommendations = []

    doc = nlp(text)

    clean_text = " ".join(
        token.text
        for token in doc
    )

    for disease, info in MEDICAL_DB.items():

        for keyword in info["keywords"]:

            if keyword in clean_text:

                if disease not in detected:

                    detected.append(disease)

                    recommendations.extend(
                        info["recommendations"]
                    )

                break

    return detected, recommendations


# ============================================================
# RISK DETECTION
# ============================================================

def detect_risk(text):

    text = text.lower()

    risk_factors = []

    # Previous admission

    if (
        "previous admission" in text
        or "previous admissions" in text
        or "previously admitted" in text
        or "past admission" in text
    ):

        risk_factors.append(
            "Previous Hospital Admission"
        )

    # Medication adherence

    if (
        "poor medication adherence" in text
        or "non adherence" in text
        or "non-adherence" in text
        or "medication noncompliance" in text
        or "poor compliance" in text
    ):

        risk_factors.append(
            "Poor Medication Adherence"
        )

    # Diabetes / HbA1c

    if (
        "hba1c" in text
        or "uncontrolled diabetes" in text
        or "poorly controlled diabetes" in text
    ):

        risk_factors.append(
            "Diabetes / Elevated HbA1c"
        )

    # CKD

    if (
        "ckd" in text
        or "chronic kidney disease" in text
        or "renal disease" in text
    ):

        risk_factors.append(
            "Chronic Kidney Disease"
        )

    # Heart failure

    if (
        "heart failure" in text
        or "cardiac failure" in text
    ):

        risk_factors.append(
            "Heart Failure"
        )

    # Sepsis

    if (
        "sepsis" in text
        or "septic" in text
    ):

        risk_factors.append(
            "Sepsis"
        )

    # Shortness of breath

    if (
        "shortness of breath" in text
        or "breathlessness" in text
        or "dyspnea" in text
    ):

        risk_factors.append(
            "Respiratory Symptoms"
        )

    return risk_factors


# ============================================================
# ANALYSIS
# ============================================================

if analyze:

    if not notes.strip():

        st.warning(
            "Please enter clinical notes before analysis."
        )

    else:

        # ====================================================
        # RUN ANALYSIS
        # ====================================================

        conditions, recommendations = (
            detect_conditions(notes)
        )

        risk = detect_risk(notes)

        # ====================================================
        # TEXT STATISTICS
        # ====================================================

        doc = nlp(notes)

        num_tokens = len(doc)

        num_sentences = len(
            [
                sentence
                for sentence in re.split(
                    r"[.!?]+",
                    notes
                )
                if sentence.strip()
            ]
        )

        num_words = len(
            [
                token
                for token in doc
                if token.is_alpha
            ]
        )

        # ====================================================
        # RISK SCORE
        # ====================================================

        risk_score = (
            len(conditions)
            + len(risk)
        )

        # ====================================================
        # RISK LEVEL
        # ====================================================

        if risk_score >= 6:

            risk_level = "High"

        elif risk_score >= 3:

            risk_level = "Moderate"

        else:

            risk_level = "Low"

        # ====================================================
        # RESULTS HEADER
        # ====================================================

        st.markdown("---")

        st.header("📊 Clinical Analysis Results")

        # ====================================================
        # TEXT STATISTICS
        # ====================================================

        st.subheader(
            "📊 Clinical Note Statistics"
        )

        c1, c2, c3 = st.columns(3)

        with c1:

            st.metric(
                "Words",
                num_words
            )

        with c2:

            st.metric(
                "Sentences",
                num_sentences
            )

        with c3:

            st.metric(
                "Tokens",
                num_tokens
            )

        # ====================================================
        # CONDITIONS + RISK FACTORS
        # ====================================================

        st.markdown("---")

        col1, col2 = st.columns(2)

        # ----------------------------------------------------
        # CONDITIONS
        # ----------------------------------------------------

        with col1:

            st.subheader(
                "🩺 Detected Medical Conditions"
            )

            if conditions:

                for condition in conditions:

                    st.success(
                        f"✅ {condition}"
                    )

            else:

                st.info(
                    "No medical conditions detected."
                )

        # ----------------------------------------------------
        # RISK FACTORS
        # ----------------------------------------------------

        with col2:

            st.subheader(
                "⚠️ Readmission Risk Factors"
            )

            if risk:

                for factor in risk:

                    st.error(
                        f"⚠️ {factor}"
                    )

            else:

                st.success(
                    "No major risk factors detected."
                )

        # ====================================================
        # RECOMMENDATIONS
        # ====================================================

        st.markdown("---")

        st.subheader(
            "🤖 AI Recommendations"
        )

        unique_recommendations = sorted(
            set(recommendations)
        )

        if unique_recommendations:

            for recommendation in unique_recommendations:

                st.info(
                    "✅ " + recommendation
                )

        else:

            st.info(
                "No specific recommendations generated."
            )

        # ====================================================
        # RISK ASSESSMENT
        # ====================================================

        st.markdown("---")

        st.subheader(
            "📊 AI Clinical Risk Assessment"
        )

        if risk_level == "High":

            st.error(
                "🔴 HIGH RISK"
            )

        elif risk_level == "Moderate":

            st.warning(
                "🟡 MODERATE RISK"
            )

        else:

            st.success(
                "🟢 LOW RISK"
            )

        # Risk score progress

        risk_progress = min(
            risk_score / 8,
            1.0
        )

        st.progress(
            risk_progress
        )

        st.caption(
            f"Risk factor score: "
            f"{risk_score}"
        )

        # ====================================================
        # AI CLINICAL SUMMARY
        # ====================================================

        st.markdown("---")

        st.subheader(
            "🧠 AI Clinical Summary"
        )

        if conditions:

            summary = (
                "The clinical notes indicate "
                f"{', '.join(conditions)}. "
            )

            if risk:

                summary += (
                    "Important documented readmission "
                    "risk factors include "
                    f"{', '.join(risk)}. "
                )

            summary += (
                "The rule-based clinical assessment "
                f"classifies the documented risk as "
                f"{risk_level.lower()}. "
            )

            summary += (
                "Clinical findings should be reviewed "
                "by the treating healthcare professional."
            )

        else:

            summary = (
                "No major conditions were identified "
                "from the supplied clinical notes. "
                "The findings should still be reviewed "
                "by the treating healthcare professional."
            )

        st.success(
            summary
        )

        # ====================================================
        # PATIENT'S EXISTING MODEL RESULT
        # ====================================================

        st.markdown("---")

        st.subheader(
            "📈 Existing Readmission Prediction"
        )

        existing_risk = str(
            patient.get(
                "risk_level",
                "N/A"
            )
        )

        try:

            existing_probability = float(
                patient.get(
                    "risk_probability",
                    0
                )
            )

        except Exception:

            existing_probability = 0.0

        c1, c2 = st.columns(2)

        with c1:

            st.metric(
                "Model Risk Level",
                existing_risk
            )

        with c2:

            st.metric(
                "Model Readmission Probability",
                f"{existing_probability * 100:.2f}%"
            )

        st.caption(
            "The readmission prediction above comes from "
            "the existing prediction model. The clinical "
            "assistant analysis is a separate rule-based "
            "assessment of the supplied clinical notes."
        )

# ============================================================
# DOCTOR NOTICE
# ============================================================

st.divider()

st.warning(
    "⚠️ AI-generated clinical decision-support information "
    "must be reviewed by a qualified healthcare professional "
    "before any clinical decision is made."
)