
import streamlit as st
import google.generativeai as genai
from PyPDF2 import PdfReader
import requests
import io
import os
from dotenv import load_dotenv
import html

load_dotenv()

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

if "model" not in st.session_state:
    # 모델을 선택한다.
    MODEL_NAME = "gemini-2.5-flash"
    st.session_state.model = genai.GenerativeModel(MODEL_NAME)
    st.session_state.chat_history = []
    st.session_state.pdf_url = None
    st.session_state.pdf_text = None
    st.session_state.summary = None


def get_pdf_text(pdf_url):
    try:
        response = requests.get(pdf_url)
        response.raise_for_status()  # Raise an exception for HTTP errors
        with io.BytesIO(response.content) as pdf_file:
            reader = PdfReader(pdf_file)
            text = ""
            for page in reader.pages:
                text += page.extract_text() or ""
            return text
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching PDF from URL: {e}")
        return None
    except Exception as e:
        st.error(f"Error processing PDF: {e}")
        return None


def summarize_text(text):
    prompt = f"Summarize the following text (in Korean):\n\n{text}"
    return st.session_state.model.generate_content(prompt, stream=True)


def get_gemini_response(question, context):
    prompt = (f"Based on the following context, answer the question (in Korean):\n\n" +
              f"Context: {context}\n\n" +
              f"Question: {question}")
    return st.session_state.model.generate_content(prompt, stream=True)


st.set_page_config(page_title="PDF Chat with Gemini", layout="wide")

st.markdown("""
<style>
    .stAppHeader, .stAppToolbar {
        display: none !important;
    }
    .stMainBlockContainer  {
        padding-top: 0 !important;
    }
</style>
""", unsafe_allow_html=True)

st.title("PDF Chat with Gemini")

pdf_url = st.text_input("Enter PDF URL:")

col1, col2 = st.columns([6, 4])

with col1:
    if pdf_url:
        st.write(f'<iframe src="{html.escape(pdf_url)}" width="100%" height="800px"></iframe>',
                 unsafe_allow_html=True)
    else:
        st.session_state.chat_history = []
        st.session_state.pdf_url = None
        st.session_state.pdf_text = None
        st.session_state.summary = None

with col2:
    with st.container(height=800, border=True):
        container = st.container()
        with container:
            if pdf_url and pdf_url != st.session_state.pdf_url:
                with st.spinner("Extracing contents..."):
                    pdf_text = get_pdf_text(pdf_url)

                st.session_state.chat_history = []
                st.session_state.pdf_url = pdf_url
                st.session_state.pdf_text = pdf_text
                st.session_state.summary = None

            for chat in st.session_state.chat_history:
                st.markdown("## 👨‍🦰" + chat['question'])
                st.write(chat['answer'])

            if st.session_state.pdf_text and not st.session_state.summary:
                summary_request = "Summarize the paper in Korean."
                st.markdown("## 👨‍🦰 " + summary_request)

                with st.spinner("Summarizing..."):
                    response = summarize_text(st.session_state.pdf_text)
                    summary = st.write_stream(chunk.text for chunk in response)
                    st.session_state.summary = summary
                    st.session_state.chat_history = [
                        {"question": summary_request,
                         "answer": summary}]

        if st.session_state.pdf_text:
            user_question = st.text_input("Question:",
                                          placeholder='Input question here')

            if user_question:
                with container:
                    st.markdown("## 👨‍🦰" + user_question)
                    with st.spinner("Asking..."):
                        response = get_gemini_response(
                            user_question,
                            st.session_state.pdf_text)
                        answer = st.write_stream(
                            chunk.text for chunk in response)
                        st.session_state.chat_history.append(
                            {"question": user_question,
                                "answer": answer})
