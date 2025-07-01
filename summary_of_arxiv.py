import streamlit as st
import traceback
import io
import requests
from filestore import FileStore
from PyPDF2 import PdfReader


fs = FileStore("data/arxiv")

summary_guide = """Summarize the main points from the uploaded PDF file using markdown bullet points.
Maintain the numbering and titles of chapters, sections, and subsections as in the paper's table of contents.
Stay faithful to the original content without making arbitrary modifications.
Ensure the summary is sufficiently detailed and not too short.
Use primarily Korean, with English for technical terms.
Use the declarative form "이다" instead of the polite form "입니다."
Apply heading level 1 (#) for title captions, level 2 (##) for chapter captions, level 3 (###) for section captions, and level 4 (####) for subsection captions.
Use $...$ for inline math and $$...$$ for block math."""


def get_arxiv_summary(pdf_url: str) -> str:
    try:
        response = requests.get(pdf_url)
        pdf_data = response.content

        reader = PdfReader(io.BytesIO(pdf_data))
        pdf_text = ""

        for page in reader.pages:
            if len(pdf_text) > 500000:
                st.warning("Long text will be truncated.")
                break

            pdf_text += page.extract_text() or ""

        prompt = (
            "Based on the following context, answer the question:\n\n"
            + "Context: "
            + pdf_text
            + "\n\n"
            + "Question: "
            + summary_guide
        )

        with st.spinner("Analyzing..."):
            response = st.session_state.model.generate_content(
                [{"role": "user", "parts": [prompt]}], stream=True
            )

        with st.container():
            return st.write_stream(chunk.text for chunk in response)
    except Exception as e:
        traceback.print_exc()
        st.error(f"An error occurred while processing PDF file: {e}")


def summarize() -> None:
    pdf_url = st.text_input("PDF URL:")

    if not pdf_url:
        return

    pdf_url = pdf_url.replace("https://arxiv.org/abs/", "https://arxiv.org/pdf/")

    summary_results = fs[pdf_url]

    if summary_results:
        st.write(summary_results)
    else:
        summary_results = get_arxiv_summary(pdf_url)
        if summary_results:
            fs[pdf_url] = summary_results

    if summary_results and st.button("Show markdown"):
        st.text_area("Markdown:", summary_results, height=600)
