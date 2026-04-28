from langgraph.graph import StateGraph
from typing import TypedDict
import os

from app.core.llm import get_llm
from app.rag.retrieve import get_relevant_docs
from app.tools.quiz import generate_quiz
from app.tools.summary import generate_summary

llm = get_llm()


# 🧠 State
class AgentState(TypedDict):
    query: str
    history: list
    context: str
    task: str
    response: str
    source: str
    relevant: bool


# 🔹 Step 1: Detect intent (ONLY current query)
def detect_intent(state: AgentState):
    query = state["query"].lower()

    if "quiz" in query:
        task = "quiz"
    elif "summarize" in query or "summary" in query:
        task = "summary"
    else:
        task = "normal"

    return {**state, "task": task}


# 🔹 Step 2: Retrieve docs
def retrieve(state: AgentState):
    if not os.path.exists("data/index"):
        return {**state, "context": "", "relevant": False}

    docs_with_scores = get_relevant_docs(state["query"])

    docs = [doc for doc, score in docs_with_scores]
    scores = [score for doc, score in docs_with_scores]

    context = "\n\n".join([doc.page_content for doc in docs]) if docs else ""

    # 🔥 relevance threshold
    relevant = any(score < 0.5 for score in scores)

    return {
        **state,
        "context": context,
        "relevant": relevant
    }


# 🔹 Step 3: Route task (FINAL FIX)
def route_task(state: AgentState):
    query = state["query"]
    history = state.get("history", [])
    context = state["context"]
    task = state["task"]
    relevant = state["relevant"]

    source = "pdf" if relevant else "general"

    # 🧠 Build limited history (avoid confusion)
    history_text = ""
    for msg in history[-3:]:  # 🔥 limit memory influence
        history_text += f"{msg['role']}: {msg['content']}\n"

    # =========================
    # 🔵 GENERAL (NO PDF)
    # =========================
    if not relevant:
        if task == "quiz":
            prompt = generate_quiz(query)

        elif task == "summary":
            prompt = generate_summary(query)

        else:
            response = llm.invoke(f"""
You are a helpful assistant.

IMPORTANT:
- Answer ONLY the CURRENT question
- Ignore previous instructions like quiz or summary unless explicitly asked again

Conversation history:
{history_text}

Current question:
{query}
""")

            return {
                **state,
                "response": response.content,
                "source": source
            }

        response = llm.invoke(prompt)

        return {
            **state,
            "response": response.content,
            "source": source
        }

    # =========================
    # 🟢 PDF (RAG)
    # =========================
    if task == "quiz":
        prompt = generate_quiz(context)

    elif task == "summary":
        prompt = generate_summary(context)

    else:
        prompt = f"""
You are a helpful study assistant.

IMPORTANT:
- Answer ONLY the CURRENT question
- Do NOT continue previous tasks like quiz unless asked again

Conversation history:
{history_text}

Context:
{context}

Question:
{query}
"""

    response = llm.invoke(prompt)

    return {
        **state,
        "response": response.content,
        "source": source
    }


# 🔹 Build graph
def build_graph():
    builder = StateGraph(AgentState)

    builder.add_node("intent", detect_intent)
    builder.add_node("retrieve", retrieve)
    builder.add_node("route", route_task)

    builder.set_entry_point("intent")

    builder.add_edge("intent", "retrieve")
    builder.add_edge("retrieve", "route")

    return builder.compile()