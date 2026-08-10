import streamlit as st
import os
import json
import pandas as pd

from auth import require_role, logout


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="CareWatch-AI | Patient Dashboard",
    page_icon="🏥",
    layout="wide"
)


# =========================================================
# PATIENT ACCESS ONLY
# =========================================================

require_role(["Patient"])


# =========================================================
# SESSION
# =========================================================

patient_id = st.session_state.get(
    "patient_id"
)

patient_name = st.session_state.get(
    "patient_name",
    patient_id
)


# =========================================================
# HEADER
# =========================================================

col1, col2 = st.columns([5, 1])

with col1:

    st.title("🏥 CareWatch-AI")

    st.caption(
        "AI-Based Clinical Decision Support System"
    )


with col2:

    if st.button(
        "Logout",
        use_container_width=True
    ):

        logout()


st.divider()


# =========================================================
# LANGUAGE
# =========================================================

language = st.selectbox(
    "🌐 Language",
    [
        "English",
        "Kannada",
        "Hindi",
        "Tamil",
        "Telugu",
        "Malayalam"
    ]
)


# =========================================================
# TRANSLATIONS
# =========================================================

TEXT = {

    "English": {

        "welcome":
            "👤 Welcome, Patient!",

        "subtitle":
            "Your Personal Health Portal",

        "profile":
            "👤 My Profile",

        "profile_desc":
            "View your registered health information.",

        "name":
            "Name",

        "age":
            "Age",

        "gender":
            "Gender",

        "hospital":
            "Hospital",

        "doctor":
            "Doctor",

        "state":
            "State",

        "risk":
            "📊 My Health Risk",

        "risk_desc":
            "View your latest health risk assessment.",

        "current_risk":
            "Current Risk Level",

        "probability":
            "Probability of 30-day hospital readmission",

        "summary":
            "🧠 Medical Summary",

        "recommendations":
            "💡 My Recommendations",

        "reports":
            "📄 My Reports",

        "security":
            "🔒 Your health information is securely displayed only within your account.",

        "doctor_notice":
            "Please consult your healthcare professional for medical decisions.",

        "no_prediction":
            "No prediction information is currently available for your Patient ID.",

        "no_report":
            "No reports have been generated for you yet."

    },

    "Kannada": {

        "welcome":
            "👤 ಸ್ವಾಗತ, ರೋಗಿಯೇ!",

        "subtitle":
            "ನಿಮ್ಮ ವೈಯಕ್ತಿಕ ಆರೋಗ್ಯ ಪೋರ್ಟಲ್",

        "profile":
            "👤 ನನ್ನ ಪ್ರೊಫೈಲ್",

        "profile_desc":
            "ನಿಮ್ಮ ನೋಂದಾಯಿತ ಆರೋಗ್ಯ ಮಾಹಿತಿಯನ್ನು ವೀಕ್ಷಿಸಿ.",

        "name":
            "ಹೆಸರು",

        "age":
            "ವಯಸ್ಸು",

        "gender":
            "ಲಿಂಗ",

        "hospital":
            "ಆಸ್ಪತ್ರೆ",

        "doctor":
            "ವೈದ್ಯರು",

        "state":
            "ರಾಜ್ಯ",

        "risk":
            "📊 ನನ್ನ ಆರೋಗ್ಯ ಅಪಾಯ",

        "risk_desc":
            "ನಿಮ್ಮ ಇತ್ತೀಚಿನ ಆರೋಗ್ಯ ಅಪಾಯ ಮೌಲ್ಯಮಾಪನವನ್ನು ವೀಕ್ಷಿಸಿ.",

        "current_risk":
            "ಪ್ರಸ್ತುತ ಅಪಾಯದ ಮಟ್ಟ",

        "probability":
            "30 ದಿನಗಳಲ್ಲಿ ಮರುಆಸ್ಪತ್ರೆ ಪ್ರವೇಶದ ಸಾಧ್ಯತೆ",

        "summary":
            "🧠 ವೈದ್ಯಕೀಯ ಸಾರಾಂಶ",

        "recommendations":
            "💡 ನನ್ನ ಶಿಫಾರಸುಗಳು",

        "reports":
            "📄 ನನ್ನ ವರದಿಗಳು",

        "security":
            "🔒 ನಿಮ್ಮ ಆರೋಗ್ಯ ಮಾಹಿತಿಯನ್ನು ನಿಮ್ಮ ಖಾತೆಯಲ್ಲಿ ಮಾತ್ರ ಸುರಕ್ಷಿತವಾಗಿ ಪ್ರದರ್ಶಿಸಲಾಗುತ್ತದೆ.",

        "doctor_notice":
            "ವೈದ್ಯಕೀಯ ನಿರ್ಧಾರಗಳಿಗಾಗಿ ನಿಮ್ಮ ಆರೋಗ್ಯ ತಜ್ಞರನ್ನು ಸಂಪರ್ಕಿಸಿ.",

        "no_prediction":
            "ನಿಮ್ಮ Patient ID ಗಾಗಿ ಯಾವುದೇ ಮುನ್ಸೂಚನೆ ಮಾಹಿತಿ ಲಭ್ಯವಿಲ್ಲ.",

        "no_report":
            "ನಿಮಗಾಗಿ ಇನ್ನೂ ಯಾವುದೇ ವರದಿಯನ್ನು ರಚಿಸಲಾಗಿಲ್ಲ."
    },

    "Hindi": {

        "welcome":
            "👤 स्वागत है, मरीज!",

        "subtitle":
            "आपका व्यक्तिगत स्वास्थ्य पोर्टल",

        "profile":
            "👤 मेरी प्रोफ़ाइल",

        "profile_desc":
            "अपनी पंजीकृत स्वास्थ्य जानकारी देखें।",

        "name":
            "नाम",

        "age":
            "आयु",

        "gender":
            "लिंग",

        "hospital":
            "अस्पताल",

        "doctor":
            "डॉक्टर",

        "state":
            "राज्य",

        "risk":
            "📊 मेरा स्वास्थ्य जोखिम",

        "risk_desc":
            "अपना नवीनतम स्वास्थ्य जोखिम मूल्यांकन देखें।",

        "current_risk":
            "वर्तमान जोखिम स्तर",

        "probability":
            "30 दिनों में पुनः अस्पताल में भर्ती होने की संभावना",

        "summary":
            "🧠 चिकित्सा सारांश",

        "recommendations":
            "💡 मेरी सिफारिशें",

        "reports":
            "📄 मेरी रिपोर्ट",

        "security":
            "🔒 आपकी स्वास्थ्य जानकारी केवल आपके खाते में सुरक्षित रूप से प्रदर्शित की जाती है।",

        "doctor_notice":
            "चिकित्सकीय निर्णयों के लिए अपने स्वास्थ्य विशेषज्ञ से परामर्श करें।",

        "no_prediction":
            "आपके Patient ID के लिए कोई पूर्वानुमान जानकारी उपलब्ध नहीं है।",

        "no_report":
            "आपके लिए अभी तक कोई रिपोर्ट तैयार नहीं की गई है।"
    },

    "Tamil": {

        "welcome":
            "👤 வரவேற்கிறோம், நோயாளியே!",

        "subtitle":
            "உங்கள் தனிப்பட்ட சுகாதார போர்டல்",

        "profile":
            "👤 எனது சுயவிவரம்",

        "profile_desc":
            "உங்கள் பதிவு செய்யப்பட்ட சுகாதார தகவல்களைப் பார்க்கவும்.",

        "name":
            "பெயர்",

        "age":
            "வயது",

        "gender":
            "பாலினம்",

        "hospital":
            "மருத்துவமனை",

        "doctor":
            "மருத்துவர்",

        "state":
            "மாநிலம்",

        "risk":
            "📊 எனது சுகாதார ஆபத்து",

        "risk_desc":
            "உங்கள் சமீபத்திய சுகாதார ஆபத்து மதிப்பீட்டைப் பார்க்கவும்.",

        "current_risk":
            "தற்போதைய ஆபத்து நிலை",

        "probability":
            "30 நாட்களில் மீண்டும் மருத்துவமனையில் சேர்க்கப்படும் வாய்ப்பு",

        "summary":
            "🧠 மருத்துவ சுருக்கம்",

        "recommendations":
            "💡 எனது பரிந்துரைகள்",

        "reports":
            "📄 எனது அறிக்கைகள்",

        "security":
            "🔒 உங்கள் சுகாதார தகவல்கள் உங்கள் கணக்கில் மட்டும் பாதுகாப்பாகக் காட்டப்படுகின்றன.",

        "doctor_notice":
            "மருத்துவ முடிவுகளுக்கு உங்கள் சுகாதார நிபுணரை அணுகவும்.",

        "no_prediction":
            "உங்கள் Patient ID-க்கு எந்த முன்கணிப்பு தகவலும் கிடைக்கவில்லை.",

        "no_report":
            "உங்களுக்காக இன்னும் எந்த அறிக்கையும் உருவாக்கப்படவில்லை."
    },

    "Telugu": {

        "welcome":
            "👤 స్వాగతం, రోగి!",

        "subtitle":
            "మీ వ్యక్తిగత ఆరోగ్య పోర్టల్",

        "profile":
            "👤 నా ప్రొఫైల్",

        "profile_desc":
            "మీ నమోదైన ఆరోగ్య సమాచారాన్ని చూడండి.",

        "name":
            "పేరు",

        "age":
            "వయస్సు",

        "gender":
            "లింగం",

        "hospital":
            "ఆసుపత్రి",

        "doctor":
            "వైద్యుడు",

        "state":
            "రాష్ట్రం",

        "risk":
            "📊 నా ఆరోగ్య ప్రమాదం",

        "risk_desc":
            "మీ తాజా ఆరోగ్య ప్రమాద అంచనాను చూడండి.",

        "current_risk":
            "ప్రస్తుత ప్రమాద స్థాయి",

        "probability":
            "30 రోజుల్లో తిరిగి ఆసుపత్రిలో చేరే అవకాశం",

        "summary":
            "🧠 వైద్య సారాంశం",

        "recommendations":
            "💡 నా సిఫార్సులు",

        "reports":
            "📄 నా నివేదికలు",

        "security":
            "🔒 మీ ఆరోగ్య సమాచారం మీ ఖాతాలో మాత్రమే సురక్షితంగా ప్రదర్శించబడుతుంది.",

        "doctor_notice":
            "వైద్య నిర్ణయాల కోసం మీ ఆరోగ్య నిపుణుడిని సంప్రదించండి.",

        "no_prediction":
            "మీ Patient ID కోసం ఎటువంటి అంచనా సమాచారం అందుబాటులో లేదు.",

        "no_report":
            "మీ కోసం ఇంకా ఎటువంటి నివేదిక రూపొందించబడలేదు."
    },

    "Malayalam": {

        "welcome":
            "👤 സ്വാഗതം, രോഗിയേ!",

        "subtitle":
            "നിങ്ങളുടെ വ്യക്തിഗത ആരോഗ്യ പോർട്ടൽ",

        "profile":
            "👤 എന്റെ പ്രൊഫൈൽ",

        "profile_desc":
            "നിങ്ങളുടെ രജിസ്റ്റർ ചെയ്ത ആരോഗ്യ വിവരങ്ങൾ കാണുക.",

        "name":
            "പേര്",

        "age":
            "പ്രായം",

        "gender":
            "ലിംഗം",

        "hospital":
            "ആശുപത്രി",

        "doctor":
            "ഡോക്ടർ",

        "state":
            "സംസ്ഥാനം",

        "risk":
            "📊 എന്റെ ആരോഗ്യ അപകടസാധ്യത",

        "risk_desc":
            "നിങ്ങളുടെ ഏറ്റവും പുതിയ ആരോഗ്യ അപകട വിലയിരുത്തൽ കാണുക.",

        "current_risk":
            "നിലവിലെ അപകട നില",

        "probability":
            "30 ദിവസത്തിനുള്ളിൽ വീണ്ടും ആശുപത്രിയിൽ പ്രവേശിക്കാനുള്ള സാധ്യത",

        "summary":
            "🧠 മെഡിക്കൽ സംഗ്രഹം",

        "recommendations":
            "💡 എന്റെ ശുപാർശകൾ",

        "reports":
            "📄 എന്റെ റിപ്പോർട്ടുകൾ",

        "security":
            "🔒 നിങ്ങളുടെ ആരോഗ്യ വിവരങ്ങൾ നിങ്ങളുടെ അക്കൗണ്ടിൽ മാത്രം സുരക്ഷിതമായി പ്രദർശിപ്പിക്കുന്നു.",

        "doctor_notice":
            "മെഡിക്കൽ തീരുമാനങ്ങൾക്കായി നിങ്ങളുടെ ആരോഗ്യ വിദഗ്ധനെ സമീപിക്കുക.",

        "no_prediction":
            "നിങ്ങളുടെ Patient ID-യ്ക്ക് വിവരങ്ങളൊന്നും കണ്ടെത്താനായില്ല.",

        "no_report":
            "നിങ്ങൾക്കായി ഇതുവരെ റിപ്പോർട്ടുകളൊന്നും തയ്യാറാക്കിയിട്ടില്ല."
    }
}


