import os
import json
from typing import List
import requests
from dotenv import load_dotenv
from math import sqrt

load_dotenv()

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")
if not OPENROUTER_API_KEY:
    raise RuntimeError("OPENROUTER_API_KEY not set in environment")

DATA_DIR = os.environ.get("DATA_DIR", "./data")

# Бесплатные модели на OpenRouter
EMBEDDING_MODEL = "mistral/mistral-embed"  # эмбеддинги
CHAT_MODEL = "mistral/mistral-7b-instruct"  # генерация ответов

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

headers = {
    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
    "HTTP-Referer": "http://localhost",  # можно указать свой домен
    "X-Title": "ITMO Master Advisor"
}

def embed_text(text: str) -> List[float]:
    resp = requests.post(
        f"{OPENROUTER_BASE_URL}/embeddings",
        headers=headers,
        json={"model": EMBEDDING_MODEL, "input": text}
    )
    resp.raise_for_status()
    return resp.json()["data"][0]["embedding"]

def load_program(key: str):
    path = os.path.join(DATA_DIR, f"{key}.json")
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)["data"]

def cosine(a, b):
    da = sqrt(sum(x * x for x in a))
    db = sqrt(sum(x * x for x in b))
    if da == 0 or db == 0:
        return 0.0
    return sum(x * y for x, y in zip(a, b)) / (da * db)

def retrieve_relevant(program_key: str, query: str, top_k=5):
    prog = load_program(program_key)
    if not prog:
        return []
    candidates = []
    emb_q = embed_text(query)
    for item in prog.get("items", []):
        try:
            emb_item = embed_text(item)
            score = cosine(emb_item, emb_q)
            candidates.append((score, item))
        except Exception:
            if query.lower() in item.lower():
                candidates.append((1.0, item))
    candidates.sort(key=lambda x: x[0], reverse=True)
    return [c for s, c in candidates[:top_k]]

def answer_question(program_key: str, query: str):
    hits = retrieve_relevant(program_key, query, top_k=5)
    if not hits:
        return "Я могу отвечать только на вопросы, связанные с контентом программ. Не нашёл релевантных фрагментов."

    prompt = "Ты помощник абитуриента. Используя приведённые фрагменты, дай короткий ответ на вопрос:\n\n"
    for i, h in enumerate(hits, 1):
        prompt += f"Фрагмент {i}: {h}\n"
    prompt += f"Вопрос: {query}\nОтвет:"

    resp = requests.post(
        f"{OPENROUTER_BASE_URL}/chat/completions",
        headers=headers,
        json={
            "model": CHAT_MODEL,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 300,
            "temperature": 0.0
        }
    )
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"].strip()
