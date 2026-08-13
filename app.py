import os
import streamlit as st

from auth import redirect_after_login


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
# PATHS
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")

HOSPITAL_PATH = os.path.join(
    ASSETS_DIR,
    "hospital.jpg"
)


# ============================================================
# CHECK LOGIN STATUS
# ============================================================

logged_in = bool(
    st.session_state.get("authenticated", False)
    or st.session_state.get("logged_in", False)
    or st.session_state.get("user")
    or st.session_state.get("role")
)


# ============================================================
# CSS
# ============================================================

if not logged_in:

    # Hide sidebar ONLY on login screen

    st.markdown(
        """
        <style>

        .stApp {
            background-color: #f5f8fb;
        }

        .block-container {
            max-width: 850px;
            padding-top: 1rem;
            padding-bottom: 2rem;
        }

        section[data-testid="stSidebar"] {
            display: none;
        }

        div[data-testid="stForm"] {
            background: white;
            border: 1px solid #e1e7ec;
            border-radius: 16px;
            padding: 25px 28px 20px 28px;
            box-shadow: 0 5px 20px rgba(0,0,0,0.07);
        }

        div[data-testid="stFormSubmitButton"] button {
            width: 100%;
            border-radius: 9px;
            min-height: 44px;
            font-weight: 600;
        }

        .carewatch-footer {
            text-align: center;
            color: #7b8794;
            font-size: 0.8rem;
            margin-top: 25px;
            padding-top: 15px;
            border-top: 1px solid #dfe5ea;
        }

        </style>
        """,
        unsafe_allow_html=True
    )

else:

    # ========================================================
    # AFTER LOGIN
    # ========================================================
    # Sidebar is intentionally NOT hidden.

    st.markdown(
        """
        <style>

        .stApp {
            background-color: #f5f8fb;
        }

        .carewatch-footer {
            text-align: center;
            color: #7b8794;
            font-size: 0.8rem;
            margin-top: 25px;
            padding-top: 15px;
            border-top: 1px solid #dfe5ea;
        }

        </style>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# LOGIN / REDIRECT
# ============================================================

redirect_after_login()


# ============================================================
# HOSPITAL IMAGE
# ============================================================

# Only show the hospital image on the login page.
# After login, the dashboards handle their own layout.

if not logged_in:

    if os.path.exists(HOSPITAL_PATH):

        st.image(
            HOSPITAL_PATH,
            use_container_width=True
        )


# ============================================================
# FOOTER
# ============================================================

if not logged_in:

    st.markdown(
        """
        <div class="carewatch-footer">
            🔒 CareWatch-AI | Secure Clinical Decision Support System
        </div>
        """,
        unsafe_allow_html=True
    )