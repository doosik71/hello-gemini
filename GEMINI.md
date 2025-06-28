# Gemini Customization File

This file helps Gemini understand your project better. You can provide instructions and context here.

## Project Overview

*   **Name:** hello-gemini
*   **Description:** A sample project to demonstrate Gemini's capabilities.
*   **Primary Language:** Python

## Instructions for Gemini

*   **Coding Style:** Follow PEP 8 for Python code.
*   **Libraries:** Use the standard Python library whenever possible.
    * Use `uv` command instead of `pip` because `uv` is faster than `pip`.
*   **Testing:** Use the `unittest` module for tests.
*   **Commits:** Write commit messages in the conventional commit format.

## Important Files

*   `main.py`: The main entry point of the application.
*   `README.md`: Contains project documentation.
*   `demo-genai-console.py`: A console-based application demonstrating interaction with the Generative AI.
*   `demo-genai-streamlit.py`: A Streamlit GUI application for chatting with the Generative AI.
    * commands:
      * `/help`: Show available commands.
      * `/clear`: Clear chat history.
      * `/pdf <url>`: Read PDF from URL and summarize its contents.
      * `/html <url>`: Read HTML from URL and summarize its contents.
      * `/youtube <url>`: Read YouTube transcripts from URL and summarize them.
*   `demo-genai-pdf.py`: PDF URL을 입력받고, 해당 PDF를 왼쪽 pane에 출력한다. 오른쪽 pane에는 PDF의 요약 내용을 출력하고 사용자 질의를 받아 PDF에 대해 답변을 한다.
