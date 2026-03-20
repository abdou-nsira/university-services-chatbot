from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from src.config import DOCS_PATH, CHUNK_SIZE, CHUNK_OVERLAP


def load_documents():
    docs = []
    docs_path = Path(DOCS_PATH)

    for file_path in docs_path.iterdir():
        if file_path.suffix.lower() == ".pdf":
            loader = PyPDFLoader(str(file_path))
            docs.extend(loader.load())
        elif file_path.suffix.lower() in [".txt", ".md"]:
            loader = TextLoader(str(file_path), encoding="utf-8")
            docs.extend(loader.load())

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP
    )

    split_docs = text_splitter.split_documents(docs)
    return split_docs