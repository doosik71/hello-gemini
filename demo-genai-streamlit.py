from dotenv import load_dotenv
from youtube_transcript_api import YouTubeTranscriptApi
import google.generativeai as genai
import io
import os
import PyPDF2
import re
import requests
import streamlit as st
import traceback


# 페이지 설정
st.set_page_config(
    page_title="Gemini Chatbot",
    page_icon="🤖",
    initial_sidebar_state="expanded"
)

st.title("Gemini Chatbot")

load_dotenv()

print('Starting streamlit app...')

# 제너레이티브 AI 모델을 설정한다.
# 'YOUR_API_KEY'를 실제 API 키로 대체한다.
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

if "model" not in st.session_state:
    # 모델을 선택한다.
    MODEL_NAME = "gemini-2.5-flash"
    st.session_state.model = genai.GenerativeModel(MODEL_NAME)

# st.session_state.messages는 GUI에 메시지 기록을 출력하기 위한 메시지 기록 저장소이다.
# 이 목록은 "user"와 "assistant" 두 가지 역할을 가질 수 있다.
# 메시지 정보는 "content" 키에 저장된다.
if "messages" not in st.session_state:
    st.session_state.messages = []

# st.session_state.chat_history는 모델에 전달하기 위한 메시지 기록 저장소이다.
# 이 목록은 "user"와 "model" 두 가지 역할을 가질 수 있다.
# 메시지 정보는 "parts" 키에 저장된다.
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# GUI에 메시지 기록을 출력한다.
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


def add_message(role, content):
    assert role in ["user", "model"], f"Invalid role: {role}"

    # genai 모델에 전달하기 위해 메시지 기록 저장소에 메시지를 추가한다.
    st.session_state.chat_history.append({"role": role, "parts": [content]})

    # streamlit은 모델 역할을 표시하기 위해 "assistant"로 표시되어야 한다.
    # 따라서 "model" 역할을 "assistant" 역할로 변환한다.
    if role == "model":
        role = "assistant"

    # GUI에 메시지 기록을 출력하기 위해 메시지 기록 저장소에 메시지를 추가한다.
    st.session_state.messages.append({"role": role, "content": content})


def _handle_clear_command():
    st.session_state.messages = []
    st.session_state.chat_history = []
    st.success("Chat history cleared!")
    st.rerun()


def _handle_help_command():
    st.chat_message("user").markdown("/help")
    add_message("user", "/help")

    help_message = """
Available commands:
* `/help`: Show available commands.
* `/clear`: Clear chat history.
* `/pdf <url>`: Read PDF from URL and summarize its contents.
* `/html <url>`: Read HTML from URL and summarize its contents.
* `/youtube <url>`: Read YouTube transcripts from URL and summarize them.
"""

    add_message("model", help_message)
    st.chat_message("assistant").markdown(help_message)


def _handle_html_command(url):
    """
    requests를 이용해서 웹 페치 기능을 대신한다.
    """

    try:
        prompt = f"Analyze and summarize the content from {url}"
        st.chat_message("user").markdown(prompt)
        add_message("user", prompt)

        with st.spinner(f"Reading HTML from {url}..."):
            response = requests.get(url)
            response.raise_for_status()
            html_content = response.text

        prompt = f"Please analyze and summarize the following HTML contents:\n\n{html_content}"

        with st.spinner(f"Analyzing {url}"):
            response = st.session_state.model.generate_content(
                st.session_state.chat_history + [{"role": "user", "parts": [prompt]}], stream=True)

        with st.chat_message("assistant"):
            ai_response = st.write_stream(chunk.text for chunk in response)

        add_message("model", ai_response)

    except Exception as e:
        st.error(f"An error occurred while processing HTML: {e}")


def _handle_pdf_command(url):
    """
    PDF 파일을 URL에서 다운로드하고 텍스트를 추출한 후 Gemini 모델로 요약한다.
    """

    try:
        prompt = f"Analyze the PDF content from {url}"
        st.chat_message("user").markdown(prompt)
        add_message("user", prompt)

        # Step 1: Get PDF document from URL
        with st.spinner(f"Downloading PDF from {url}..."):
            response = requests.get(url)
            response.raise_for_status()  # HTTP 오류가 있으면 예외 발생

            if not response.headers.get('content-type', '').lower().startswith('application/pdf'):
                st.error("The URL does not point to a valid PDF file.")
                return

        # Step 2: Get text from PDF
        with st.spinner("Extracting text from PDF..."):
            pdf_file = io.BytesIO(response.content)

            try:
                pdf_reader = PyPDF2.PdfReader(pdf_file)

                # PDF 텍스트 추출
                text_content = ""
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    text_content += page.extract_text() + "\n"

                if not text_content.strip():
                    st.error(
                        "Could not extract text from the PDF. The PDF might be image-based or encrypted.")
                    return

                # 텍스트가 너무 길면 잘라내기 (모델 토큰 제한 고려)
                if len(text_content) > 30000:  # 약 30KB 제한
                    text_content = text_content[:30000] + \
                        "\n\n[Content truncated due to length...]"

            except PyPDF2.PdfReadError as e:
                st.error(f"Error reading PDF: {e}")
                return

        # Step 3: Summarize pdf text by using model
        with st.spinner("Analyzing PDF content..."):
            prompt = f"Please analyze and summarize the following PDF content:\n\n{text_content}"

            response = st.session_state.model.generate_content(
                st.session_state.chat_history + [{"role": "user", "parts": [prompt]}], stream=True)

        with st.chat_message("assistant"):
            ai_response = st.write_stream(chunk.text for chunk in response)

        add_message("model", ai_response)

    except requests.RequestException as e:
        st.error(f"Error downloading PDF: {e}")
    except Exception as e:
        traceback.print_exc()
        st.error(f"An error occurred while processing PDF: {e}")


