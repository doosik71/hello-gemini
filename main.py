import streamlit as st
from dotenv import load_dotenv
import google.generativeai as genai
import os


title = "Gemini Chatbot"

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

if "model" not in st.session_state:
    MODEL_NAME = "gemini-2.5-flash"
    st.session_state.model = genai.GenerativeModel(MODEL_NAME)

st.set_page_config(
    page_title=title,
    page_icon="🤖",
    initial_sidebar_state="expanded"
)

with st.sidebar:
    st.header(title)

    menu_selection = st.radio(
        "메뉴를 선택하세요:",
        ("Youtube 요약", "논문 파일 요약", "Arxiv 논문 요약")
    )

if menu_selection == "Youtube 요약":
    import summary_of_youtube

    summary_of_youtube.summarize()

elif menu_selection == "논문 파일 요약":
    import summary_of_pdf_file

    uploaded_file = st.file_uploader("PDF file:", type=["pdf"], key="pdf_file")
    summary_of_pdf_file.summarize(uploaded_file)

elif menu_selection == "Arxiv 논문 요약":
    import summary_of_arxiv

    summary_of_arxiv.summarize()