T = TEXT.get(
    language,
    TEXT["English"]
)


# =========================================================
# PATIENT DATA
# =========================================================

patient_file = "patients.csv"

patient = None

if os.path.exists(patient_file):

    try:

        patients = pd.read_csv(
            patient_file
        )

        patients["patient_id"] = (
            patients["patient_id"]
            .astype(str)
            .str.strip()
        )

        matching = patients[
            patients["patient_id"]
            == str(patient_id).strip()
        ]

        if not matching.empty:

            patient = matching.iloc[0]

    except Exception as e:

        st.error(
            f"Unable to read patient data: {e}"
        )


# =========================================================
# PREDICTION DATA
# =========================================================

prediction = None

prediction_file = "prediction_results.csv"

if os.path.exists(prediction_file):

    try:

        predictions = pd.read_csv(
            prediction_file
        )

        predictions["patient_id"] = (
            predictions["patient_id"]
            .astype(str)
            .str.strip()
        )

        matching_prediction = predictions[
            predictions["patient_id"]
            == str(patient_id).strip()
        ]

        if not matching_prediction.empty:

            prediction = (
                matching_prediction.iloc[-1]
            )

    except Exception:

        prediction = None


# =========================================================
# PATIENT HEADER
# =========================================================

st.title(T["welcome"])

