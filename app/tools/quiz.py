from langchain_openai import ChatOpenAI
import os
import json

llm = ChatOpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    model="gpt-4o-mini"
)

def generate_quiz(context):
    prompt = f"""
    Create 5 MCQ questions.

    Return STRICT JSON:
    {{
      "mcq_questions": [
        {{
          "question": "...",
          "options": ["A", "B", "C", "D"],
          "answer": "A"
        }}
      ]
    }}

    Content:
    {context}
    """

    response = llm.invoke(prompt).content

    try:
        return json.loads(response)
    except:
        return {"mcq_questions": []}