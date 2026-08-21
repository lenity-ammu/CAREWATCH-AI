import os

import streamlit as st

from auth import (
    initialize_session,
    is_logged_in,
    redirect_after_login,
    show_sidebar
)


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="CareWatch-AI",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# INITIALIZE SESSION
# ============================================================

initialize_session()


# ============================================================
# PATHS
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

ASSETS_DIR = os.path.join(
    BASE_DIR,
    "assets"
)

LOGO_PATH = os.path.join(
    ASSETS_DIR,
    "logo.png"
)


# ============================================================
# GLOBAL CSS
# ============================================================

st.markdown(
    """
    <style>

    .stApp {
        background-color: #f5f8fb;
    }

    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
    }

    .carewatch-footer {
        text-align: center;
        color: #7b8794;
        font-size: 0.82rem;
        margin-top: 35px;
        padding-top: 15px;
        border-top: 1px solid #dfe5ea;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# LOGIN CHECK
# ============================================================

if not is_logged_in():

    st.switch_page(
        "pages/1Login.py"
    )

    st.stop()


# ============================================================
# SHOW ROLE-BASED SIDEBAR
# ============================================================

show_sidebar()


# ============================================================
# MAIN HEADER
# ============================================================

header_col, logo_col = st.columns(
    [5, 1]
)


with header_col:

    st.title(
        "🏥 CareWatch-AI"
    )

    st.caption(
        "Explainable AI-Based Hospital Readmission "
        "Prediction and Clinical Decision Support System"
    )


with logo_col:

    if os.path.exists(
        LOGO_PATH
    ):

        st.image(
            LOGO_PATH,
            use_container_width=True
        )


st.markdown("---")


# ============================================================
# ROLE LANDING CONTENT
# ============================================================

redirect_after_login()


# ============================================================
# SYSTEM OVERVIEW
# ============================================================

st.markdown("---")

st.header(
    "🧠 CareWatch-AI Platform"
)


role = st.session_state.get(
    "role"
)


# ============================================================
# DOCTOR VIEW
# ============================================================

if role == "Doctor":

    st.write(
        "CareWatch-AI provides an integrated clinical "
        "workflow for 30-day hospital readmission prediction, "
        "Electronic Health Record review, Explainable AI, "
        "blockchain auditing and clinical report generation."
    )


    c1, c2, c3 = st.columns(
        3
    )


    with c1:

        st.subheader(
            "🧠 AI Prediction"
        )

        st.write(
            "Run the finalized Class-Weighted LightGBM "
            "readmission prediction using 27 healthcare features."
        )

        st.page_link(
            "pages/3_Prediction.py",
            label="Open AI Prediction",
            use_container_width=True
        )


    with c2:

        st.subheader(
            "📋 Electronic Health Record"
        )

        st.write(
            "Review patient demographic, admission, diagnosis, "
            "clinical, hospital and financial information."
        )

        st.page_link(
            "pages/11_EHR.py",
            label="Open EHR",
            use_container_width=True
        )


    with c3:

        st.subheader(
            "🔬 Explainable AI"
        )

        st.write(
            "Use SHAP to understand the features "
            "contributing to the final LightGBM prediction."
        )

        st.page_link(
            "pages/4_SHAP_Explainability.py",
            label="Open SHAP / XAI",
            use_container_width=True
        )


    st.write("")


    c4, c5, c6 = st.columns(
        3
    )


    with c4:

        st.subheader(
            "🔗 Blockchain Audit"
        )

        st.write(
            "Review the tamper-evident audit trail "
            "associated with prediction records."
        )

        st.page_link(
            "pages/12_Blockchain.py",
            label="Open Blockchain Audit",
            use_container_width=True
        )


    with c5:

        st.subheader(
            "📄 Report Generation"
        )

        st.write(
            "Generate patient clinical AI reports "
            "containing prediction and risk information."
        )

        st.page_link(
            "pages/5_Report_Generation.py",
            label="Open Report Generation",
            use_container_width=True
        )


    with c6:

        st.subheader(
            "📊 Doctor Dashboard"
        )

        st.write(
            "Review patient statistics, prediction counts "
            "and recent AI prediction activity."
        )

        st.page_link(
            "pages/1_Doctor_Dashboard.py",
            label="Open Doctor Dashboard",
            use_container_width=True
        )


# ============================================================
# PATIENT VIEW
# ============================================================

elif role == "Patient":

    st.write(
        "CareWatch-AI provides secure access to your "
        "health information and available clinical records."
    )


    c1, c2 = st.columns(
        2
    )


    with c1:

        st.subheader(
            "🏠 Patient Dashboard"
        )

        st.write(
            "Review your CareWatch-AI patient information "
            "and available healthcare information."
        )

        st.page_link(
            "pages/10_Patient_Dashboard.py",
            label="Open Patient Dashboard",
            use_container_width=True
        )


    with c2:

        st.subheader(
            "📋 Electronic Health Record"
        )

        st.write(
            "Review your admissions, diagnosis, "
            "billing and available AI prediction information."
        )

        st.page_link(
            "pages/11_EHR.py",
            label="Open My EHR",
            use_container_width=True
        )


    st.info(
        "🔒 Patients can access only the health record "
        "associated with their registered Patient ID."
    )


# ============================================================
# ADMIN VIEW
# ============================================================

elif role == "Admin":

    st.write(
        "The CareWatch-AI administration portal provides "
        "authorized access to system-level management "
        "and blockchain audit information."
    )


    c1, c2 = st.columns(
        2
    )


    with c1:

        st.subheader(
            "⚙️ Administration"
        )

        st.write(
            "Review administrative and system information."
        )

        st.page_link(
            "pages/7_Admin.py",
            label="Open Administration",
            use_container_width=True
        )


    with c2:

        st.subheader(
            "🔗 Blockchain Audit"
        )

        st.write(
            "Review blockchain integrity and audit records."
        )

        st.page_link(
            "pages/12_Blockchain.py",
            label="Open Blockchain Audit",
            use_container_width=True
        )


# ============================================================
# FINAL MODEL INFORMATION
# ============================================================

if role == "Doctor":

    st.markdown("---")

    with st.expander(
        "ℹ️ Final AI Model Information"
    ):

        st.write(
            "**Prediction Model:** Class-Weighted LightGBM"
        )

        st.write(
            "**Input Features:** 27"
        )

        st.write(
            "**Target:** 30-Day Hospital Readmission"
        )

        st.write(
            "**Binary Decision Threshold:** 0.55"
        )

        st.write(
            "**ROC-AUC:** 0.7578"
        )

        st.write(
            "**PR-AUC:** 0.3403"
        )

        st.caption(
            "The optimized 0.55 threshold is used for "
            "the binary readmission decision. "
            "Low, Moderate and High risk categories are "
            "separate application-level probability bands."
        )


# ============================================================
# SECURITY NOTICE
# ============================================================

st.markdown("---")

st.info(
    "🔒 CareWatch-AI uses role-based access control "
    "to restrict clinical information and application modules "
    "to authorized users."
)


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """
    <div class="carewatch-footer">
        CareWatch-AI | Explainable AI-Based Clinical Decision Support System
    </div>
    """,
    unsafe_allow_html=True
)