st.subheader(
    T["subtitle"]
)

st.divider()


# =========================================================
# PATIENT PROFILE
# =========================================================

st.header(
    T["profile"]
)

st.write(
    T["profile_desc"]
)

if patient is not None:

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            T["name"],
            str(
                patient.get(
                    "name",
                    patient_id
                )
            )
        )

        st.metric(
            T["age"],
            str(
                patient.get(
                    "age",
                    "N/A"
                )
            )
        )

    with col2:

        st.metric(
            T["gender"],
            str(
                patient.get(
                    "gender",
                    "N/A"
                )
            )
        )

        st.metric(
            T["state"],
            str(
                patient.get(
                    "state",
                    "N/A"
                )
            )
        )

    with col3:

        st.metric(
            T["hospital"],
            str(
                patient.get(
                    "hospital",
                    "CareWatch General Hospital"
                )
            )
        )

        st.metric(
            T["doctor"],
            str(
                patient.get(
                    "doctor",
                    "Dr. Assigned"
                )
            )
        )

else:

    st.warning(
        T["no_prediction"]
    )


st.divider()


# =========================================================
# RISK ASSESSMENT
# =========================================================

st.header(
    T["risk"]
)

st.write(
    T["risk_desc"]
)

if prediction is not None:

    risk_level = str(
        prediction.get(
            "risk_level",
            "Unknown"
        )
    )

    try:

        probability = float(
            prediction.get(
                "risk_probability",
                0
            )
        )

    except Exception:

        probability = 0.0


    if risk_level.lower() == "high":

        st.error(
            "🔴 " +
            T["current_risk"] +
            ": HIGH"
        )

    elif risk_level.lower() == "moderate":

        st.warning(
            "🟡 " +
            T["current_risk"] +
            ": MODERATE"
        )

    else:

        st.success(
            "🟢 " +
            T["current_risk"] +
            ": LOW"
        )


    st.metric(
        T["probability"],
        f"{probability * 100:.2f}%"
    )


