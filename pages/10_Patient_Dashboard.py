import streamlit as st
import pandas as pd
import os
import json
from datetime import datetime

from auth import require_login, require_role

# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="CareWatch-AI | Patient Portal",
    page_icon="🩺",
    layout="wide"
)

# ============================================================
# AUTHENTICATION
# ============================================================

require_login()
require_role("Patient")

# ============================================================
# LANGUAGE
# ============================================================

LANGUAGES = [
    "English",
    "Tamil",
    "Hindi",
    "Telugu",
    "Kannada",
    "Malayalam"
]

# Keep language persistent
if "patient_language" not in st.session_state:
    st.session_state.patient_language = st.session_state.get(
        "language",
        "English"
    )

current_language = st.session_state.patient_language

selected_language = st.selectbox(
    "🌐 Language",
    LANGUAGES,
    index=LANGUAGES.index(current_language)
)

if selected_language != current_language:
    st.session_state.patient_language = selected_language
    st.session_state.language = selected_language
    st.rerun()

L = current_language

# ============================================================
# COMPLETE PATIENT TRANSLATIONS
# ============================================================

TEXT = {

"English": {
    "app_name": "CAREWATCH-AI",
    "subtitle": "AI-Based Hospital Readmission Support",
    "welcome": "Welcome, Patient!",
    "portal": "Your Personal Health Portal",
    "profile": "My Profile",
    "profile_desc": "Your registered health information.",
    "patient_id": "Patient ID",
    "age": "Age",
    "gender": "Gender",
    "state": "State",
    "insurance": "Insurance",
    "bpl": "BPL Card",
    "comorbidities": "Comorbidities",
    "previous": "Previous Admissions",

    "risk": "My Health Risk",
    "risk_desc": "Your latest AI-based hospital readmission risk assessment.",
    "risk_level": "Current Risk Level",
    "probability": "30-Day Readmission Probability",

    "high": "HIGH RISK",
    "moderate": "MODERATE RISK",
    "low": "LOW RISK",

    "summary": "Medical Summary",
    "recommendations": "My Recommendations",

    "rec1": "Discuss the assessment with your doctor.",
    "rec2": "Attend your scheduled follow-up appointments.",
    "rec3": "Continue regular health monitoring.",

    "report": "My Health Report",
    "report_desc": "Download your latest health and AI assessment as a PDF.",
    "download": "Download PDF Report",
    "no_report": "No prediction report is available yet.",
    "go_prediction": "Please ask your doctor to complete a readmission risk assessment.",

    "secure": "Your health information is securely displayed only for your account.",
    "doctor_notice": "Please consult your healthcare professional for medical decisions.",
    "logout": "Logout",

    "risk_high_summary":
        "The AI model indicates a higher risk of hospital readmission within 30 days. Please discuss the assessment with your healthcare professional.",

    "risk_moderate_summary":
        "The AI model indicates a moderate risk of hospital readmission within 30 days. Additional clinical monitoring may be appropriate.",

    "risk_low_summary":
        "The AI model indicates a lower risk of hospital readmission within 30 days.",

    "report_title": "CareWatch-AI Patient Health Report",
    "generated": "Generated",
    "risk_level_report": "Risk Level",
    "readmission_probability": "Readmission Probability",
    "medical_summary": "Medical Summary",
    "recommendation_title": "Recommendations",
    "confidential": "Confidential Patient Health Information"
},

"Tamil": {
    "app_name": "CAREWATCH-AI",
    "subtitle": "செயற்கை நுண்ணறிவு அடிப்படையிலான மருத்துவமனை மீள்சேர்க்கை ஆதரவு",
    "welcome": "வரவேற்கிறோம், நோயாளியே!",
    "portal": "உங்கள் தனிப்பட்ட சுகாதார போர்டல்",
    "profile": "எனது சுயவிவரம்",
    "profile_desc": "உங்கள் பதிவு செய்யப்பட்ட சுகாதார தகவல்கள்.",
    "patient_id": "நோயாளர் அடையாள எண்",
    "age": "வயது",
    "gender": "பாலினம்",
    "state": "மாநிலம்",
    "insurance": "காப்பீடு",
    "bpl": "BPL அட்டை",
    "comorbidities": "இணைநோய்கள்",
    "previous": "முந்தைய மருத்துவமனை அனுமதிகள்",

    "risk": "எனது சுகாதார ஆபத்து",
    "risk_desc": "உங்கள் சமீபத்திய செயற்கை நுண்ணறிவு அடிப்படையிலான மருத்துவமனை மீள்சேர்க்கை ஆபத்து மதிப்பீடு.",
    "risk_level": "தற்போதைய ஆபத்து நிலை",
    "probability": "30 நாட்களில் மீள்சேர்க்கை வாய்ப்பு",

    "high": "அதிக ஆபத்து",
    "moderate": "மிதமான ஆபத்து",
    "low": "குறைந்த ஆபத்து",

    "summary": "மருத்துவ சுருக்கம்",
    "recommendations": "எனது பரிந்துரைகள்",

    "rec1": "இந்த மதிப்பீட்டை உங்கள் மருத்துவருடன் கலந்துரையாடுங்கள்.",
    "rec2": "திட்டமிடப்பட்ட பின்தொடர் மருத்துவ சந்திப்புகளில் கலந்து கொள்ளுங்கள்.",
    "rec3": "தொடர்ந்து உங்கள் உடல்நிலையை கண்காணிக்கவும்.",

    "report": "எனது சுகாதார அறிக்கை",
    "report_desc": "உங்கள் சமீபத்திய சுகாதார மற்றும் செயற்கை நுண்ணறிவு மதிப்பீட்டை PDF ஆக பதிவிறக்கவும்.",
    "download": "PDF அறிக்கையைப் பதிவிறக்கவும்",
    "no_report": "இதுவரை எந்த ஆபத்து மதிப்பீட்டு அறிக்கையும் இல்லை.",
    "go_prediction": "மீள்சேர்க்கை ஆபத்து மதிப்பீட்டை முடிக்க உங்கள் மருத்துவரை அணுகவும்.",

    "secure": "உங்கள் சுகாதார தகவல்கள் உங்கள் கணக்கிற்காக மட்டும் பாதுகாப்பாகக் காட்டப்படுகின்றன.",
    "doctor_notice": "மருத்துவ முடிவுகளுக்கு உங்கள் சுகாதார நிபுணரை அணுகவும்.",
    "logout": "வெளியேறு",

    "risk_high_summary":
        "அடுத்த 30 நாட்களில் மருத்துவமனையில் மீண்டும் அனுமதிக்கப்படும் ஆபத்து அதிகமாக இருப்பதாக செயற்கை நுண்ணறிவு மாதிரி காட்டுகிறது. இந்த மதிப்பீட்டை உங்கள் சுகாதார நிபுணருடன் கலந்துரையாடுங்கள்.",

    "risk_moderate_summary":
        "அடுத்த 30 நாட்களில் மருத்துவமனையில் மீண்டும் அனுமதிக்கப்படும் ஆபத்து மிதமாக இருப்பதாக செயற்கை நுண்ணறிவு மாதிரி காட்டுகிறது. கூடுதல் மருத்துவ கண்காணிப்பு பொருத்தமானதாக இருக்கலாம்.",

    "risk_low_summary":
        "அடுத்த 30 நாட்களில் மருத்துவமனையில் மீண்டும் அனுமதிக்கப்படும் ஆபத்து குறைவாக இருப்பதாக செயற்கை நுண்ணறிவு மாதிரி காட்டுகிறது.",

    "report_title": "CareWatch-AI நோயாளர் சுகாதார அறிக்கை",
    "generated": "உருவாக்கப்பட்ட நேரம்",
    "risk_level_report": "ஆபத்து நிலை",
    "readmission_probability": "மீள்சேர்க்கை வாய்ப்பு",
    "medical_summary": "மருத்துவ சுருக்கம்",
    "recommendation_title": "பரிந்துரைகள்",
    "confidential": "ரகசிய நோயாளர் சுகாதார தகவல்"
},

"Hindi": {
    "app_name": "CAREWATCH-AI",
    "subtitle": "AI आधारित अस्पताल पुनः भर्ती सहायता",
    "welcome": "स्वागत है, रोगी!",
    "portal": "आपका व्यक्तिगत स्वास्थ्य पोर्टल",
    "profile": "मेरी प्रोफ़ाइल",
    "profile_desc": "आपकी पंजीकृत स्वास्थ्य जानकारी।",
    "patient_id": "रोगी पहचान संख्या",
    "age": "आयु",
    "gender": "लिंग",
    "state": "राज्य",
    "insurance": "बीमा",
    "bpl": "BPL कार्ड",
    "comorbidities": "सह-रोग",
    "previous": "पिछली अस्पताल भर्तियां",

    "risk": "मेरा स्वास्थ्य जोखिम",
    "risk_desc": "आपका नवीनतम AI आधारित अस्पताल पुनः भर्ती जोखिम मूल्यांकन।",
    "risk_level": "वर्तमान जोखिम स्तर",
    "probability": "30 दिनों में पुनः भर्ती की संभावना",

    "high": "उच्च जोखिम",
    "moderate": "मध्यम जोखिम",
    "low": "कम जोखिम",

    "summary": "चिकित्सीय सारांश",
    "recommendations": "मेरी सिफारिशें",

    "rec1": "इस मूल्यांकन पर अपने डॉक्टर से चर्चा करें।",
    "rec2": "निर्धारित फॉलो-अप अपॉइंटमेंट में शामिल हों।",
    "rec3": "अपने स्वास्थ्य की नियमित निगरानी जारी रखें।",

    "report": "मेरी स्वास्थ्य रिपोर्ट",
    "report_desc": "अपनी नवीनतम स्वास्थ्य और AI मूल्यांकन रिपोर्ट PDF के रूप में डाउनलोड करें।",
    "download": "PDF रिपोर्ट डाउनलोड करें",
    "no_report": "अभी कोई जोखिम मूल्यांकन रिपोर्ट उपलब्ध नहीं है।",
    "go_prediction": "जोखिम मूल्यांकन पूरा करने के लिए अपने डॉक्टर से संपर्क करें।",

    "secure": "आपकी स्वास्थ्य जानकारी केवल आपके खाते के लिए सुरक्षित रूप से प्रदर्शित की जाती है।",
    "doctor_notice": "चिकित्सीय निर्णयों के लिए अपने स्वास्थ्य विशेषज्ञ से परामर्श करें।",
    "logout": "लॉग आउट",

    "risk_high_summary":
        "AI मॉडल अगले 30 दिनों में अस्पताल में पुनः भर्ती होने का अधिक जोखिम दर्शाता है। कृपया इस मूल्यांकन पर अपने स्वास्थ्य विशेषज्ञ से चर्चा करें।",

    "risk_moderate_summary":
        "AI मॉडल अगले 30 दिनों में अस्पताल में पुनः भर्ती होने का मध्यम जोखिम दर्शाता है। अतिरिक्त चिकित्सीय निगरानी उचित हो सकती है।",

    "risk_low_summary":
        "AI मॉडल अगले 30 दिनों में अस्पताल में पुनः भर्ती होने का कम जोखिम दर्शाता है।",

    "report_title": "CareWatch-AI रोगी स्वास्थ्य रिपोर्ट",
    "generated": "बनाया गया",
    "risk_level_report": "जोखिम स्तर",
    "readmission_probability": "पुनः भर्ती की संभावना",
    "medical_summary": "चिकित्सीय सारांश",
    "recommendation_title": "सिफारिशें",
    "confidential": "गोपनीय रोगी स्वास्थ्य जानकारी"
},

"Telugu": {
    "app_name": "CAREWATCH-AI",
    "subtitle": "కృత్రిమ మేధస్సు ఆధారిత ఆసుపత్రి పునఃచేరిక సహాయం",
    "welcome": "స్వాగతం, రోగి!",
    "portal": "మీ వ్యక్తిగత ఆరోగ్య పోర్టల్",
    "profile": "నా వివరాలు",
    "profile_desc": "మీ నమోదు చేసిన ఆరోగ్య సమాచారం.",
    "patient_id": "రోగి గుర్తింపు సంఖ్య",
    "age": "వయస్సు",
    "gender": "లింగం",
    "state": "రాష్ట్రం",
    "insurance": "బీమా",
    "bpl": "BPL కార్డు",
    "comorbidities": "సహవ్యాధులు",
    "previous": "మునుపటి ఆసుపత్రి చేరికలు",

    "risk": "నా ఆరోగ్య ప్రమాదం",
    "risk_desc": "మీ తాజా AI ఆధారిత ఆసుపత్రి పునఃచేరిక ప్రమాద అంచనా.",
    "risk_level": "ప్రస్తుత ప్రమాద స్థాయి",
    "probability": "30 రోజుల్లో పునఃచేరిక అవకాశం",

    "high": "అధిక ప్రమాదం",
    "moderate": "మధ్యస్థ ప్రమాదం",
    "low": "తక్కువ ప్రమాదం",

    "summary": "వైద్య సారాంశం",
    "recommendations": "నా సూచనలు",

    "rec1": "ఈ అంచనాను మీ వైద్యునితో చర్చించండి.",
    "rec2": "నిర్దేశించిన ఫాలో-అప్ అపాయింట్‌మెంట్లకు హాజరుకండి.",
    "rec3": "మీ ఆరోగ్యాన్ని క్రమం తప్పకుండా పర్యవేక్షించండి.",

    "report": "నా ఆరోగ్య నివేదిక",
    "report_desc": "మీ తాజా ఆరోగ్య మరియు AI అంచనా నివేదికను PDFగా డౌన్‌లోడ్ చేయండి.",
    "download": "PDF నివేదికను డౌన్‌లోడ్ చేయండి",
    "no_report": "ఇంకా ఎటువంటి ప్రమాద అంచనా నివేదిక అందుబాటులో లేదు.",
    "go_prediction": "ప్రమాద అంచనాను పూర్తి చేయడానికి మీ వైద్యుడిని సంప్రదించండి.",

    "secure": "మీ ఆరోగ్య సమాచారం మీ ఖాతాకు మాత్రమే సురక్షితంగా చూపబడుతుంది.",
    "doctor_notice": "వైద్య నిర్ణయాల కోసం మీ ఆరోగ్య నిపుణుడిని సంప్రదించండి.",
    "logout": "లాగ్ అవుట్",

    "risk_high_summary":
        "తదుపరి 30 రోజుల్లో ఆసుపత్రిలో తిరిగి చేరే ప్రమాదం ఎక్కువగా ఉందని AI నమూనా సూచిస్తుంది. ఈ అంచనాను మీ ఆరోగ్య నిపుణుడితో చర్చించండి.",

    "risk_moderate_summary":
        "తదుపరి 30 రోజుల్లో ఆసుపత్రిలో తిరిగి చేరే ప్రమాదం మధ్యస్థంగా ఉందని AI నమూనా సూచిస్తుంది. అదనపు వైద్య పర్యవేక్షణ అవసరం కావచ్చు.",

    "risk_low_summary":
        "తదుపరి 30 రోజుల్లో ఆసుపత్రిలో తిరిగి చేరే ప్రమాదం తక్కువగా ఉందని AI నమూనా సూచిస్తుంది.",

    "report_title": "CareWatch-AI రోగి ఆరోగ్య నివేదిక",
    "generated": "రూపొందించిన సమయం",
    "risk_level_report": "ప్రమాద స్థాయి",
    "readmission_probability": "పునఃచేరిక అవకాశం",
    "medical_summary": "వైద్య సారాంశం",
    "recommendation_title": "సూచనలు",
    "confidential": "రహస్య రోగి ఆరోగ్య సమాచారం"
},

"Kannada": {
    "app_name": "CAREWATCH-AI",
    "subtitle": "ಕೃತಕ ಬುದ್ಧಿಮತ್ತೆ ಆಧಾರಿತ ಆಸ್ಪತ್ರೆ ಮರುದಾಖಲಾತಿ ಸಹಾಯ",
    "welcome": "ಸ್ವಾಗತ, ರೋಗಿಯೇ!",
    "portal": "ನಿಮ್ಮ ವೈಯಕ್ತಿಕ ಆರೋಗ್ಯ ಪೋರ್ಟಲ್",
    "profile": "ನನ್ನ ವಿವರಗಳು",
    "profile_desc": "ನಿಮ್ಮ ನೋಂದಾಯಿತ ಆರೋಗ್ಯ ಮಾಹಿತಿ.",
    "patient_id": "ರೋಗಿ ಗುರುತು ಸಂಖ್ಯೆ",
    "age": "ವಯಸ್ಸು",
    "gender": "ಲಿಂಗ",
    "state": "ರಾಜ್ಯ",
    "insurance": "ವಿಮೆ",
    "bpl": "BPL ಕಾರ್ಡ್",
    "comorbidities": "ಸಹರೋಗಗಳು",
    "previous": "ಹಿಂದಿನ ಆಸ್ಪತ್ರೆ ದಾಖಲಾತಿಗಳು",

    "risk": "ನನ್ನ ಆರೋಗ್ಯ ಅಪಾಯ",
    "risk_desc": "ನಿಮ್ಮ ಇತ್ತೀಚಿನ AI ಆಧಾರಿತ ಆಸ್ಪತ್ರೆ ಮರುದಾಖಲಾತಿ ಅಪಾಯ ಮೌಲ್ಯಮಾಪನ.",
    "risk_level": "ಪ್ರಸ್ತುತ ಅಪಾಯ ಮಟ್ಟ",
    "probability": "30 ದಿನಗಳಲ್ಲಿ ಮರುದಾಖಲಾತಿ ಸಾಧ್ಯತೆ",

    "high": "ಹೆಚ್ಚಿನ ಅಪಾಯ",
    "moderate": "ಮಧ್ಯಮ ಅಪಾಯ",
    "low": "ಕಡಿಮೆ ಅಪಾಯ",

    "summary": "ವೈದ್ಯಕೀಯ ಸಾರಾಂಶ",
    "recommendations": "ನನ್ನ ಶಿಫಾರಸುಗಳು",

    "rec1": "ಈ ಮೌಲ್ಯಮಾಪನವನ್ನು ನಿಮ್ಮ ವೈದ್ಯರೊಂದಿಗೆ ಚರ್ಚಿಸಿ.",
    "rec2": "ನಿಗದಿತ ಅನುಸರಣೆ ಭೇಟಿಗಳಿಗೆ ಹಾಜರಾಗಿರಿ.",
    "rec3": "ನಿಮ್ಮ ಆರೋಗ್ಯವನ್ನು ನಿಯಮಿತವಾಗಿ ಮೇಲ್ವಿಚಾರಣೆ ಮಾಡಿ.",

    "report": "ನನ್ನ ಆರೋಗ್ಯ ವರದಿ",
    "report_desc": "ನಿಮ್ಮ ಇತ್ತೀಚಿನ ಆರೋಗ್ಯ ಮತ್ತು AI ಮೌಲ್ಯಮಾಪನವನ್ನು PDF ಆಗಿ ಡೌನ್‌ಲೋಡ್ ಮಾಡಿ.",
    "download": "PDF ವರದಿ ಡೌನ್‌ಲೋಡ್ ಮಾಡಿ",
    "no_report": "ಇನ್ನೂ ಯಾವುದೇ ಅಪಾಯ ಮೌಲ್ಯಮಾಪನ ವರದಿ ಲಭ್ಯವಿಲ್ಲ.",
    "go_prediction": "ಅಪಾಯ ಮೌಲ್ಯಮಾಪನವನ್ನು ಪೂರ್ಣಗೊಳಿಸಲು ನಿಮ್ಮ ವೈದ್ಯರನ್ನು ಸಂಪರ್ಕಿಸಿ.",

    "secure": "ನಿಮ್ಮ ಆರೋಗ್ಯ ಮಾಹಿತಿಯನ್ನು ನಿಮ್ಮ ಖಾತೆಗೆ ಮಾತ್ರ ಸುರಕ್ಷಿತವಾಗಿ ಪ್ರದರ್ಶಿಸಲಾಗುತ್ತದೆ.",
    "doctor_notice": "ವೈದ್ಯಕೀಯ ನಿರ್ಧಾರಗಳಿಗಾಗಿ ನಿಮ್ಮ ಆರೋಗ್ಯ ತಜ್ಞರನ್ನು ಸಂಪರ್ಕಿಸಿ.",
    "logout": "ಲಾಗ್ ಔಟ್",

    "risk_high_summary":
        "ಮುಂದಿನ 30 ದಿನಗಳಲ್ಲಿ ಆಸ್ಪತ್ರೆಯಲ್ಲಿ ಮರುದಾಖಲಾಗುವ ಅಪಾಯ ಹೆಚ್ಚಾಗಿದೆ ಎಂದು AI ಮಾದರಿ ಸೂಚಿಸುತ್ತದೆ. ಈ ಮೌಲ್ಯಮಾಪನವನ್ನು ನಿಮ್ಮ ಆರೋಗ್ಯ ತಜ್ಞರೊಂದಿಗೆ ಚರ್ಚಿಸಿ.",

    "risk_moderate_summary":
        "ಮುಂದಿನ 30 ದಿನಗಳಲ್ಲಿ ಆಸ್ಪತ್ರೆಯಲ್ಲಿ ಮರುದಾಖಲಾಗುವ ಅಪಾಯ ಮಧ್ಯಮವಾಗಿದೆ ಎಂದು AI ಮಾದರಿ ಸೂಚಿಸುತ್ತದೆ. ಹೆಚ್ಚುವರಿ ವೈದ್ಯಕೀಯ ಮೇಲ್ವಿಚಾರಣೆ ಅಗತ್ಯವಾಗಬಹುದು.",

    "risk_low_summary":
        "ಮುಂದಿನ 30 ದಿನಗಳಲ್ಲಿ ಆಸ್ಪತ್ರೆಯಲ್ಲಿ ಮರುದಾಖಲಾಗುವ ಅಪಾಯ ಕಡಿಮೆಯಾಗಿದೆ ಎಂದು AI ಮಾದರಿ ಸೂಚಿಸುತ್ತದೆ.",

    "report_title": "CareWatch-AI ರೋಗಿ ಆರೋಗ್ಯ ವರದಿ",
    "generated": "ರಚಿಸಿದ ಸಮಯ",
    "risk_level_report": "ಅಪಾಯ ಮಟ್ಟ",
    "readmission_probability": "ಮರುದಾಖಲಾತಿ ಸಾಧ್ಯತೆ",
    "medical_summary": "ವೈದ್ಯಕೀಯ ಸಾರಾಂಶ",
    "recommendation_title": "ಶಿಫಾರಸುಗಳು",
    "confidential": "ಗೌಪ್ಯ ರೋಗಿ ಆರೋಗ್ಯ ಮಾಹಿತಿ"
},

"Malayalam": {
    "app_name": "CAREWATCH-AI",
    "subtitle": "കൃത്രിമ ബുദ്ധി അടിസ്ഥാനമാക്കിയ ആശുപത്രി പുനഃപ്രവേശന സഹായം",
    "welcome": "സ്വാഗതം, രോഗിയേ!",
    "portal": "നിങ്ങളുടെ വ്യക്തിഗത ആരോഗ്യ പോർട്ടൽ",
    "profile": "എന്റെ പ്രൊഫൈൽ",
    "profile_desc": "നിങ്ങളുടെ രജിസ്റ്റർ ചെയ്ത ആരോഗ്യ വിവരങ്ങൾ.",
    "patient_id": "രോഗി തിരിച്ചറിയൽ നമ്പർ",
    "age": "പ്രായം",
    "gender": "ലിംഗം",
    "state": "സംസ്ഥാനം",
    "insurance": "ഇൻഷുറൻസ്",
    "bpl": "BPL കാർഡ്",
    "comorbidities": "സഹരോഗങ്ങൾ",
    "previous": "മുൻ ആശുപത്രി പ്രവേശനങ്ങൾ",

    "risk": "എന്റെ ആരോഗ്യ അപകടസാധ്യത",
    "risk_desc": "നിങ്ങളുടെ ഏറ്റവും പുതിയ AI അടിസ്ഥാനമാക്കിയ ആശുപത്രി പുനഃപ്രവേശന അപകട വിലയിരുത്തൽ.",
    "risk_level": "നിലവിലെ അപകട നില",
    "probability": "30 ദിവസത്തെ പുനഃപ്രവേശന സാധ്യത",

    "high": "ഉയർന്ന അപകടം",
    "moderate": "മിതമായ അപകടം",
    "low": "കുറഞ്ഞ അപകടം",

    "summary": "വൈദ്യശാസ്ത്ര സംഗ്രഹം",
    "recommendations": "എന്റെ ശുപാർശകൾ",

    "rec1": "ഈ വിലയിരുത്തൽ നിങ്ങളുടെ ഡോക്ടറുമായി ചർച്ച ചെയ്യുക.",
    "rec2": "നിശ്ചയിച്ച ഫോളോ-അപ്പ് സന്ദർശനങ്ങളിൽ പങ്കെടുക്കുക.",
    "rec3": "നിങ്ങളുടെ ആരോഗ്യനില പതിവായി നിരീക്ഷിക്കുക.",

    "report": "എന്റെ ആരോഗ്യ റിപ്പോർട്ട്",
    "report_desc": "നിങ്ങളുടെ ഏറ്റവും പുതിയ ആരോഗ്യവും AI വിലയിരുത്തലും PDF ആയി ഡൗൺലോഡ് ചെയ്യുക.",
    "download": "PDF റിപ്പോർട്ട് ഡൗൺലോഡ് ചെയ്യുക",
    "no_report": "ഇതുവരെ അപകട വിലയിരുത്തൽ റിപ്പോർട്ട് ലഭ്യമല്ല.",
    "go_prediction": "അപകട വിലയിരുത്തൽ പൂർത്തിയാക്കാൻ നിങ്ങളുടെ ഡോക്ടറെ സമീപിക്കുക.",

    "secure": "നിങ്ങളുടെ ആരോഗ്യ വിവരങ്ങൾ നിങ്ങളുടെ അക്കൗണ്ടിനായി മാത്രം സുരക്ഷിതമായി പ്രദർശിപ്പിക്കുന്നു.",
    "doctor_notice": "വൈദ്യ തീരുമാനങ്ങൾക്കായി നിങ്ങളുടെ ആരോഗ്യ വിദഗ്ധനെ സമീപിക്കുക.",
    "logout": "ലോഗ് ഔട്ട്",

    "risk_high_summary":
        "അടുത്ത 30 ദിവസത്തിനുള്ളിൽ ആശുപത്രിയിൽ വീണ്ടും പ്രവേശിക്കാനുള്ള അപകടസാധ്യത കൂടുതലാണെന്ന് AI മാതൃക സൂചിപ്പിക്കുന്നു. ഈ വിലയിരുത്തൽ നിങ്ങളുടെ ആരോഗ്യ വിദഗ്ധനുമായി ചർച്ച ചെയ്യുക.",

    "risk_moderate_summary":
        "അടുത്ത 30 ദിവസത്തിനുള്ളിൽ ആശുപത്രിയിൽ വീണ്ടും പ്രവേശിക്കാനുള്ള അപകടസാധ്യത മിതമാണെന്ന് AI മാതൃക സൂചിപ്പിക്കുന്നു. അധിക വൈദ്യ നിരീക്ഷണം ആവശ്യമായേക്കാം.",

    "risk_low_summary":
        "അടുത്ത 30 ദിവസത്തിനുള്ളിൽ ആശുപത്രിയിൽ വീണ്ടും പ്രവേശിക്കാനുള്ള അപകടസാധ്യത കുറവാണെന്ന് AI മാതൃക സൂചിപ്പിക്കുന്നു.",

    "report_title": "CareWatch-AI രോഗി ആരോഗ്യ റിപ്പോർട്ട്",
    "generated": "സൃഷ്ടിച്ച സമയം",
    "risk_level_report": "അപകട നില",
    "readmission_probability": "പുനഃപ്രവേശന സാധ്യത",
    "medical_summary": "വൈദ്യശാസ്ത്ര സംഗ്രഹം",
    "recommendation_title": "ശുപാർശകൾ",
    "confidential": "രഹസ്യ രോഗി ആരോഗ്യ വിവരങ്ങൾ"
}

}

