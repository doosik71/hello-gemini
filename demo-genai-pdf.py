
import streamlit as st
import google.generativeai as genai
from PyPDF2 import PdfReader
import requests
import io
import os
from dotenv import load_dotenv
import html


def init_pdf_info(pdf_url: str = None, pdf_text: str = None) -> None:
    st.session_state.pdf_url = pdf_url
    st.session_state.pdf_text = pdf_text
    st.session_state.chat_history = []


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


def get_gemini_response(question) -> None:
    st.markdown("## 👨‍🦰 " + question)

    with st.spinner("Asking..."):
        prompt = (f"Based on the following context, answer the question (in Korean):\n\n" +
                  f"Context: {st.session_state.pdf_text}\n\n" +
                  f"Question: {question}")
        response = st.session_state.model.generate_content(prompt, stream=True)
        answer = st.write_stream(
            chunk.text for chunk in response)

        st.session_state.chat_history = [
            {"question": question,
             "answer": answer}]


load_dotenv()

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

if "model" not in st.session_state:
    # 모델을 선택한다.
    MODEL_NAME = "gemini-2.5-flash"

    st.session_state.model = genai.GenerativeModel(MODEL_NAME)
    init_pdf_info()


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

        if pdf_url != st.session_state.pdf_url:
            init_pdf_info(pdf_url, get_pdf_text(pdf_url))
    else:
        init_pdf_info()


with col2:
    if st.session_state.pdf_text:
        with st.container(height=800, border=True):
            container = st.container()

            with container:
                for chat in st.session_state.chat_history:
                    st.markdown("## 👨‍🦰" + chat['question'])
                    st.write(chat['answer'])

                if len(st.session_state.chat_history) == 0:
                    for request in ["논문 내용을 요약해줘."]:
                        get_gemini_response(request)

                question = st.text_input("Question:",
                                         placeholder='Input question here')

                if question:
                    get_gemini_response(question)
