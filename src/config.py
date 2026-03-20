import os
from dotenv import load_dotenv

load_dotenv()

try:
    import streamlit as st
    STREAMLIT_AVAILABLE = True
except Exception:
    STREAMLIT_AVAILABLE = False


def get_secret(name: str, default=None):
    value = os.getenv(name)
    if value:
        return value

    if STREAMLIT_AVAILABLE:
        try:
            return st.secrets[name]
        except Exception:
            pass

    return default


OPENAI_API_KEY = get_secret("OPENAI_API_KEY")
OPENAI_MODEL = get_secret("OPENAI_MODEL", "gpt-4.1-mini")
EMBEDDING_MODEL = get_secret("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")

DOCS_PATH = "data/docs"
CHUNK_SIZE = 800
CHUNK_OVERLAP = 150
TOP_K = 4