import streamlit as st
import os
import time

from auth import initialize_session, login
from config.theme import apply_theme


# ============================================================
# INITIALIZATION
# ============================================================

initialize_session()
apply_theme()

st.set_page_config(
    page_title="CareWatch-AI | Login",
    page_icon="🏥",
    layout="centered"
)


# ============================================================
# LOGO
# ============================================================

logo_path = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "assets",
    "logo.png"
)

if os.path.exists(logo_path):

    st.image(
        logo_path,
        width=180
    )

else:

    st.markdown(
        """
        <h1 style="text-align:center;">
            🏥 CareWatch-AI
        </h1>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# TITLE
# ============================================================

st.title("CareWatch-AI")

st.caption(
    "Explainable AI-Based Clinical Decision Support System"
)

st.write("")


# ============================================================
# LOGIN
# ============================================================

st.divider()

st.subheader("🔐 User Login")

username = st.text_input(
    "Username",
    placeholder="Admin / Doctor / Patient ID"
)

password = st.text_input(
    "Password",
    type="password",
    placeholder="Enter your password"
)

login_button = st.button(
    "Login",
    use_container_width=True
)


# ============================================================
# LOGIN PROCESS
# ============================================================

if login_button:

    if not username or not password:

        st.warning(
            "Please enter both username and password."
        )

    else:

        success = login(username, password)

        if success:

            st.success(
                f"Login successful! "
                f"Welcome, {st.session_state['role']}."
            )

            import time
            time.sleep(1)

            st.switch_page("app.py")

        else:

            st.error("Invalid username or password.")

            st.info(
                "For patients, use your Patient ID "
                "(for example P001) and password "
                "'patient123'."
            )


# ============================================================
# DEMO LOGIN INFORMATION
# ============================================================

with st.expander("🔑 Login Information"):

    st.write("### 👑 Admin")

    st.code(
        "Username: admin\n"
        "Password: admin123"
    )

    st.write("### 👨‍⚕️ Doctor")

    st.code(
        "Username: doctor\n"
        "Password: doctor123"
    )

    st.write("### 👤 Patient")

    st.code(
        "Username: P001\n"
        "Password: patient123"
    )

    st.caption(
        "Other patients can log in using their own "
        "patient_id from prediction_results.csv."
    )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "CareWatch-AI | AI-Assisted Healthcare Decision Support"
)