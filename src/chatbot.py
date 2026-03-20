import os
from langchain_openai import ChatOpenAI
from src.config import OPENAI_API_KEY, OPENAI_MODEL, TOP_K
from src.prompts import SYSTEM_PROMPT
from src.vector_store import create_vector_store


class UniversityChatbot:
    def __init__(self):
        self.vector_store = create_vector_store()
        self.retriever = self.vector_store.as_retriever(search_kwargs={"k": TOP_K})
        self.llm = ChatOpenAI(
            openai_api_key=OPENAI_API_KEY,
            model=OPENAI_MODEL,
            temperature=0
        )

    def answer_question(self, question: str, chat_history, language: str = "English"):
        scored_results = self.vector_store.similarity_search_with_score(question, k=TOP_K)

        docs = [doc for doc, score in scored_results]
        scores = [score for doc, score in scored_results]

        context = "\n\n".join(
            [
                f"Source: {os.path.basename(doc.metadata.get('source', 'Unknown'))}\n"
                f"Page: {doc.metadata.get('page', 'N/A')}\n"
                f"Content:\n{doc.page_content}"
                for doc in docs
            ]
        )

        history_text = "\n".join(
            [f"{msg['role']}: {msg['content']}" for msg in chat_history]
        )

        user_prompt = f"""
Answer the following question in {language}.

Conversation history:
{history_text}

Question:
{question}

Context:
{context}
"""

        response = self.llm.invoke([
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt}
        ])

        confidence = self._estimate_confidence(scores)

        return response.content, docs, confidence

    def _estimate_confidence(self, scores):
        if not scores:
            return "Low"

        best_score = min(scores)

        if best_score < 0.4:
            return "High"
        elif best_score < 0.9:
            return "Medium"
        return "Low"