else:

    st.info(
        T["no_prediction"]
    )


# =========================================================
# MEDICAL SUMMARY
# =========================================================

st.divider()

st.header(
    T["summary"]
)

if prediction is not None:

    summary = str(
        prediction.get(
            "clinical_summary",
            "No clinical summary available."
        )
    )

    st.info(
        summary
    )

else:

    st.info(
        T["no_prediction"]
    )


# =========================================================
# RECOMMENDATIONS
# =========================================================

st.divider()

st.header(
    T["recommendations"]
)

if prediction is not None:

    risk_level = str(
        prediction.get(
            "risk_level",
            "Low"
        )
    ).lower()

    if risk_level == "high":

        recommendations = [

            "Discuss the readmission risk assessment with your doctor.",

            "Arrange appropriate follow-up care.",

            "Continue close monitoring of your health condition."

        ]

    elif risk_level == "moderate":

        recommendations = [

            "Review your health risk factors with your doctor.",

            "Attend scheduled follow-up appointments.",

            "Continue regular health monitoring."

        ]

    else:

        recommendations = [

            "Continue following your healthcare plan.",

            "Attend scheduled follow-up appointments.",

            "Maintain regular health monitoring."

        ]

    for recommendation in recommendations:

        st.success(
            f"✅ {recommendation}"
        )

