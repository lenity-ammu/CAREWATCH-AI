import streamlit as st


def apply_theme():

    st.markdown(
        """
        <style>

        /* -----------------------------
           GLOBAL
        ----------------------------- */

        .stApp {
            background-color: #F5F9FC;
        }

        /* -----------------------------
           MAIN HEADINGS
        ----------------------------- */

        h1, h2, h3 {
            color: #123B5D;
            font-family: Arial, sans-serif;
        }

        /* -----------------------------
           BUTTONS
        ----------------------------- */

        .stButton > button {
            background-color: #1677A8;
            color: white;
            border-radius: 8px;
            border: none;
            padding: 0.55rem 1.2rem;
            font-weight: 600;
        }

        .stButton > button:hover {
            background-color: #0F5E86;
            color: white;
        }

        /* -----------------------------
           INPUT BOXES
        ----------------------------- */

        input {
            border-radius: 7px !important;
        }

        /* -----------------------------
           SIDEBAR
        ----------------------------- */

        section[data-testid="stSidebar"] {
            background-color: #EAF4F8;
        }

        /* -----------------------------
           CARDS
        ----------------------------- */

        .carewatch-card {

            background-color: white;

            padding: 20px;

            border-radius: 12px;

            box-shadow:
                0px 2px 10px rgba(0,0,0,0.08);

            margin-bottom: 20px;
        }

        /* -----------------------------
           LOGIN CARD
        ----------------------------- */

        .login-card {

            max-width: 500px;

            margin: auto;

            padding: 35px;

            background-color: white;

            border-radius: 15px;

            box-shadow:
                0px 4px 18px rgba(0,0,0,0.10);

        }

        </style>
        """,
        unsafe_allow_html=True
    )