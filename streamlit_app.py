import streamlit as st
import requests
import json
import os
import uuid

BASE_URL = "http://127.0.0.1:8000"
CHAT_FILE = "chats.json"

st.set_page_config(page_title="Study Assistant", layout="wide")

# -------------------------
# STORAGE
# -------------------------
def save_chats():
    with open(CHAT_FILE, "w") as f:
        json.dump(st.session_state["chats"], f)

def load_chats():
    if os.path.exists(CHAT_FILE):
        with open(CHAT_FILE, "r") as f:
            return json.load(f)
    return {}

# -------------------------
# SESSION INIT
# -------------------------
if "quiz" not in st.session_state:
    st.session_state.quiz = None

if "quiz_index" not in st.session_state:
    st.session_state.quiz_index = 0

if "score" not in st.session_state:
    st.session_state.score = 0

# -------------------------
# LOGIN
# -------------------------
def login():
    st.title("🔐 Login")

    user = st.text_input("Username")
    pwd = st.text_input("Password", type="password")

    if st.button("Login"):
        if user == "admin" and pwd == "admin123":
            st.session_state.logged_in = True
            st.success("Login successful")
            st.rerun()
        else:
            st.error("Invalid credentials")

# -------------------------
# MAIN APP
# -------------------------
def main_app():

    if "chats" not in st.session_state:
        st.session_state["chats"] = load_chats()

    if not st.session_state["chats"]:
        cid = str(uuid.uuid4())
        st.session_state["chats"][cid] = {
            "name": "Chat 1",
            "messages": []
        }
        st.session_state["current_chat"] = cid

    if "current_chat" not in st.session_state:
        st.session_state["current_chat"] = list(st.session_state["chats"].keys())[0]

    chat = st.session_state["chats"][st.session_state["current_chat"]]

    # -------------------------
    # SIDEBAR
    # -------------------------
    st.sidebar.title("📚 Study Assistant")

    file = st.sidebar.file_uploader("Upload PDF", type=["pdf"])

    if file:
        try:
            res = requests.post(
                f"{BASE_URL}/upload",
                files={"file": (file.name, file.getvalue(), "application/pdf")}
            )
            if res.status_code == 200:
                st.sidebar.success("Uploaded!")
            else:
                st.sidebar.error("Upload failed")
        except:
            st.sidebar.error("Backend not reachable")

    st.sidebar.divider()

    if st.sidebar.button("➕ New Chat"):
        cid = str(uuid.uuid4())
        st.session_state["chats"][cid] = {
            "name": f"Chat {len(st.session_state['chats'])+1}",
            "messages": []
        }
        st.session_state["current_chat"] = cid
        save_chats()
        st.rerun()

    st.sidebar.markdown("### Chats")

    for cid, c in st.session_state["chats"].items():
        if st.sidebar.button(c["name"], key=cid):
            st.session_state["current_chat"] = cid
            st.rerun()

    # -------------------------
    # CHAT UI
    # -------------------------
    st.title("🧠 Smart Study Assistant")

    for msg in chat["messages"]:
        if msg["role"] == "user":
            st.chat_message("user").write(msg["content"])
        else:
            st.chat_message("assistant").write(msg["content"])

            if msg.get("source") == "pdf":
                st.caption("📄 From Document")
            else:
                st.caption("🌐 General AI")

    # -------------------------
    # INPUT
    # -------------------------
    query = st.chat_input("Ask anything...")

    if query:

        chat["messages"].append({"role": "user", "content": query})
        st.chat_message("user").write(query)

        thinking = st.chat_message("assistant")
        thinking.write("🧠 Thinking...")

        try:
            res = requests.post(
                f"{BASE_URL}/chat",
                json={"query": query, "history": chat["messages"]}
            )

            data = res.json()

            # -------------------------
            # QUIZ TRIGGER (FIXED)
            # -------------------------
            if data.get("quiz_active"):
                st.session_state.quiz = data["quiz"]
                st.session_state.quiz_index = 0
                st.session_state.score = 0
                thinking.write("🎯 Quiz started!")

            else:
                answer = data["response"]
                source = data["source"]

                thinking.empty()
                st.chat_message("assistant").write(answer)

                if source == "pdf":
                    st.caption("📄 From Document")
                else:
                    st.caption("🌐 General AI")

                chat["messages"].append({
                    "role": "assistant",
                    "content": answer,
                    "source": source
                })

                save_chats()

        except Exception as e:
            thinking.write("Error")
            st.code(str(e))

    # -------------------------
    # QUIZ UI (IMPORTANT)
    # -------------------------
    if st.session_state.quiz:

        quiz = st.session_state.quiz["mcq_questions"]
        idx = st.session_state.quiz_index
        total = len(quiz)

        st.divider()
        st.subheader("🎯 Quiz")

        st.progress(idx / total if total else 0)

        if idx < total:

            q = quiz[idx]
            st.write(f"**Q{idx+1}: {q['question']}**")

            for opt in q["options"]:
                if st.button(opt, key=f"{idx}_{opt}"):

                    if opt.lower() == q["answer"].lower():
                        st.success("✅ Correct!")
                        st.session_state.score += 1
                    else:
                        st.error(f"❌ Correct answer: {q['answer']}")

                    st.session_state.quiz_index += 1
                    st.rerun()

        else:
            st.success(f"🏁 Final Score: {st.session_state.score}/{total}")

            if st.button("🔄 Restart Quiz"):
                st.session_state.quiz = None
                st.session_state.quiz_index = 0
                st.session_state.score = 0
                st.rerun()

# -------------------------
# APP FLOW
# -------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    login()
else:
    main_app()