def _handle_youtube_command(url):
    """
    YouTube 동영상 URL에서 스크립트를 추출하고 Gemini 모델로 요약한다.
    """
    try:
        video_id_match = re.search(r"(?<=v=)[a-zA-Z0-9_-]+", url)
        if not video_id_match:
            st.error(
                "Invalid YouTube URL. Please provide a valid YouTube video URL.")
            return
        video_id = video_id_match.group(0)

        prompt = f"Analyze the YouTube video transcript from {url}"
        st.chat_message("user").markdown(prompt)
        add_message("user", prompt)

        with st.spinner(f"Fetching transcript from YouTube video {url}..."):
            transcript_list = YouTubeTranscriptApi.get_transcript(
                video_id, languages=("ko", "en"))
            transcript_text = " ".join([d['text'] for d in transcript_list])

        if not transcript_text.strip():
            st.error(
                "Could not extract transcript from the YouTube video. It might not have captions or be unavailable.")
            return

        # 텍스트가 너무 길면 잘라내기 (모델 토큰 제한 고려)
        if len(transcript_text) > 30000:  # 약 30KB 제한
            transcript_text = transcript_text[:30000] + \
                "\n\n[Content truncated due to length...]"

        with st.spinner("Analyzing YouTube transcript..."):
            prompt = f"Please analyze and summarize the following YouTube video transcript:\n\n{transcript_text}"

            response = st.session_state.model.generate_content(
                st.session_state.chat_history + [{"role": "user", "parts": [prompt]}], stream=True)

        with st.chat_message("assistant"):
            ai_response = st.write_stream(chunk.text for chunk in response)

        add_message("model", ai_response)

    except Exception as e:
        traceback.print_exc()
        st.error(f"An error occurred while processing YouTube video: {e}")


def _handle_user_input():
    """
    Example:
    /help
    /clear
    /pdf https://arxiv.org/pdf/2506.21384
    /html https://cadabra.tistory.com/138
    /youtube https://www.youtube.com/watch?v=dQw4w9WgXcQ
    """

    if prompt := st.chat_input("Say something..."):
        prompt = prompt.strip()

        if prompt.lower() == "/clear":
            _handle_clear_command()
        elif prompt.lower() == "/help":
            _handle_help_command()
        elif prompt.lower().startswith("/pdf"):
            url = prompt[len("/pdf"):].strip()
            if url:
                _handle_pdf_command(url)
            else:
                st.error(
                    "Please provide a PDF URL after /pdf, e.g., /pdf https://example.com/document.pdf")
        elif prompt.lower().startswith("/html"):
            url = prompt[len("/html"):].strip()
            if url:
                _handle_html_command(url)
            else:
                st.error(
                    "Please provide an HTML URL after /html, e.g., /html https://example.com")
        elif prompt.lower().startswith("/youtube"):
            url = prompt[len("/youtube"):].strip()
            if url:
                _handle_youtube_command(url)
            else:
                st.error(
                    "Please provide a YouTube URL after /youtube, e.g., /youtube https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        elif prompt.startswith("https://arxiv.org/pdf/"):
            _handle_pdf_command(prompt)
        elif prompt.startswith("https://www.youtube.com/"):
            _handle_youtube_command(prompt)
        elif prompt.startswith("http://") or prompt.startswith("https://"):
            _handle_html_command(prompt)
        else:
            # Display user message in chat message container
            st.chat_message("user").markdown(prompt)

            # Add user message to chat history
            add_message("user", prompt)

            try:
                with st.spinner("Waiting for response..."):
                    response = st.session_state.model.generate_content(
                        st.session_state.chat_history, stream=True)

                # Display assistant response in chat message container
                with st.chat_message("assistant"):
                    ai_response = st.write_stream(
                        chunk.text for chunk in response)
                # Add assistant response to chat history
                add_message("model", ai_response)

            except Exception as e:
                traceback.print_exc()
                st.error(f"An error occurred: {e}")


_handle_user_input()
