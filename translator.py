from deep_translator import GoogleTranslator
import streamlit as st


@st.cache_data(show_spinner=False)
def translate_text(text, language):

    language_map = {

        "English": "en",

        "Hindi": "hi",

        "Kannada": "kn",

        "Tamil": "ta",

        "Telugu": "te",

        "Malayalam": "ml"

    }

    if language == "English":

        return text

    try:

        return GoogleTranslator(
            source="en",
            target=language_map[language]
        ).translate(text)

    except:

        return text