T = TEXT[L]

# ============================================================
# DATA LOADING
# ============================================================

BASE_DIR = os.path.dirname(os.path.dirname(__file__))


@st.cache_data
def load_csv(filename):
    path = os.path.join(BASE_DIR, filename)

    if not os.path.exists(path):
        return pd.DataFrame()

    try:
        return pd.read_csv(path)
    except Exception:
        return pd.DataFrame()


patients = load_csv("patients.csv")
predictions = load_csv("prediction_results.csv")

# ============================================================
# PATIENT ID
# ============================================================

patient_id = st.session_state.get("patient_id")

if not patient_id:
    patient_id = st.session_state.get("user_patient_id")

if not patient_id:
    st.error(T["secure"])
    st.stop()

patient_id = str(patient_id).strip()

# ============================================================
# PATIENT RECORD
# ============================================================

patient = None

if not patients.empty and "patient_id" in patients.columns:

    rows = patients[
        patients["patient_id"].astype(str).str.strip() == patient_id
    ]

    if not rows.empty:
        patient = rows.iloc[0]

if patient is None:
    st.error(T["secure"])
    st.stop()

# ============================================================
# FIND LATEST PREDICTION
# ============================================================

prediction = None

if not predictions.empty:

    if "patient_id" in predictions.columns:

        p = predictions[
            predictions["patient_id"].astype(str).str.strip() == patient_id
        ].copy()

        if not p.empty:

            if "timestamp" in p.columns:
                p["timestamp"] = pd.to_datetime(
                    p["timestamp"],
                    errors="coerce"
                )
                p = p.sort_values("timestamp")

            prediction = p.iloc[-1]

