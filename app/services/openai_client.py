# app/services/openai_client.py
import os, re, json
from typing import Dict, Any
import httpx
from dotenv import load_dotenv

load_dotenv()  # garante que .env está carregado mesmo se main não carregar

SYSTEM_PROMPT = (
    "You are a tag generator. Given a product description or lead note, return JSON like: "
    '{"tags": ["tag1","tag2"], "confidence": 0.92}. Keep tags short, lowercase, 1-3 words.'
)

def _get_api_key() -> str:
    return os.getenv("OPENAI_API_KEY") or ""

async def generate_tags_openai(text: str) -> Dict[str, Any]:
    api_key = _get_api_key()
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY not configured")
    url = "https://api.openai.com/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}"}
    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role":"system","content": SYSTEM_PROMPT},
            {"role":"user","content": text}
        ],
        "max_tokens": 120,
        "temperature": 0.0
    }
    async with httpx.AsyncClient(timeout=20.0) as client:
        r = await client.post(url, headers=headers, json=payload)
        r.raise_for_status()
        j = r.json()

    # extrai texto da resposta
    reply = ""
    choices = j.get("choices") or []
    if choices:
        msg = choices[0].get("message") or choices[0]
        reply = msg.get("content") if isinstance(msg, dict) else str(msg)

    # tenta parsear JSON {tags, confidence}
    try:
        parsed = json.loads(reply)
        if isinstance(parsed, dict):
            tags = parsed.get("tags") or []
            conf = float(parsed.get("confidence", 0.9 if tags else 0.4))
            return {"tags": [str(t).lower().strip() for t in tags], "confidence": conf, "raw_reply": reply, "raw_api": j}
    except Exception:
        pass

    # fallback: tenta achar um array na string
    m = re.search(r"\{.*\"tags\".*\}", reply, re.S)
    if m:
        try:
            parsed = json.loads(m.group(0))
            tags = parsed.get("tags") or []
            conf = float(parsed.get("confidence", 0.9 if tags else 0.4))
            return {"tags": [str(t).lower().strip() for t in tags], "confidence": conf, "raw_reply": reply, "raw_api": j}
        except Exception:
            pass

    # sem parse: devolve vazio com confiança baixa
    return {"tags": [], "confidence": 0.4, "raw_reply": reply, "raw_api": j}
