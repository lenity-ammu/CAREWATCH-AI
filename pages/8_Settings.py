import streamlit as st

from translator import translate_text

# Get selected language
lang = st.session_state.get("language", "English")

st.set_page_config(page_title="Settings", layout="wide")

st.title("⚙️"+translate_text(" Settings",lang))

st.subheader("Application Settings")

# -------------------------
# Theme
# -------------------------

theme = st.selectbox(
    "Theme",
    ["Light", "Dark"]
)

# -------------------------
# Language
# -------------------------

language = st.selectbox(

    "🌍 Select Language",

    [

        "English",

        "Hindi",

        "Kannada",

        "Tamil",

        "Telugu",

        "Malayalam"

    ]

)

st.session_state.language = language
# -------------------------
# Notifications
# -------------------------

notifications = st.checkbox(
    "Enable Notifications",
    value=True
)

# -------------------------
# Email
# -------------------------

email = st.text_input(
    "Administrator Email",
    "admin@carewatch.ai"
)

# -------------------------
# Threshold
# -------------------------

threshold = st.slider(
    "High Risk Threshold",
    0.00,
    1.00,
    0.25,
    0.01
)

st.divider()

st.subheader("Language Preview")
st.session_state["language"] = language

translations = {
    "English":
        "Prediction Completed Successfully.",

    "Kannada":
        "ಭವಿಷ್ಯವಾಣಿ ಯಶಸ್ವಿಯಾಗಿ ಪೂರ್ಣಗೊಂಡಿದೆ.",

    "Hindi":
        "पूर्वानुमान सफलतापूर्वक पूरा हुआ।",

    "Tamil":
        "முன்கணிப்பு வெற்றிகரமாக முடிந்தது.",

    "Telugu":
        "అంచనా విజయవంతంగా పూర్తయింది.",

    "Malayalam":
        "പ്രവചനം വിജയകരമായി പൂർത്തിയായി."
}

st.success(translations[language])

st.divider()

if st.button("💾 Save Settings", use_container_width=True):

    st.success("Settings saved successfully.")