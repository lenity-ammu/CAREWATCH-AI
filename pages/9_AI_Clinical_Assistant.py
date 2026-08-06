import streamlit as st
import spacy

from translator import translate_text
# =====================================================
# Initialize Session Variables
# =====================================================

conditions = st.session_state.get("conditions", [])

risk = st.session_state.get("risk_factors", [])

recommendations = st.session_state.get("recommendations", [])

summary = st.session_state.get("clinical_summary", "")

risk_level = st.session_state.get("risk_level", "Low")

# ==========================================================
# PAGE CONFIG (Must be first Streamlit command)
# ==========================================================

st.set_page_config(
    page_title="AI Clinical Assistant",
    page_icon="🧠",
    layout="wide"
)

lang = st.session_state.get("language", "English")

st.title("🧠 " + translate_text("AI Clinical Assistant", lang))

st.markdown(
    translate_text(
        "Analyze doctor's clinical notes using Natural Language Processing (NLP) and generate AI-powered clinical recommendations.",
        lang
    )
)

# ==========================================================
# LOAD SPACY MODEL
# ==========================================================

@st.cache_resource
def load_model():
    return spacy.blank("en")

nlp = load_model()

# ==========================================================
# MEDICAL KNOWLEDGE BASE
# ==========================================================

MEDICAL_DB = {

    "Diabetes":{

        "keywords":[
            "diabetes",
            "glucose",
            "hyperglycemia",
            "hba1c"
        ],

        "recommendations":[

            "Monitor HbA1c every 3 months.",

            "Maintain blood glucose control.",

            "Provide diabetic diet counselling.",

            "Ensure medication adherence."

        ]

    },

    "Chronic Kidney Disease":{

        "keywords":[

            "ckd",

            "kidney",

            "renal",

            "creatinine"

        ],

        "recommendations":[

            "Schedule nephrology follow-up.",

            "Monitor kidney function.",

            "Avoid nephrotoxic drugs.",

            "Maintain hydration."

        ]

    },

    "Heart Failure":{

        "keywords":[

            "heart failure",

            "cardiac failure"

        ],

        "recommendations":[

            "Cardiology consultation.",

            "Reduce salt intake.",

            "Daily weight monitoring.",

            "Monitor fluid status."

        ]

    },

    "Hypertension":{

        "keywords":[

            "hypertension",

            "blood pressure"

        ],

        "recommendations":[

            "Monitor blood pressure.",

            "Reduce sodium intake.",

            "Encourage regular exercise."

        ]

    },

    "COPD":{

        "keywords":[

            "copd",

            "chronic obstructive"

        ],

        "recommendations":[

            "Smoking cessation.",

            "Pulmonary rehabilitation.",

            "Monitor oxygen saturation."

        ]

    },

    "Pneumonia":{

        "keywords":[

            "pneumonia",

            "lung infection"

        ],

        "recommendations":[

            "Complete antibiotic therapy.",

            "Maintain hydration.",

            "Monitor respiratory status."

        ]

    },

    "Sepsis":{

        "keywords":[

            "sepsis",

            "infection"

        ],

        "recommendations":[

            "Monitor infection markers.",

            "Frequent vital monitoring.",

            "Review antibiotic response."

        ]

    }

}
# ==========================================================
# NLP FUNCTIONS
# ==========================================================

def detect_conditions(text):

    text = text.lower()

    detected = []

    recommendations = []

    doc = nlp(text)

    processed_text = " ".join([token.text for token in doc])

    for disease, data in MEDICAL_DB.items():

        for keyword in data["keywords"]:

            if keyword in processed_text:

                if disease not in detected:

                    detected.append(disease)

                    recommendations.extend(data["recommendations"])

                break

    return detected, recommendations


# ==========================================================
# READMISSION RISK DETECTION
# ==========================================================