# ============================================================
# HEADER
# ============================================================

st.markdown(
    f"""
    <div style="
        padding:25px;
        border-radius:15px;
        background:linear-gradient(135deg,#0f766e,#155e75);
        color:white;
        margin-bottom:20px;
    ">
        <h1>🩺 {T["app_name"]}</h1>
        <h2>{T["welcome"]}</h2>
        <p>{T["portal"]}</p>
    </div>
    """,
    unsafe_allow_html=True
)

# ============================================================
# PATIENT PROFILE
# ============================================================

st.header(T["profile"])
st.caption(T["profile_desc"])

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.metric(
        T["patient_id"],
        patient_id
    )

with c2:
    st.metric(
        T["age"],
        str(patient.get("age", "—"))
    )

with c3:
    st.metric(
        T["gender"],
        str(patient.get("gender", "—"))
    )

with c4:
    st.metric(
        T["state"],
        str(patient.get("state", "—"))
    )

c1, c2, c3 = st.columns(3)

with c1:
    st.info(
        f"**{T['insurance']}:** "
        f"{patient.get('insurance_type', '—')}"
    )

with c2:
    st.info(
        f"**{T['bpl']}:** "
        f"{patient.get('bpl_card', '—')}"
    )

with c3:
    st.info(
        f"**{T['comorbidities']}:** "
        f"{patient.get('comorbidity_count', '—')}"
    )

