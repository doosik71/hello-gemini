import streamlit as st
from dotenv import load_dotenv
import google.generativeai as genai
import os


def hide_header() -> None:
    css = """<style>
        .stAppHeader,
        .stAppToolbar {
            display: none !important;
        }
        .stMainBlockContainer {
            padding-top: 0 !important;
        }
        </style>"""
    st.markdown(css, unsafe_allow_html=True)


def set_max_width(width: int) -> None:
    css = """<style>
        .stMain .block-container {
        max-width: {width}px;
            margin: 0 auto;
        }
        </style>"""
    css = css.replace("{width}", f"{width}")
    st.markdown(css, unsafe_allow_html=True)


title = "Gemini Chatbot"
print("Starting", title)

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

if "model" not in st.session_state:
    MODEL_NAME = "gemini-2.5-flash"
    st.session_state.model = genai.GenerativeModel(MODEL_NAME)

st.set_page_config(
    page_title=title,
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

hide_header()

with st.sidebar:
    st.header(title)

    menu_selection = st.selectbox(
        "메뉴를 선택하세요:",
        ("---", "Youtube 요약", "논문 파일 요약", "논문 분석")
    )

if menu_selection == "Youtube 요약":
    import summary_of_youtube

    set_max_width(800)
    url = st.text_input("Youtube URL:", key="youtube_url")
    summary_of_youtube.summarize(url)

elif menu_selection == "논문 파일 요약":
    import summary_of_pdf_file

    set_max_width(1000)
    uploaded_file = st.file_uploader("PDF file:", type=["pdf"], key="pdf_file")
    summary_of_pdf_file.summarize(uploaded_file)

# elif menu_selection == "논문 검색":
#     st.header("논문 검색 화면")
#     st.write("여기에 논문 검색 기능을 구현합니다.")
#     # 예시: 검색 입력 필드
#     search_query = st.text_input("검색어를 입력하세요:")
#     if st.button("검색"):
#         st.write(f"'{search_query}'에 대한 논문을 검색합니다.")

# elif menu_selection == "논문 분석":
#     st.header("논문 분석 화면")
#     st.write("여기에 논문 분석 기능을 구현합니다.")
#     # 예시: 파일 업로드 또는 URL 입력
#     uploaded_file = st.file_uploader("논문 파일을 업로드하세요:", type=["pdf", "txt"])
#     if uploaded_file is not None:
#         st.write(f"'{uploaded_file.name}' 파일이 업로드되었습니다. 분석을 시작합니다.")