def detect_risk(text):

    text = text.lower()

    risks = []

    risk_keywords = {

        "Previous Hospital Admission":"previous admission",

        "Poor Medication Adherence":"poor medication adherence",

        "High HbA1c":"hba1c",

        "Chronic Kidney Disease":"ckd",

        "Heart Failure":"heart failure",

        "Sepsis":"sepsis",

        "COPD":"copd",

        "Hypertension":"hypertension"

    }

    for label, keyword in risk_keywords.items():

        if keyword in text:

            risks.append(label)

    return risks


# ==========================================================
# AI CLINICAL NOTES INPUT
# ==========================================================

st.markdown("---")

st.subheader(
    translate_text(
        "Clinical Notes",
        lang
    )
)

notes = st.text_area(

    translate_text(
        "Enter Doctor's Clinical Notes",
        lang
    ),

    height=250,

    placeholder="""
Patient has uncontrolled diabetes.

Known CKD Stage III.

Previous admission due to heart failure.

HbA1c remains elevated.

Poor medication adherence.

Complains of breathlessness.

Creatinine elevated.
"""

)

analyze = st.button(

    translate_text(
        "Analyze Clinical Notes",
        lang
    ),

    use_container_width=True

)

# ==========================================================
# AI ANALYSIS
# ==========================================================

if analyze:

    if notes.strip() == "":

        st.warning(

            translate_text(
                "Please enter clinical notes.",
                lang
            )

        )

    else:

        conditions, recommendations = detect_conditions(notes)

        risk = detect_risk(notes)

        recommendations = sorted(list(set(recommendations)))

        st.markdown("---")

        col1, col2 = st.columns(2)

        with col1:

            st.subheader("🩺 " + translate_text("Detected Conditions", lang))

            if len(conditions)==0:

                st.info(

                    translate_text(
                        "No medical conditions detected.",
                        lang
                    )

                )

            else:

                for item in conditions:

                    st.success(item)

        with col2:

            st.subheader("⚠️ " + translate_text("Readmission Risk Factors", lang))

            if len(risk)==0:

                st.success(

                    translate_text(
                        "No major risk factors detected.",
                        lang
                    )

                )

            else:

                for item in risk:

                    st.error(item)
                    
# ==========================================================
# AI RECOMMENDATIONS
# ==========================================================

        st.markdown("---")

        st.subheader("🤖 " + translate_text("AI Recommendations", lang))

        if len(recommendations) == 0:

            st.info(
                translate_text(
                    "No recommendations generated.",
                    lang
                )
            )

        else:

            for rec in recommendations:

                st.info("✅ " + rec)


# ==========================================================
# AI RISK SCORE
# ==========================================================

        st.markdown("---")

        risk_score = len(conditions) + len(risk)

        st.subheader("📊 " + translate_text("Clinical Risk Assessment", lang))

        if risk_score >= 6:

            risk_level = "High"

            st.error("🔴 HIGH RISK")

        elif risk_score >= 3:

            risk_level = "Moderate"

            st.warning("🟡 MODERATE RISK")

        else:

            risk_level = "Low"

            st.success("🟢 LOW RISK")

        st.progress(min(risk_score / 8, 1.0))


# ==========================================================
# AI CLINICAL SUMMARY
# ==========================================================

        st.markdown("---")

        st.subheader("🧠 " + translate_text("AI Clinical Summary", lang))

        if len(conditions) == 0:

            summary = (
                "No significant chronic medical conditions were detected from the clinical notes."
            )

        else:

            summary = (
                f"The patient presents with {', '.join(conditions)}. "
            )

            if len(risk) > 0:

                summary += (
                    f"Important readmission risk factors include {', '.join(risk)}. "
                )

            summary += (
                f"The overall assessment indicates a {risk_level.lower()} likelihood of "
                "30-day hospital readmission. Early follow-up, medication review and "
                "appropriate specialist consultation are recommended."
            )

        st.success(summary)
