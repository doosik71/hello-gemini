import os
import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv


load_dotenv()

# Configure the Generative AI model
# Replace 'YOUR_API_KEY' with your actual API key
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

# Choose a model, e.g., 'gemini-pro'
MODEL_NAME = "gemini-2.5-flash"

st.title("Gemini Chatbot")

# Initialize chat history in session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# React to user input
if prompt := st.chat_input("Say something..."):
    # Display user message in chat message container
    st.chat_message("user").markdown(prompt)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    try:
        model = genai.GenerativeModel(MODEL_NAME)
        response = model.generate_content(prompt, stream=True)

        # Display assistant response in chat message container
        with st.chat_message("assistant"):
            ai_response = st.write_stream(chunk.text for chunk in response)
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": ai_response})

    except Exception as e:
        st.error(f"An error occurred: {e}")
        st.session_state.messages.append({"role": "assistant", "content": f"Error: {e}"})