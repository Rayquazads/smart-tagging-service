# app/services/supabase_client.py
import os
from typing import Dict, Any
from dotenv import load_dotenv, find_dotenv
from supabase import create_client

load_dotenv(find_dotenv(), override=True)  # carrega .env sempre (inclusive no reloader)

_client = None  # singleton

def _get_env(k: str) -> str:
    return (os.getenv(k) or "").strip()

def _build_client():
    url = _get_env("SUPABASE_URL")
    key = _get_env("SUPABASE_KEY")
    if not url or not key:
        return None
    try:
        return create_client(url, key)
    except Exception:
        # se der erro de URL/chave, não derruba a app
        return None

def _get_client():
    global _client
    if _client is None:
        _client = _build_client()
    return _client

def save_log_to_supabase(record: Dict[str, Any]) -> Dict[str, Any]:
    client = _get_client()
    if client is None:
        return {"error": "supabase_not_configured"}
    try:
        res = client.table("tag_logs").insert(record).execute()
        return {"ok": True, "data": getattr(res, "data", None)}
    except Exception as e:
        return {"error": str(e)}

def supabase_env_status() -> Dict[str, bool]:
    return {
        "url": bool(_get_env("SUPABASE_URL")),
        "key": bool(_get_env("SUPABASE_KEY")),
        "client": _get_client() is not None,
    }