st.info(
    f"**{T['previous']}:** "
    f"{patient.get('prev_admissions', '—')}"
)

# ============================================================
# RISK
# ============================================================

st.markdown("---")
st.header(T["risk"])
st.caption(T["risk_desc"])

if prediction is None:

    st.warning(T["no_report"])
    st.info(T["go_prediction"])

else:

    risk = str(
        prediction.get(
            "risk_level",
            prediction.get("risk", "Low")
        )
    ).strip()

    probability = prediction.get(
        "readmission_probability",
        prediction.get("probability", 0)
    )

    try:
        probability = float(probability)
    except Exception:
        probability = 0.0

    if probability <= 1:
        probability_percent = probability * 100
    else:
        probability_percent = probability

    risk_lower = risk.lower()

    if "high" in risk_lower:
        risk_text = T["high"]
        icon = "🔴"
        summary = T["risk_high_summary"]

    elif "moderate" in risk_lower or "medium" in risk_lower:
        risk_text = T["moderate"]
        icon = "🟠"
        summary = T["risk_moderate_summary"]

    else:
        risk_text = T["low"]
        icon = "🟢"
        summary = T["risk_low_summary"]

    c1, c2 = st.columns(2)

    with c1:
        st.metric(
            T["risk_level"],
            f"{icon} {risk_text}"
        )

    with c2:
        st.metric(
            T["probability"],
            f"{probability_percent:.2f}%"
        )

    st.markdown(
        f"""
        <div style="
            padding:20px;
            border-radius:12px;
            border:1px solid #dddddd;
            margin-top:15px;
        ">
        <h3>🧠 {T["summary"]}</h3>
        <p>{summary}</p>
        </div>
        """,
        unsafe_allow_html=True
    )

