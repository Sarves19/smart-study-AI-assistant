from fastapi import APIRouter
from pydantic import BaseModel
from app.rag.retrieve import get_relevant_docs
from app.tools.quiz import generate_quiz
from langchain_openai import ChatOpenAI
import os

router = APIRouter()

class ChatRequest(BaseModel):
    query: str
    history: list = []

llm = ChatOpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    model="gpt-4o-mini"
)

@router.post("/chat")
async def chat(request: ChatRequest):

    query = request.query.lower()

    docs = get_relevant_docs(query)

    # -------------------------
    # 📄 DOCUMENT CASE
    # -------------------------
    if docs and len(docs) > 0:

        context = "\n\n".join([doc.page_content for doc in docs])

        # 🎯 QUIZ TRIGGER (STRICT)
        quiz_keywords = [
            "create quiz",
            "generate quiz",
            "quiz from document",
            "quiz from pdf"
        ]

        if any(k in query for k in quiz_keywords):

            quiz = generate_quiz(context)

            return {
                "response": "Quiz started!",
                "source": "pdf",
                "quiz_active": True,
                "quiz": quiz
            }

        # 📄 DOCUMENT ANSWER (STRICT)
        prompt = f"""
        Answer ONLY using the document below.
        If the answer is not found, reply ONLY with: NOT FOUND

        Document:
        {context}

        Question:
        {query}
        """

        answer = llm.invoke(prompt).content

        # 🔥 FALLBACK CHECK
        if "NOT FOUND" in answer.upper():

            general_answer = llm.invoke(query).content

            return {
                "response": general_answer,
                "source": "general"
            }

        return {
            "response": answer,
            "source": "pdf"
        }

    # -------------------------
    # 🌐 GENERAL CASE
    # -------------------------
    general_answer = llm.invoke(query).content

    return {
        "response": general_answer,
        "source": "general"
    }