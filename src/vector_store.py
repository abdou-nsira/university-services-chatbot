from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS

from src.config import OPENAI_API_KEY, EMBEDDING_MODEL
from src.loader import load_documents


def create_vector_store():
    documents = load_documents()

    embeddings = OpenAIEmbeddings(
        openai_api_key=OPENAI_API_KEY,
        model=EMBEDDING_MODEL
    )

    vector_store = FAISS.from_documents(documents, embeddings)
    return vector_store