import os

import joblib
import matplotlib.pyplot as plt
import pandas as pd
import shap
import streamlit as st

from auth import require_role
from translator import translate_text


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="CareWatch-AI | SHAP Explainability",
    page_icon="🔬",
    layout="wide"
)


# ============================================================
# AUTHENTICATION
# ============================================================

require_role(["Doctor"])


# ============================================================
# LANGUAGE
# ============================================================

lang = st.session_state.get(
    "language",
    "English"
)


# ============================================================
# PATHS
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

MODEL_DIR = os.path.join(
    BASE_DIR,
    "model"
)


# ============================================================
# LOAD FINAL MODEL ARTIFACTS
# ============================================================

@st.cache_resource
def load_model_files():

    model = joblib.load(
        os.path.join(
            MODEL_DIR,
            "carewatch_lightgbm_model.pkl"
        )
    )

    feature_columns = joblib.load(
        os.path.join(
            MODEL_DIR,
            "feature_columns.pkl"
        )
    )

    threshold = joblib.load(
        os.path.join(
            MODEL_DIR,
            "readmission_threshold.pkl"
        )
    )

    return (
        model,
        feature_columns,
        float(threshold)
    )


try:

    (
        model,
        FEATURE_COLUMNS,
        FINAL_THRESHOLD
    ) = load_model_files()

except Exception as error:

    st.error(
        "Unable to load the CareWatch-AI "
        "explainability model."
    )

    st.exception(error)

    st.stop()


# ============================================================
# HEADER
# ============================================================

st.title(
    "🔬 "
    + translate_text(
        "AI Explainability (SHAP)",
        lang
    )
)

st.caption(
    translate_text(
        "Understand the factors influencing "
        "the patient's readmission prediction.",
        lang
    )
)

st.markdown("---")


# ============================================================
# GET PREDICTION INPUT
# ============================================================

model_input = st.session_state.get(
    "last_model_input"
)

last_prediction = st.session_state.get(
    "last_prediction"
)


# ============================================================
# REQUIRE A PREVIOUS PREDICTION
# ============================================================

if model_input is None:

    st.warning(
        "No patient prediction is available for explanation."
    )

    st.info(
        "Run a patient prediction first. "
        "The SHAP page will then explain the exact "
        "feature values used by the final LightGBM model."
    )

    st.page_link(
        "pages/3_Prediction.py",
        label="🧠 Open AI Prediction",
        use_container_width=True
    )

    st.stop()


# ============================================================
# NORMALIZE MODEL INPUT
# ============================================================

if isinstance(
    model_input,
    pd.DataFrame
):

    df = model_input.copy()

else:

    try:

        df = pd.DataFrame(
            model_input
        )

    except Exception:

        st.error(
            "The saved prediction input could not be loaded."
        )

        st.stop()


# ============================================================
# VERIFY FEATURE COLUMNS
# ============================================================

for feature in FEATURE_COLUMNS:

    if feature not in df.columns:

        df[feature] = 0


df = df[
    FEATURE_COLUMNS
].copy()


for column in df.columns:

    df[column] = pd.to_numeric(
        df[column],
        errors="coerce"
    )


df = df.fillna(0)


# ============================================================
# IMPORTANT MODEL CONSISTENCY
# ============================================================
# DO NOT APPLY StandardScaler.
#
# The finalized Class-Weighted LightGBM model was trained
# using the encoded but unscaled feature representation.
# ============================================================


# ============================================================
# FINAL MODEL PREDICTION
# ============================================================

try:

    probability = float(
        model.predict_proba(
            df
        )[0][1]
    )

except Exception as error:

    st.error(
        "Unable to generate the prediction "
        "for SHAP explanation."
    )

    st.exception(error)

    st.stop()


predicted_readmission = int(
    probability >= FINAL_THRESHOLD
)

readmission_label = (
    "Yes"
    if predicted_readmission == 1
    else "No"
)


# ============================================================
# PATIENT INFORMATION
# ============================================================

patient_id = None

if isinstance(
    last_prediction,
    dict
):

    patient_id = last_prediction.get(
        "patient_id"
    )


st.subheader(
    "📊 Prediction Being Explained"
)

c1, c2, c3, c4 = st.columns(
    4
)


with c1:

    st.metric(
        "Patient ID",
        patient_id
        if patient_id
        else "N/A"
    )


with c2:

    st.metric(
        "Readmission Probability",
        f"{probability:.2%}"
    )


with c3:

    st.metric(
        "30-Day Readmission",
        readmission_label
    )


with c4:

    st.metric(
        "Model Threshold",
        f"{FINAL_THRESHOLD:.2f}"
    )


st.caption(
    "SHAP explains the same encoded 27-feature input "
    "used by the final Class-Weighted LightGBM model."
)

