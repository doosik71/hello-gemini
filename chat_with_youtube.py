from youtube_transcript_api import YouTubeTranscriptApi
import re
import streamlit as st
import traceback


summary_guide = """Summarize the main points and detailed explanations from the script below.
Use appropriate headings with relevant emojis to represent each section.
Present each section as a cohesive paragraph under its heading.
Ensure the summary is clear, detailed, and informative, resembling an executive summary in news articles.
Maintain a direct and objective tone without using phrases like "the script provides."
Write in Korean."""


def summarize_youtube(url: str) -> None:
    if not url:
        return

    try:
        video_id_match = re.search(r"(?<=v=)[a-zA-Z0-9_-]+", url)
        if not video_id_match:
            st.error("Invalid YouTube URL.")
            return

        video_id = video_id_match.group(0)
        if not video_id:
            st.error("Invalid video id.")
            return

        with st.spinner(f"Fetching transcript from YouTube video {url}..."):
            transcript_list = YouTubeTranscriptApi.get_transcript(
                video_id, languages=("ko", "en"))
            transcript_text = " ".join(
                [d['text'] for d in transcript_list])

        if not transcript_text.strip():
            st.error("Could not extract transcript from the YouTube video.")
            return

        if len(transcript_text) > 30000:
            transcript_text = (transcript_text[:30000] +
                               "\n\n[Content truncated due to length...]")

        st.write(f'<iframe width="560" height="315" src="https://www.youtube.com/embed/{video_id}" ' +
                 'title="YouTube video player" frameborder="0"' +
                 'allow="autoplay; encrypted-media; picture-in-picture"' +
                 'referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>',
                 unsafe_allow_html=True)

        st.write("<style>iframe{display: block; margin-left: auto; margin-right: auto;}</style>",
                 unsafe_allow_html=True)

        with st.spinner("Summarizing YouTube transcript..."):
            prompt = summary_guide + "\n---\n" + transcript_text
            response = st.session_state.model.generate_content(
                [{"role": "user", "parts": [prompt]}], stream=True)

        with st.container():
            st.write_stream(chunk.text for chunk in response)
    except Exception as e:
        traceback.print_exc()
        st.error(f"An error occurred while processing YouTube video: {e}")
