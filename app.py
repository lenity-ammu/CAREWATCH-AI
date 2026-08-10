import streamlit as st

from auth import initialize_session, require_login


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="CareWatch-AI",
    page_icon="🏥",
    layout="wide"
)


# =========================================================
# SESSION
# =========================================================

initialize_session()


# =========================================================
# LOGIN CHECK
# =========================================================

require_login()


# =========================================================
# GET CURRENT ROLE
# =========================================================

role = st.session_state.get("role")

username = st.session_state.get(
    "username",
    ""
)


# =========================================================
# HEADER
# =========================================================

st.title("🏥 CareWatch-AI")

st.subheader(
    "AI Powered Hospital Readmission Prediction System"
)

st.markdown("---")


# =========================================================
# ROLE BASED LANDING PAGE
# =========================================================

if role == "Patient":

    st.success(
        f"Welcome, {st.session_state.get('patient_name', username)}!"
    )

    st.write(
        "You are logged in as a Patient."
    )

    st.info(
        "Opening your Patient Dashboard..."
    )

    st.switch_page(
        "pages/10_Patient_Dashboard.py"
    )


elif role == "Doctor":

    st.success(
        f"Welcome, Dr. {username.title()}!"
    )

    st.write(
        "You are logged in as a Doctor."
    )

    st.info(
        "Opening the Doctor Dashboard..."
    )

    st.switch_page(
        "pages/2_Dashboard.py"
    )


elif role == "Admin":

    st.success(
        "Welcome, Admin!"
    )

    st.write(
        "You are logged in as an Administrator."
    )

    st.info(
        "Opening the Admin Dashboard..."
    )

    st.switch_page(
        "pages/7_Admin.py"
    )


else:

    st.error(
        "Unknown user role."
    )

    st.write(
        f"Current role: {role}"
    )