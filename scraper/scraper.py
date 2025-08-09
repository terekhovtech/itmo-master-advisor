import os
import json
import hashlib
import datetime
import requests
from bs4 import BeautifulSoup

DATA_DIR = os.environ.get("DATA_DIR", "./data")
os.makedirs(DATA_DIR, exist_ok=True)

PROGRAMS = {
    "ai": "https://abit.itmo.ru/program/master/ai",
    "ai_product": "https://abit.itmo.ru/program/master/ai_product"
}

def fetch(url):
    headers = {"User-Agent": "itmo-master-advisor/1.0"}
    r = requests.get(url, headers=headers, timeout=15)
    r.raise_for_status()
    return r.text

def content_hash(text):
    return hashlib.sha256(text.encode('utf-8')).hexdigest()

def parse_program(html, source_url):
    soup = BeautifulSoup(html, "lxml")
    title = soup.select_one("h1")
    title_text = title.get_text(strip=True) if title else source_url
    desc = soup.select_one("meta[name='description']")
    desc_text = desc["content"] if desc and desc.get("content") else ""
    # try to collect links that look like "учебн"
    plan_link = None
    for a in soup.find_all("a"):
        txt = a.get_text(" ", strip=True).lower()
        if "учебн" in txt or "учебный" in txt or "учебный план" in txt:
            plan_link = a.get("href")
            break
    # Collect headings and paragraphs as simple "courses" proxy
    items = []
    for tag in soup.select("h2, h3, li"):
        txt = tag.get_text(" ", strip=True)
        if txt and len(txt) < 200:
            items.append(txt)
    return {
        "title": title_text,
        "description": desc_text,
        "plan_link": plan_link,
        "items": items,
        "source_url": source_url
    }

def save(key, payload, raw_html, hsh):
    path = os.path.join(DATA_DIR, f"{key}.json")
    meta = {
        "fetched_at": datetime.datetime.utcnow().isoformat() + "Z",
        "content_hash": hsh,
    }
    obj = {"meta": meta, "data": payload}
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
    with open(os.path.join(DATA_DIR, f"{key}.html"), "w", encoding="utf-8") as f:
        f.write(raw_html)
    return path

def is_fresh(key, max_age_hours=24):
    path = os.path.join(DATA_DIR, f"{key}.json")
    if not os.path.exists(path):
        return False
    with open(path, "r", encoding="utf-8") as f:
        obj = json.load(f)
    fetched = obj["meta"].get("fetched_at")
    if not fetched:
        return False
    dt = datetime.datetime.fromisoformat(fetched.replace("Z",""))
    age = (datetime.datetime.utcnow() - dt).total_seconds()
    return age < max_age_hours * 3600

def update_if_needed(key):
    url = PROGRAMS.get(key)
    if not url:
        raise ValueError("Unknown program key")
    if is_fresh(key):
        with open(os.path.join(DATA_DIR, f"{key}.json"), "r", encoding="utf-8") as f:
            return json.load(f)["data"]
    html = fetch(url)
    h = content_hash(html)
    parsed = parse_program(html, url)
    save(key, parsed, html, h)
    return parsed

if __name__ == '__main__':
    # quick test run: update both
    for k in PROGRAMS:
        print("Updating", k)
        data = update_if_needed(k)
        print(data['title'])
