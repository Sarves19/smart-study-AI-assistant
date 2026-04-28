# Smart Study Assistant

An AI-powered study assistant that allows users to:
-  Upload PDFs
-  Ask questions
-  Get answers from documents or general knowledge
-  Maintain chat history

Built using **FastAPI + Streamlit + LangChain + FAISS**

---

## 🚀 Features

### ✅ Document Understanding (RAG)
- Upload PDF files
- Extracts and splits content into chunks
- Uses embeddings + vector search to retrieve relevant information

### ✅ Smart Chat System
- Ask questions about uploaded documents
- Falls back to general knowledge if not found in PDF

### ✅ Multi-Chat Support
- Create multiple chat sessions
- Switch between chats
- Persistent chat history

### ✅ Clean UI (Streamlit)
- ChatGPT-like interface
- Sidebar with chats + file upload
- Real-time "Analyzing..." feedback

---

## 🏗️ Tech Stack

| Layer        | Technology |
|-------------|-----------|
| Backend      | FastAPI |
| Frontend     | Streamlit |
| LLM / RAG    | LangChain |
| Vector DB    | FAISS |
| Embeddings   | OpenAI Embeddings |
| Storage      | JSON (chat history) |

---


