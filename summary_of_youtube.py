from youtube_transcript_api import YouTubeTranscriptApi
from filestore import FileStore
import re
import streamlit as st
import traceback


fs = FileStore("data/youtube")

summary_guide = """Summarize the main points and detailed explanations from the script below.
Begin with the video title caption, starting with `#`.
Use section headings marked with `##` and include relevant emojis for each section.
Each section should be written as a cohesive paragraph that clearly and thoroughly conveys the main ideas.
The summary should be informative, concise, and resemble an executive news article.
Maintain a direct and objective tone.
Do not use phrases like "the script provides."
Write the summary in Korean."""


def get_youtube_summary(video_id: str) -> str:
    try:
        with st.spinner(f"Fetching transcript..."):
            transcript_list = YouTubeTranscriptApi.get_transcript(
                video_id, languages=("ko", "en")
            )
            transcript_text = " ".join([d["text"] for d in transcript_list])

        if not transcript_text.strip():
            st.error("Could not extract transcript from the YouTube video.")
            return

        if len(transcript_text) > 500000:
            transcript_text = (
                transcript_text[:500000] + "\n\n[Content truncated due to length...]"
            )

        prompt = (
            "Based on the following context, answer the question:\n\n"
            + "Context: "
            + transcript_text
            + "\n\n"
            + "Question: "
            + summary_guide
        )

        with st.spinner("Summarizing transcript..."):
            # prompt = summary_guide + "\n---\n" + transcript_text
            response = st.session_state.model.generate_content(
                [{"role": "user", "parts": [prompt]}], stream=True
            )

        with st.container():
            return st.write_stream(chunk.text for chunk in response)
    except Exception as e:
        traceback.print_exc()
        st.error(f"An error occurred while processing YouTube video: {e}")


def summarize() -> None:
    if "youtube_url" not in st.session_state:
        st.session_state.youtube_url = ""

    youtube_url = st.text_input("Youtube URL:", value=st.session_state.youtube_url)
    st.session_state.youtube_url = youtube_url

    if not youtube_url:
        return

    video_id_match = re.search(r"(?<=v=)[a-zA-Z0-9_-]+", youtube_url)
    if not video_id_match:
        st.error("Invalid YouTube URL.")
        return

    video_id = video_id_match.group(0)
    if not video_id:
        st.error("Invalid video id.")
        return

    st.write(
        '<iframe width="560" height="315" id="youtube_video" '
        + f'src="https://www.youtube.com/embed/{video_id}" '
        + 'title="YouTube video player" frameborder="0" '
        + "allowfullscreen></iframe>",
        unsafe_allow_html=True,
    )

    st.write(
        "<style>iframe{display: block; margin-left: auto; margin-right: auto;}</style>",
        unsafe_allow_html=True,
    )

    summary_results = fs[video_id]

    if summary_results:
        st.write(summary_results)
    else:
        summary_results = get_youtube_summary(video_id)
        if summary_results:
            fs[video_id] = summary_results

    if summary_results and st.button("Show markdown"):
        st.text_area("Markdown:", summary_results, height=600)