# ============================================================
# RECOMMENDATIONS
# ============================================================

st.markdown("---")
st.header(T["recommendations"])

st.success(f"✅ {T['rec1']}")
st.success(f"✅ {T['rec2']}")
st.success(f"✅ {T['rec3']}")

# ============================================================
# REPORT SECTION
# ============================================================

st.markdown("---")
st.header(T["report"])
st.caption(T["report_desc"])

report_ready = prediction is not None

if report_ready:

    report_data = {
        "patient_id": patient_id,
        "language": L,
        "risk_level": risk_text,
        "probability": probability_percent,
        "summary": summary,
        "recommendations": [
            T["rec1"],
            T["rec2"],
            T["rec3"]
        ],
        "generated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    st.session_state["patient_report_data"] = report_data

    # Navigate to report generation page
    try:
        st.page_link(
            "pages/5_Report_Generation.py",
            label=f"📄 {T['download']}",
            icon="📄"
        )
    except Exception:

        st.info(
            f"📄 {T['download']}"
        )

else:
    st.info(T["no_report"])

# ============================================================
# SECURITY
# ============================================================

st.markdown("---")

st.info(
    f"🔒 {T['secure']}"
)

st.warning(
    f"⚕️ {T['doctor_notice']}"
)

# ============================================================
# IMPORTANT:
# NO EHR LINK HERE
# ============================================================