else:

    st.info(
        T["no_prediction"]
    )


# =========================================================
# REPORTS
# =========================================================

st.divider()

st.header(
    T["reports"]
)

report_file = "patient_reports.json"

reports_found = False

if os.path.exists(report_file):

    try:

        with open(
            report_file,
            "r",
            encoding="utf-8"
        ) as f:

            reports = json.load(f)

        # Patient-specific report

        patient_report = reports.get(
            str(patient_id)
        )

        if patient_report:

            reports_found = True

            generated_at = patient_report.get(
                "generated_at",
                "N/A"
            )

            risk = patient_report.get(
                "risk_level",
                "N/A"
            )

            report_probability = patient_report.get(
                "probability",
                0
            )

            report_summary = patient_report.get(
                "clinical_summary",
                "N/A"
            )

            report_recommendations = patient_report.get(
                "recommendations",
                []
            )

            with st.expander(
                f"📄 Report - {generated_at}",
                expanded=True
            ):

                st.write(
                    f"**Prepared:** {generated_at}"
                )

                st.write(
                    f"**Risk Level:** {risk}"
                )

                try:

                    st.write(
                        "**Readmission Probability:** "
                        f"{float(report_probability) * 100:.2f}%"
                    )

                except Exception:

                    st.write(
                        "**Readmission Probability:** N/A"
                    )

                st.write(
                    "**Medical Summary:**"
                )

                st.info(
                    str(report_summary)
                )

                st.write(
                    "**Recommendations:**"
                )

                for recommendation in report_recommendations:

                    st.write(
                        f"✅ {recommendation}"
                    )

    except Exception as e:

        st.error(
            f"Unable to load reports: {e}"
        )


if not reports_found:

    st.info(
        T["no_report"]
    )


# =========================================================
# SECURITY NOTICE
# =========================================================

st.divider()

st.info(
    "🔒 " + T["security"]
)

st.caption(
    "⚕️ " + T["doctor_notice"]
)