import streamlit as st
from translator import translate_text

lang = st.session_state.get("language", "English")


st.set_page_config(
    page_title="CareWatch-AI Login",
    page_icon="🏥",
    layout="wide"
)

st.title("🏥"+translate_text(" CareWatch-AI Login",lang))

st.markdown("---")

role = st.selectbox(
    "Login As",
    [
        "Doctor",
        "Patient",
        "Administrator"
    ]
)

username = st.text_input("Username")

password = st.text_input(
    "Password",
    type="password"
)

if st.button("Login"):

    if username == "" or password == "":
        st.error("Please enter username and password")

    else:
        st.success(f"Welcome {username}")

        st.write("Logged in as :", role)
