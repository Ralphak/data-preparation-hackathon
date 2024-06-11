import streamlit as st
import pandas as pd
from app.gemini_connection import send_prompt_to_gemini
from app.openai_connection import send_prompt_to_openai
from main import config, menu, stylesheet

stylesheet()
config()
menu()

# Function to load data from the uploaded file
def load_data(uploaded_file):
    if uploaded_file is not None:
        try:
            if uploaded_file.type == "text/csv":
                df = pd.read_csv(uploaded_file)
            elif uploaded_file.type == "application/json":
                df = pd.read_json(uploaded_file)
            else:
                st.error("Unsupported file type. Please upload a CSV or JSON file.")
                return None
            st.session_state['dataframe'] = df
            return df
        except Exception as e:
            st.error(f"Error loading the file: {e}")
            return None
    else:
        return None

# Function to add a message
def add_message(role, content):
    st.session_state['messages'].append({'role': role, 'content': content})

# Function to send a message
def send_message():
    user_input = st.session_state.user_input
    if user_input:
        add_message("User", user_input)
        # Generate prompt based on user choice and dataframe
        if 'dataframe' in st.session_state:
            df = st.session_state['dataframe']
            prompt = generate_prompt_for_issue(user_input, df)
            # Send prompt to the AI and get response
            with st.spinner("Sending prompt to AI..."):
                response = send_prompt_to_gemini(prompt)  # or send_prompt_to_openai(prompt)
            if response:
                add_message("AI", response)
            else:
                add_message("AI", "Error obtaining response from AI.")
        else:
            add_message("AI", "No data file loaded.")
        # Clear text input
        st.session_state.user_input = ""

# Function to generate the specific prompt based on user choice
def generate_prompt_for_issue(issue, df):
    default_prompt = "###### Rules to follow: 1. Maximum 100 tokens per prompt."
    
    if issue == "1":
        prompt = f"Provide a descriptive analysis of the data:\n{df.describe(include='all')}"
    elif issue == "2":
        prompt = f"Provide a predictive analysis of the data:\n{df.describe(include='all')}"
    elif issue == "3":
        prompt = f"Provide a time series analysis of the data:\n{df.describe(include='all')}"
    else:
        prompt = "Invalid option. Please choose one of the provided options."
    return prompt + "\n\n" + default_prompt

# Function to initialize the chat session
def initialize_chat():
    if 'messages' not in st.session_state:
        st.session_state['messages'] = []
    initial_message = (
        "Hello, I have just analyzed your file, what would you like to know?\n"
        "1. Provide a descriptive analysis of the data\n"
        "2. Provide a predictive analysis of the data\n"
        "3. Provide a time series analysis of the data\n"
    )
    st.session_state['messages'].append({'role': 'AI', 'content': initial_message})

# Ensure session state keys are initialized
if 'messages' not in st.session_state:
    st.session_state['messages'] = []

if 'dataframe' not in st.session_state:
    st.session_state['dataframe'] = None

# Main page layout
st.title("Data Correction Chatbot")

# File upload
uploaded_file = st.file_uploader("Upload a file", type=["csv", "json"])

# Load and display data from the uploaded file
if uploaded_file:
    df = load_data(uploaded_file)
    if df is not None:
        st.write("Loaded data:")
        st.dataframe(df)
        if not st.session_state['messages']:
            initialize_chat()
            prompt = generate_prompt_for_issue("1", df)
            with st.spinner("Sending prompt to AI..."):
                response = send_prompt_to_gemini(prompt) 
            if response:
                add_message("AI", response)
            else:
                add_message("AI", "Error obtaining response from AI.")

# Display messages
for message in st.session_state['messages']:
    st.write(f"**{message['role']}:** {message['content']}")

# Text input box
st.text_input("You:", key="user_input", on_change=send_message)

# Button to close the chat
if st.button("Close Chat"):
    st.session_state['modal'] = False
