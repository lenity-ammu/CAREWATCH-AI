import os
import time

import streamlit as st

from auth import (
    initialize_session,
    login,
    register_patient
)

from config.theme import apply_theme


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="CareWatch-AI | Login",
    page_icon="🏥",
    layout="centered",
    initial_sidebar_state="collapsed"
)


# ============================================================
# INITIALIZATION
# ============================================================

initialize_session()
apply_theme()


# ============================================================
# PATHS
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

LOGO_PATH = os.path.join(
    BASE_DIR,
    "assets",
    "logo.png"
)


# ============================================================
# LOGIN PAGE CSS
# ============================================================

st.markdown(
    """
    <style>

    section[data-testid="stSidebar"] {
        display:none;
    }

    .block-container {
        max-width:700px;
        padding-top:1.5rem;
        padding-bottom:2rem;
    }

    .carewatch-footer {
        text-align:center;
        color:#7b8794;
        font-size:0.82rem;
        margin-top:25px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# LOGO
# ============================================================

if os.path.exists(
    LOGO_PATH
):

    c1, c2, c3 = st.columns(
        [
            1,
            2,
            1
        ]
    )

    with c2:

        st.image(
            LOGO_PATH,
            use_container_width=True
        )

else:

    st.markdown(
        """
        <div style="
            text-align:center;
            font-size:60px;
        ">
            🏥
        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# TITLE
# ============================================================

st.markdown(
    """
    <h1 style="text-align:center;">
        CareWatch-AI
    </h1>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <p style="
        text-align:center;
        color:#6c757d;
    ">
        Explainable AI-Based Clinical Decision Support System
    </p>
    """,
    unsafe_allow_html=True
)

st.divider()


# ============================================================
# ALREADY LOGGED IN
# ============================================================

if st.session_state.get(
    "logged_in",
    False
):

    st.success(
        "You are already logged in."
    )

    if st.button(
        "Continue to CareWatch-AI",
        use_container_width=True
    ):

        st.switch_page(
            "app.py"
        )

    st.stop()


# ============================================================
# LOGIN / REGISTRATION TABS
# ============================================================

login_tab, registration_tab = (
    st.tabs(
        [
            "🔐 Login",
            "👤 Patient Registration"
        ]
    )
)


# ============================================================
# LOGIN TAB
# ============================================================

with login_tab:

    st.subheader(
        "🔐 Secure User Login"
    )

    st.caption(
        "Doctors, administrators and registered "
        "patients can sign in here."
    )

    with st.form(
        "carewatch_login_form",
        clear_on_submit=False
    ):

        username = st.text_input(
            "Username / Patient ID",
            placeholder=(
                "Enter username or Patient ID"
            ),
            key="login_username"
        )

        password = st.text_input(
            "Password",
            type="password",
            placeholder="Enter password",
            key="login_password"
        )

        login_submitted = (
            st.form_submit_button(
                "🔐 Login",
                use_container_width=True
            )
        )

    if login_submitted:

        username = (
            username
            .strip()
        )

        if (
            not username
            or
            not password
        ):

            st.warning(
                "Please enter both username "
                "and password."
            )

        else:

            success, message = login(
                username,
                password
            )

            if success:

                st.success(
                    message
                )

                time.sleep(
                    0.5
                )

                st.switch_page(
                    "app.py"
                )

            else:

                st.error(
                    "Invalid username or password."
                )


# ============================================================
# PATIENT REGISTRATION TAB
# ============================================================

with registration_tab:

    st.subheader(
        "👤 Create Patient Account"
    )

    st.caption(
        "Patients can register using a valid "
        "Patient ID from the CareWatch-AI "
        "healthcare dataset."
    )

    st.info(
        "You only need to register once. "
        "After registration, use your Patient ID "
        "and chosen password on the Login tab."
    )

    with st.form(
        "patient_registration_form",
        clear_on_submit=False
    ):

        patient_id = st.text_input(
            "Patient ID",
            placeholder=(
                "Enter your Patient ID"
            ),
            key="register_patient_id"
        )

        new_password = st.text_input(
            "Create Password",
            type="password",
            placeholder=(
                "Minimum 8 characters"
            ),
            key="register_password"
        )

        confirm_password = st.text_input(
            "Confirm Password",
            type="password",
            placeholder=(
                "Re-enter your password"
            ),
            key="register_confirm_password"
        )

        register_submitted = (
            st.form_submit_button(
                "👤 Create Patient Account",
                use_container_width=True
            )
        )

    if register_submitted:

        success, message = (
            register_patient(
                patient_id,
                new_password,
                confirm_password
            )
        )

        if success:

            st.success(
                message
            )

            st.info(
                "Return to the Login tab and "
                "sign in using your Patient ID."
            )

        else:

            st.error(
                message
            )


# ============================================================
# REGISTRATION SECURITY NOTE
# ============================================================

st.markdown("---")

st.caption(
    "🔒 Passwords are stored as cryptographic hashes "
    "and are not displayed by CareWatch-AI."
)

st.caption(
    "Patient self-registration is implemented for "
    "prototype demonstration. A production healthcare "
    "deployment should include stronger identity "
    "verification before account creation."
)


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """
    <div class="carewatch-footer">
        CareWatch-AI | Secure Clinical Decision Support System
    </div>
    """,
    unsafe_allow_html=True
)