# AGENTS.md

## Project
Customer support RAG pipeline: loads documents, chunks them, embeds with SentenceTransformers, stores in ChromaDB, retrieves top-k chunks, generates answers via Groq (or template fallback).

## Directory layout
```
rag_pipeline/rag_pipeline/          # Python package root
├── app.py                          # Streamlit UI entrypoint
├── main.py                         # CLI entrypoint (uv run python main.py)
├── pyproject.toml                  # uv project + dependencies
├── .env.example                    # Template (commit-safe, no real keys)
├── .env                            # Local only — contains GROQ_API_KEY (gitignored)
├── .gitignore                      # Ignores .env, caches, data/processed, secrets
├── config/settings.py              # Reads .env via load_dotenv()
├── src/rag_pipeline/               # Package: loader, splitter, embeddings, vectorstore, retriever, generator, pipeline
├── data/raw/                       # Drop documents here (txt, pdf, md)
└── data/processed/chroma_db/       # ChromaDB vector store (gitignored, regenerated on ingest)
```

## Developer commands (use `uv run`, not pip/venv directly)

| Task | Command |
|------|---------|
| Install/manage deps | `uv run python -m pip install <pkg>` or `uv add <pkg>` |
| Run CLI | `uv run python main.py` |
| Run Streamlit UI | `uv run streamlit run app.py` |
| Run Python in project env | `uv run python -c "..."` |
| Activate venv manually | `& ".venv\Scripts\Activate.ps1"` (Windows PowerShell) |

`uv` manages the `.venv` at the repo parent level (`C:\Users\admin\OneDrive\Documents\Studies\RAG\.venv`). Do not create a second venv inside `rag_pipeline/rag_pipeline/`. The repo-root `pyproject.toml` is a virtual uv workspace (no root package); the only package is `rag_pipeline/rag_pipeline`.

## Environment setup

1. Copy `.env.example` to `.env`:
   ```powershell
   copy .env.example .env
   ```
2. Edit `.env` and add your Groq API key (no quotes):
   ```
   GROQ_API_KEY=gsk_your_actual_key_here
   ```
3. `.env` is gitignored — never commit it.

## Gotchas

- **ChromaDB persistence**: `data/processed/chroma_db/` persists between runs. If you change the embedding model or documents, delete this directory before re-ingesting, otherwise old embeddings persist.
- **Relative paths**: `app.py` resolves `data/raw` relative to its own file location via `Path(__file__).parent / "data" / "raw"`. `main.py` and `pipeline.py` use relative `data/raw` — run from `rag_pipeline/rag_pipeline/`. `VECTOR_DB_PATH` is also relative by default, so running from the repo root creates a stray `RAG/data/processed/chroma_db`.
- **Groq model**: `generator.py` uses `openai/gpt-oss-120b`. If Groq returns `model_not_found`, check https://console.groq.com/docs/models for current model names.
- **No OpenAI dependency**: generation uses Groq via the `groq` package. `Generator` falls back to a template if `GROQ_API_KEY` is not set.
- **No tests/lint/typecheck configured**: `pyproject.toml` has no lint or test tooling.

## Architecture flow
`loader.py` → `splitter.py` → `embeddings.py` → `vectorstore.py` → `retriever.py` → `generator.py`, orchestrated by `pipeline.py`. `app.py` (Streamlit) and `main.py` (CLI) both call `RAGPipeline.ingest()` then `RAGPipeline.query()`.

## Where to get a Groq API key
https://console.groq.com/keys
