import os
from pathlib import Path
import streamlit as st

from src.chatbot import UniversityChatbot


st.set_page_config(
    page_title="University Services Chatbot",
    page_icon="🎓",
    layout="wide"
)


DOCS_DIR = Path("data/docs")
DOCS_DIR.mkdir(parents=True, exist_ok=True)


@st.cache_resource
def get_chatbot():
    return UniversityChatbot()


def save_uploaded_files(uploaded_files):
    saved_files = []

    for uploaded_file in uploaded_files:
        file_path = DOCS_DIR / uploaded_file.name
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        saved_files.append(uploaded_file.name)

    return saved_files


def show_confidence(confidence):
    if confidence == "High":
        st.success(f"Confidence: {confidence}")
    elif confidence == "Medium":
        st.warning(f"Confidence: {confidence}")
    else:
        st.error(f"Confidence: {confidence}")


def show_sources(docs):
    if not docs:
        st.info("No sources found.")
        return

    st.markdown("### Sources")
    shown = set()

    for doc in docs:
        source = os.path.basename(doc.metadata.get("source", "Unknown"))
        page = doc.metadata.get("page", None)
        snippet = doc.page_content[:250].strip().replace("\n", " ")

        key = (source, page, snippet)
        if key in shown:
            continue
        shown.add(key)

        with st.container():
            st.markdown(
                f"""
<div style="
    border:1px solid #2d3748;
    border-radius:12px;
    padding:14px;
    margin-bottom:12px;
    background-color:#111827;
">
    <div style="font-weight:700; font-size:16px; margin-bottom:6px;">
        📄 {source}
    </div>
    <div style="font-size:14px; color:#9ca3af; margin-bottom:8px;">
        Page: {page + 1 if isinstance(page, int) else "N/A"}
    </div>
    <div style="font-size:14px; line-height:1.5;">
        {snippet}...
    </div>
</div>
                """,
                unsafe_allow_html=True
            )


def main():
    st.title("🎓 AI Chatbot for University Services")
    st.caption("Ask questions about exams, modules, schedules, deadlines, and university services.")

    with st.sidebar:
        st.header("Settings")
        language = st.selectbox("Answer language", ["English", "German"])

        st.markdown("---")
        st.subheader("Upload documents")
        uploaded_files = st.file_uploader(
            "Upload PDF, TXT, or MD files",
            type=["pdf", "txt", "md"],
            accept_multiple_files=True
        )

        if st.button("Process uploaded documents"):
            if uploaded_files:
                saved = save_uploaded_files(uploaded_files)
                st.cache_resource.clear()
                st.success(f"Processed {len(saved)} file(s): {', '.join(saved)}")
                st.rerun()
            else:
                st.warning("Please upload at least one file.")

        st.markdown("---")
        st.markdown("**Example questions**")
        st.markdown("- Wann ist die Prüfungsanmeldung?")
        st.markdown("- How many ECTS does Softwaretechnik have?")
        st.markdown("- What are the office hours of the exam office?")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    try:
        chatbot = get_chatbot()
    except Exception as e:
        st.error(f"Startup error: {e}")
        st.stop()

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message.get("confidence"):
                show_confidence(message["confidence"])
            if message.get("sources"):
                show_sources(message["sources"])

    user_input = st.chat_input("Ask a question about university services...")

    if user_input:
        st.session_state.messages.append({
            "role": "user",
            "content": user_input
        })

        with st.chat_message("user"):
            st.markdown(user_input)

        with st.chat_message("assistant"):
            with st.spinner("Searching documents and preparing answer..."):
                try:
                    answer, docs, confidence = chatbot.answer_question(
    user_input,
    st.session_state.messages,
    language
)
                except Exception as e:
                    answer = f"An error occurred: {e}"
                    docs = []
                    confidence = None

            st.markdown(answer)
            if confidence:
                show_confidence(confidence)
            show_sources(docs)

        st.session_state.messages.append({
            "role": "assistant",
            "content": answer,
            "sources": docs,
            "confidence": confidence
        })


if __name__ == "__main__":
    main()