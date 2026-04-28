from langchain_openai import ChatOpenAI
import os

llm = ChatOpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    model="gpt-4o-mini"
)

def generate_summary(context):
    prompt = f"""
    Summarize the following content clearly in 5-6 bullet points:

    {context}
    """

    return llm.invoke(prompt).content