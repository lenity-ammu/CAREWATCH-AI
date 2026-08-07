import streamlit as st
import spacy
import re


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="AI Clinical Assistant",
    page_icon="🧠",
    layout="wide"
)


# ============================================================
# NLP MODEL
# ============================================================

@st.cache_resource
def load_nlp_model():

    nlp = spacy.load("en_core_web_sm")

    # Make sure sentence boundaries are available
    if (
        "parser" not in nlp.pipe_names
        and "senter" not in nlp.pipe_names
        and "sentencizer" not in nlp.pipe_names
    ):
        nlp.add_pipe("sentencizer")

    return nlp


nlp = load_nlp_model()


# ============================================================
# DEFAULT VALUES
# ============================================================

conditions = []
risk = []
recommendations = []
risk_level = "Low"
summary = ""


# ============================================================
# PAGE TITLE
# ============================================================

st.title("🧠 AI Clinical Assistant")

st.write(
    "Analyze doctor's discharge summaries and clinical notes "
    "to identify medical conditions, risk factors and "
    "generate follow-up recommendations."
)


# ============================================================
# CLINICAL NOTES
# ============================================================

notes = st.text_area(
    "📝 Enter Clinical Notes",
    height=250,
    placeholder="""
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
    width="stretch"
)


# ============================================================
# MEDICAL DATABASE
# ============================================================

MEDICAL_DB = {

    "Diabetes": {
        "keywords": [
            "diabetes",
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
            "kidney disease",
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
            "cardiac failure"
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
            "sepsis"
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
        token.text for token in doc
    )

    for disease, info in MEDICAL_DB.items():

        for keyword in info["keywords"]:

            if keyword in clean_text:

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

    if "previous admission" in text:
        risk_factors.append(
            "Previous Hospital Admission"
        )

    if "poor medication adherence" in text:
        risk_factors.append(
            "Poor Medication Adherence"
        )

    if "hba1c" in text:
        risk_factors.append(
            "High HbA1c"
        )

    if "ckd" in text:
        risk_factors.append(
            "Chronic Kidney Disease"
        )

    if "heart failure" in text:
        risk_factors.append(
            "Heart Failure"
        )

    if "sepsis" in text:
        risk_factors.append(
            "Sepsis"
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

        conditions, recommendations = detect_conditions(notes)

        risk = detect_risk(notes)

        # ----------------------------------------------------
        # TEXT STATISTICS
        # ----------------------------------------------------

        doc = nlp(notes)

        num_tokens = len(doc)

        # Do NOT depend on doc.sents
        num_sentences = len(
            [
                s for s in re.split(
                    r"[.!?]+",
                    notes
                )
                if s.strip()
            ]
        )

        num_words = len(
            [
                token
                for token in doc
                if token.is_alpha
            ]
        )

        # ----------------------------------------------------
        # RISK SCORE
        # ----------------------------------------------------

        risk_score = len(conditions) + len(risk)

        if risk_score >= 6:

            risk_level = "High"

        elif risk_score >= 3:

            risk_level = "Moderate"

        else:

            risk_level = "Low"

        # ----------------------------------------------------
        # RESULTS
        # ----------------------------------------------------

        st.markdown("---")

        st.subheader(
            "📊 Clinical Note Statistics"
        )

        c1, c2, c3 = st.columns(3)

        c1.metric(
            "Words",
            num_words
        )

        c2.metric(
            "Sentences",
            num_sentences
        )

        c3.metric(
            "Tokens",
            num_tokens
        )

        # ----------------------------------------------------
        # CONDITIONS + RISK
        # ----------------------------------------------------

        st.markdown("---")

        col1, col2 = st.columns(2)

        with col1:

            st.subheader(
                "🩺 Detected Medical Conditions"
            )

            if conditions:

                for condition in conditions:
                    st.success(condition)

            else:

                st.info(
                    "No medical conditions detected."
                )

        with col2:

            st.subheader(
                "⚠️ Readmission Risk Factors"
            )

            if risk:

                for factor in risk:
                    st.error(factor)

            else:

                st.success(
                    "No major risk factors detected."
                )

        # ----------------------------------------------------
        # RECOMMENDATIONS
        # ----------------------------------------------------

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

        # ----------------------------------------------------
        # RISK ASSESSMENT
        # ----------------------------------------------------

        st.markdown("---")

        st.subheader(
            "📊 AI Clinical Risk Assessment"
        )

        if risk_level == "High":

            st.error("🔴 HIGH RISK")

        elif risk_level == "Moderate":

            st.warning("🟡 MODERATE RISK")

        else:

            st.success("🟢 LOW RISK")

        st.progress(
            min(risk_score / 8, 1.0)
        )

        # ----------------------------------------------------
        # SUMMARY
        # ----------------------------------------------------

        st.markdown("---")

        st.subheader(
            "🧠 AI Clinical Summary"
        )

        if conditions:

            summary = (
                f"The clinical notes indicate "
                f"{', '.join(conditions)}. "
            )

            if risk:

                summary += (
                    f"Important readmission risk factors "
                    f"include {', '.join(risk)}. "
                )

            summary += (
                f"The rule-based clinical assessment "
                f"classifies the documented risk as "
                f"{risk_level.lower()}. "
                f"Clinical findings should be reviewed "
                f"by the treating healthcare professional."
            )

        else:

            summary = (
                "No major conditions were identified "
                "from the supplied clinical notes."
            )

        st.success(summary)