# ==========================================================
# FOLLOW-UP PLAN
# ==========================================================

        st.markdown("---")

        st.subheader("📅 " + translate_text("Suggested Follow-up Plan", lang))

        plan = []

        if "Diabetes" in conditions:
            plan.append("✔ HbA1c review within 3 months")

        if "Chronic Kidney Disease" in conditions:
            plan.append("✔ Nephrology consultation")

        if "Heart Failure" in conditions:
            plan.append("✔ Cardiology follow-up")

        if "Hypertension" in conditions:
            plan.append("✔ Weekly blood pressure monitoring")

        if "COPD" in conditions:
            plan.append("✔ Pulmonary rehabilitation")

        if "Sepsis" in conditions:
            plan.append("✔ Infection monitoring")

        if len(plan) == 0:
            plan.append("✔ Routine outpatient follow-up")

        for item in plan:

            st.write(item)
# ==========================================================
# FOLLOW-UP PLAN
# ==========================================================

        st.markdown("---")

        st.subheader("📅 " + translate_text("Suggested Follow-up Plan", lang))

        plan = []

        if "Diabetes" in conditions:
            plan.append("✔ HbA1c review within 3 months")

        if "Chronic Kidney Disease" in conditions:
            plan.append("✔ Nephrology consultation")

        if "Heart Failure" in conditions:
            plan.append("✔ Cardiology follow-up")

        if "Hypertension" in conditions:
            plan.append("✔ Weekly blood pressure monitoring")

        if "COPD" in conditions:
            plan.append("✔ Pulmonary rehabilitation")

        if "Sepsis" in conditions:
            plan.append("✔ Infection monitoring")

        if len(plan) == 0:
            plan.append("✔ Routine outpatient follow-up")

        for item in plan:

            st.write(item)
# ==========================================================
# SAVE RESULTS FOR REPORT PAGE
# ==========================================================

        st.session_state["conditions"] = conditions

        st.session_state["risk_factors"] = risk

        st.session_state["recommendations"] = recommendations

        st.session_state["clinical_summary"] = summary

        st.session_state["risk_level"] = risk_level


# ==========================================================
# SCORE CARDS
# ==========================================================

        st.markdown("---")

        c1, c2, c3 = st.columns(3)

        c1.metric(
            "Detected Diseases",
            len(conditions)
        )

        c2.metric(
            "Risk Factors",
            len(risk)
        )

        c3.metric(
            "Overall Risk",
            risk_level
        )
 # ==========================================================
# NLP ENTITY VISUALIZATION
# ==========================================================

st.markdown("---")

st.subheader("🔬 Medical Entity Analysis")

doc = nlp(notes)

entities_found = []

for ent in doc.ents:
    entities_found.append((ent.text, ent.label_))

if len(entities_found) == 0:

    st.info("No named entities detected by spaCy.")

else:

    entity_df = []

    for entity, label in entities_found:

        entity_df.append({

            "Entity": entity,

            "Type": label

        })

    st.dataframe(
        entity_df,
        use_container_width=True
    )
# ==========================================================
# NLP DOCUMENT STATISTICS
# ==========================================================

st.markdown("---")

st.subheader("📊 NLP Statistics")

doc = nlp(notes)

num_tokens = len(doc)

num_sentences = len(list(doc.sents))

num_words = len([t for t in doc if t.is_alpha])

num_numbers = len([t for t in doc if t.like_num])

c1,c2,c3,c4 = st.columns(4)

c1.metric("Tokens", num_tokens)

c2.metric("Words", num_words)

c3.metric("Sentences", num_sentences)

c4.metric("Numbers", num_numbers)

# ==========================================================
# AI CONFIDENCE SCORE
# ==========================================================

st.markdown("---")

st.subheader("🎯 AI Confidence")

confidence = 70

confidence += len(conditions) * 4

confidence += len(risk) * 2

confidence = min(confidence,99)

st.progress(confidence/100)

st.metric(
    "Confidence Score",
    f"{confidence}%"
)

# ==========================================================
# EXPORT SUMMARY
# ==========================================================

st.markdown("---")

st.subheader("📋 Copy Summary")

report = f"""

CAREWATCH-AI Clinical Analysis

Detected Conditions:
{', '.join(conditions)}

Risk Factors:
{', '.join(risk)}

Clinical Summary:

{summary}

Recommendations:

"""

for rec in recommendations:

    report += f"\n• {rec}"

st.text_area(

    "Clinical Summary",

    report,

    height=250

)