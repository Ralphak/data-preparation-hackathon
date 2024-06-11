import openai
import streamlit as st

API_KEY = "YOUR_OPENAI_API_KEY"  
openai.api_key = API_KEY

def send_prompt_to_openai(prompt):
    try:
        response = openai.Completion.create(
            engine="text-davinci-003",  
            prompt=prompt,
            max_tokens=100,
            n=1,
            stop=None,
            temperature=0.7, 
        )
        return response.choices[0].text.strip()
    except Exception as e:
        st.error(f"Erro ao conectar com o OpenAI: {e}")
        return None
