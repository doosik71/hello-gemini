import streamlit as st
import traceback
from PyPDF2 import PdfReader


summary_guide = """Summarize the main points from the uploaded PDF file using markdown bullet points.
Maintain the numbering and titles of chapters, sections, and subsections as in the paper's table of contents.
Stay faithful to the original content without making arbitrary modifications.
Ensure the summary is sufficiently detailed and not too short.
Use primarily Korean, with English for technical terms.
Use the declarative form "이다" instead of the polite form "입니다."
Apply heading level 1 (#) for title captions, level 2 (##) for chapter captions, level 3 (###) for section captions, and level 4 (####) for subsection captions.
Use $...$ for inline math and $$...$$ for block math."""


def summarize(pdf_file) -> None:
    if not pdf_file:
        return

    try:
        reader = PdfReader(pdf_file)
        text = ""

        for page in reader.pages:
            if len(text) > 500000:
                break

            text += page.extract_text() or ""

        prompt = (
            "Based on the following context, answer the question:\n\n"
            + "Context: "
            + text
            + "\n\n"
            + "Question: "
            + summary_guide
        )

        with st.spinner("Analyzing..."):
            response = st.session_state.model.generate_content(prompt, stream=True)

        with st.container():
            st.write_stream(chunk.text for chunk in response)
    except Exception as e:
        traceback.print_exc()
        st.error(f"An error occurred while processing YouTube video: {e}")
