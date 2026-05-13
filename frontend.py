import streamlit as st
import requests

BACKEND_URL = "http://localhost:8000"

# ── PAGE CONFIG ────────────────────────────────────────────
st.set_page_config(
    page_title="Resume Analyzer",
    page_icon="📄",
    layout="centered"
)

st.title("📄 Resume Analyzer")
st.caption("Upload a resume PDF and ask questions about it")

# ── SESSION STATE ──────────────────────────────────────────
# Streamlit reruns on every interaction
# st.session_state persists data across reruns
if "session_id" not in st.session_state:
    st.session_state.session_id = None
if "messages" not in st.session_state:
    st.session_state.messages = []
if "resume_uploaded" not in st.session_state:
    st.session_state.resume_uploaded = False

# ── SIDEBAR: Upload PDF ────────────────────────────────────
with st.sidebar:
    st.header("Upload Resume")
    uploaded_file = st.file_uploader("Choose a PDF", type="pdf")

    if uploaded_file and not st.session_state.resume_uploaded:
        with st.spinner("Processing resume..."):
            response = requests.post(
                f"{BACKEND_URL}/upload",
                files={"file": (uploaded_file.name, uploaded_file, "application/pdf")}
            )

            if response.status_code == 200:
                data = response.json()
                st.session_state.session_id = data["session_id"]
                st.session_state.resume_uploaded = True
                st.session_state.messages = []
                st.success("Resume processed! Start asking questions.")
            else:
                st.error("Failed to process resume. Try again.")

    if st.session_state.resume_uploaded:
        st.success("✅ Resume loaded")
        if st.button("Clear & Upload New"):
            # Clear session on backend
            if st.session_state.session_id:
                requests.delete(f"{BACKEND_URL}/session/{st.session_state.session_id}")
            st.session_state.session_id = None
            st.session_state.messages = []
            st.session_state.resume_uploaded = False
            st.rerun()

    st.divider()
    st.markdown("**Try asking:**")
    st.markdown("- What are the key skills?")
    st.markdown("- What is the work experience?")
    st.markdown("- Is this resume good for ML roles?")
    st.markdown("- What projects have they built?")
    st.markdown("- Rate this resume out of 10")

# ── CHAT UI ────────────────────────────────────────────────
if not st.session_state.resume_uploaded:
    st.info("👈 Upload a resume PDF from the sidebar to get started")
else:
    # Display chat history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    # Chat input
    question = st.chat_input("Ask anything about the resume...")

    if question:
        # Show user message
        with st.chat_message("human"):
            st.write(question)
        st.session_state.messages.append({
            "role": "human",
            "content": question
        })

        # Get answer from backend
        with st.chat_message("ai"):
            with st.spinner("Analyzing..."):
                response = requests.post(
                    f"{BACKEND_URL}/ask",
                    json={
                        "session_id": st.session_state.session_id,
                        "question": question
                    }
                )

                if response.status_code == 200:
                    answer = response.json()["answer"]
                    st.write(answer)
                    st.session_state.messages.append({
                        "role": "ai",
                        "content": answer
                    })
                else:
                    st.error("Something went wrong. Try again.")