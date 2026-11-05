import os
from pathlib import Path

import streamlit as st

st.set_page_config(
    page_title="SupportDesk RAG",
    page_icon=":material/support_agent:",
    layout="wide",
)

try:
    _secret_groq_key = st.secrets.get("GROQ_API_KEY")
except Exception:
    _secret_groq_key = None
if _secret_groq_key and not os.getenv("GROQ_API_KEY"):
    os.environ["GROQ_API_KEY"] = str(_secret_groq_key)

from rag_pipeline import RAGPipeline

DATA_DIR = str(Path(__file__).parent / "data" / "raw")


@st.cache_resource
def get_pipeline() -> RAGPipeline:
    return RAGPipeline()

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700&family=Work+Sans:wght@300;400;500;600&display=swap');

    :root {
        --sd-primary: #1E3A5F;
        --sd-secondary: #2563EB;
        --sd-accent: #059669;
        --sd-bg: #F8FAFC;
        --sd-fg: #0F172A;
        --sd-card: #FFFFFF;
        --sd-muted: #F1F3F5;
        --sd-muted-fg: #475569;
        --sd-border: #E4E7EB;
        --sd-error: #DC2626;
    }

    html, body, .stApp, [data-testid="stAppViewContainer"] {
        font-family: 'Work Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    }

    h1, h2, h3, h4, h5, h6 {
        font-family: 'Outfit', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
        color: var(--sd-fg);
        letter-spacing: -0.01em;
    }

    .sd-hero {
        background: linear-gradient(135deg, #1E3A5F 0%, #2563EB 100%);
        border-radius: 16px;
        padding: 1.7rem 1.9rem;
        margin-bottom: 1.1rem;
        box-shadow: 0 10px 30px rgba(30, 58, 95, 0.18);
    }
    .sd-eyebrow {
        margin: 0 0 0.45rem 0;
        color: #BFDBFE;
        font-size: 0.72rem;
        font-weight: 600;
        letter-spacing: 0.14em;
        text-transform: uppercase;
    }
    .sd-hero h1 {
        margin: 0 0 0.45rem 0;
        color: #FFFFFF;
        font-size: 2rem;
        line-height: 1.15;
    }
    .sd-hero p {
        margin: 0;
        color: #DBEAFE;
        font-size: 0.95rem;
        line-height: 1.55;
        max-width: 72ch;
    }

    div[data-testid="stVerticalBlockBorderWrapper"] {
        background: var(--sd-card);
        border: 1px solid var(--sd-border);
        border-radius: 14px;
        box-shadow: 0 1px 2px rgba(15, 23, 42, 0.04);
        transition: box-shadow 0.2s ease, border-color 0.2s ease;
    }
    div[data-testid="stVerticalBlockBorderWrapper"]:hover {
        border-color: #CBD5E1;
        box-shadow: 0 6px 20px rgba(15, 23, 42, 0.06);
    }

    .stButton > button {
        border-radius: 10px;
        font-family: 'Work Sans', sans-serif;
        font-weight: 600;
        transition: transform 0.18s ease, box-shadow 0.18s ease;
    }
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 6px 16px rgba(30, 58, 95, 0.16);
    }
    .stButton > button:focus-visible {
        outline: 2px solid var(--sd-secondary);
        outline-offset: 2px;
    }

    [data-testid="stBadge"] {
        border-radius: 999px;
        font-family: 'Work Sans', sans-serif;
        font-weight: 500;
    }

    [data-testid="stCaptionContainer"] {
        color: var(--sd-muted-fg);
    }

    @media (prefers-reduced-motion: reduce) {
        *, *::before, *::after {
            animation-duration: 0.01ms !important;
            animation-iteration-count: 1 !important;
            transition-duration: 0.01ms !important;
        }
    }

    @media (max-width: 640px) {
        .sd-hero { padding: 1.2rem 1.1rem; }
        .sd-hero h1 { font-size: 1.55rem; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

if "ingested" not in st.session_state:
    st.session_state.ingested = False
if "chunk_count" not in st.session_state:
    st.session_state.chunk_count = None
if "last_result" not in st.session_state:
    st.session_state.last_result = None
if "last_question" not in st.session_state:
    st.session_state.last_question = ""

pipeline = get_pipeline()

st.markdown(
    """
    <div class="sd-hero">
        <p class="sd-eyebrow">Support Operations · RAG Assistant</p>
        <h1>SupportDesk RAG</h1>
        <p>Ask questions about refunds, shipping, passwords, billing, and troubleshooting.
        Answers are grounded in your indexed support documents and cite their sources.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

status_col, _ = st.columns([1, 2])
with status_col:
    if st.session_state.ingested:
        st.badge(
            f"Knowledge base indexed · {st.session_state.chunk_count} chunks",
            icon=":material/check_circle:",
            color="green",
        )
    else:
        st.badge(
            "Knowledge base not indexed",
            icon=":material/pending:",
            color="orange",
        )

st.write("")

left, right = st.columns([2.2, 1], gap="large")

with left:
    with st.container(border=True):
        st.subheader("Knowledge base", icon=":material/database:")
        st.caption(
            "Index the support documents in `data/raw`. Re-ingest after changing "
            "documents or the embedding model."
        )
        if st.button(
            "Ingest support documents",
            icon=":material/database_upload:",
            type="primary",
            width="stretch",
        ):
            try:
                with st.spinner("Loading and indexing documents..."):
                    n = pipeline.ingest(DATA_DIR)
                st.session_state.ingested = True
                st.session_state.chunk_count = n
                st.session_state.last_result = None
                st.session_state.last_question = ""
                st.success(f"Ingested {n} document chunks into the vector store.")
            except Exception as e:
                st.error(f"Ingestion failed: {e}")

    with st.container(border=True):
        st.subheader("Ask a question", icon=":material/forum:")
        with st.form("ask_form", clear_on_submit=True):
            question = st.text_input(
                "Your question",
                placeholder="e.g., How do I request a refund?",
                icon=":material/search:",
                label_visibility="collapsed",
                disabled=not st.session_state.ingested,
            )
            submitted = st.form_submit_button(
                "Get answer",
                icon=":material/chat:",
                type="primary",
                width="stretch",
                disabled=not st.session_state.ingested,
            )
        if submitted:
            if not question.strip():
                st.warning("Please enter a question.")
            else:
                try:
                    with st.spinner("Retrieving context and generating answer..."):
                        result = pipeline.query(question)
                    st.session_state.last_result = result
                    st.session_state.last_question = question
                except Exception as e:
                    st.error(f"Query failed: {e}")

    result = st.session_state.last_result
    if result:
        with st.container(border=True):
            st.subheader("Answer", icon=":material/lightbulb:")
            if st.session_state.last_question:
                st.caption(f"Question: {st.session_state.last_question}")
            st.write(result["answer"])

            sources = list(dict.fromkeys(result.get("sources", [])))
            if sources:
                st.caption("Sources")
                with st.container(horizontal=True, wrap=True):
                    for src in sources:
                        st.badge(
                            Path(src).name,
                            icon=":material/description:",
                            color="gray",
                        )

with right:
    with st.container(border=True):
        st.subheader("How it works", icon=":material/route:")
        st.markdown(
            """
            1. **Ingest** — documents are chunked and embedded.
            2. **Ask** — the retriever finds the closest chunks.
            3. **Answer** — the model answers using only that context.
            """
        )

    with st.container(border=True):
        st.subheader("Data sources", icon=":material/folder:")
        with st.container(horizontal=True, wrap=True):
            st.badge("FAQs", icon=":material/help:", color="blue")
            st.badge("Support tickets", icon=":material/confirmation_number:", color="blue")
            st.badge("Troubleshooting", icon=":material/build:", color="blue")

    with st.container(border=True):
        st.subheader("Stack", icon=":material/memory:")
        with st.container(horizontal=True, wrap=True):
            st.badge("Python", color="gray")
            st.badge("SentenceTransformers", color="gray")
            st.badge("ChromaDB", color="gray")
            st.badge("Groq", color="gray")
            st.badge("Streamlit", color="gray")

st.write("")
st.caption("SupportDesk RAG · grounded answers with cited sources")
