import google.generativeai as genai
import streamlit as st

API_KEY = "***REMOVED***"
genai.configure(api_key=API_KEY)

def send_prompt_to_gemini(prompt):
    try:
        model = genai.GenerativeModel('gemini-1.5-flash-latest')
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        st.error(f"Erro ao conectar com o Gemini: {e}")
        return None
