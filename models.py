import requests
from config import OPENROUTER_API_KEY, OPENROUTER_MODEL

OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"

def generate_response(messages, model=None):
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://your-app.com",
        "X-Title": "LINE AI Chatbot"
    }

    payload = {
        "model": model or OPENROUTER_MODEL,
        "messages": messages,
        "max_tokens": 1000,
        "temperature": 0.5
    }

    response = requests.post(OPENROUTER_API_URL, headers=headers, json=payload, timeout=60)
    response.raise_for_status()
    data = response.json()

    return data["choices"][0]["message"]["content"]

def build_rag_prompt(user_query, retrieved_docs):
    context = "\n\n".join([f"- {doc['content']}" for doc in retrieved_docs])

    system_prompt = f"""You are a helpful AI assistant. Use the following context to answer the user's question. If the context doesn't contain relevant information, say so.

Context:
{context}
"""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_query}
    ]

    return messages