st.markdown("---")


# ============================================================
# CREATE SHAP EXPLAINER
# ============================================================

try:

    explainer = shap.TreeExplainer(
        model
    )

    shap_explanation = explainer(
        df
    )

except Exception as error:

    st.error(
        "SHAP explanation could not be generated."
    )

    st.exception(error)

    st.stop()


# ============================================================
# GLOBAL / FEATURE CONTRIBUTION VIEW
# ============================================================

st.subheader(
    "📊 Feature Contribution Overview"
)

st.info(
    "Features with larger SHAP values have a stronger "
    "influence on the model prediction. Positive values "
    "push the prediction toward higher readmission risk, "
    "while negative values push it toward lower risk."
)


try:

    plt.figure(
        figsize=(10, 7)
    )

    shap.summary_plot(
        shap_explanation.values,
        df,
        feature_names=FEATURE_COLUMNS,
        show=False
    )

    plt.tight_layout()

    st.pyplot(
        plt.gcf(),
        clear_figure=True
    )

except Exception as error:

    st.warning(
        "The SHAP summary plot could not be displayed."
    )

    st.caption(
        str(error)
    )


# ============================================================
# GLOBAL FEATURE IMPORTANCE BAR PLOT
# ============================================================

st.subheader(
    "📌 Important Features"
)


try:

    fig_bar = plt.figure(
        figsize=(10, 7)
    )

    shap.plots.bar(
        shap_explanation[0],
        max_display=15,
        show=False
    )

    plt.tight_layout()

    st.pyplot(
        fig_bar,
        clear_figure=True
    )

except Exception as error:

    st.warning(
        "The SHAP importance plot could not be displayed."
    )

    st.caption(
        str(error)
    )


# ============================================================
# WATERFALL EXPLANATION
# ============================================================

st.markdown("---")

st.subheader(
    "💧 Patient-Specific SHAP Waterfall"
)

st.markdown(
    """
### 📝 How to Read the Explanation

- **Red features** push the model prediction toward a higher readmission probability.
- **Blue features** push the prediction toward a lower readmission probability.
- **Longer bars** indicate a stronger contribution to the model output.
- The baseline value represents the model's average output before this patient's individual feature contributions are applied.
- SHAP explains the behaviour of the machine-learning model and does not establish clinical causation.
"""
)


try:

    fig_waterfall = plt.figure(
        figsize=(11, 7)
    )

    shap.plots.waterfall(
        shap_explanation[0],
        max_display=15,
        show=False
    )

    plt.tight_layout()

    st.pyplot(
        fig_waterfall,
        clear_figure=True
    )

except Exception as error:

    st.warning(
        "The patient-specific SHAP waterfall "
        "could not be displayed."
    )

    st.caption(
        str(error)
    )


# ============================================================
# NUMERICAL SHAP CONTRIBUTIONS
# ============================================================

st.markdown("---")

st.subheader(
    "📋 Feature Contribution Table"
)


try:

    contribution_values = (
        shap_explanation[
            0
        ].values
    )


    contribution_table = pd.DataFrame(
        {
            "Feature":
                FEATURE_COLUMNS,

            "Model Input":
                df.iloc[
                    0
                ].values,

            "SHAP Contribution":
                contribution_values
        }
    )


    contribution_table[
        "Absolute Contribution"
    ] = (
        contribution_table[
            "SHAP Contribution"
        ].abs()
    )


    contribution_table = (
        contribution_table
        .sort_values(
            "Absolute Contribution",
            ascending=False
        )
        .drop(
            columns=[
                "Absolute Contribution"
            ]
        )
        .reset_index(
            drop=True
        )
    )


    st.dataframe(
        contribution_table.head(
            15
        ),
        use_container_width=True,
        hide_index=True
    )

except Exception as error:

    st.warning(
        "Feature contribution values "
        "could not be displayed."
    )

    st.caption(
        str(error)
    )


# ============================================================
# CLINICAL INTERPRETATION NOTICE
# ============================================================

st.markdown("---")

st.info(
    "🔒 SHAP explanations support model transparency. "
    "They should be reviewed together with the patient's "
    "clinical information and professional medical judgement."
)


# ============================================================
# NAVIGATION
# ============================================================

st.subheader(
    "📋 Continue Clinical Workflow"
)

c1, c2, c3 = st.columns(
    3
)


with c1:

    st.page_link(
        "pages/3_Prediction.py",
        label="🧠 AI Prediction",
        use_container_width=True
    )


with c2:

    st.page_link(
        "pages/11_EHR.py",
        label="📋 Open EHR",
        use_container_width=True
    )


with c3:

    st.page_link(
        "pages/12_Blockchain.py",
        label="🔗 Blockchain Audit",
        use_container_width=True
    )