from fastapi import FastAPI
from dotenv import load_dotenv
import os

# ✅ LOAD ENV VARIABLES
load_dotenv()

print("🔑 API KEY LOADED:", os.getenv("OPENAI_API_KEY"))

from app.routes import chat, upload

app = FastAPI()

app.include_router(chat.router)
app.include_router(upload.router)