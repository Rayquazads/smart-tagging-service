# app/services/ac_client.py
import os, requests
from typing import List, Optional, Dict, Any
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv(), override=True)  # garante .env

def _get_env(k:str)->str:
    return (os.getenv(k) or "").strip()

AC_API_KEY = _get_env("AC_API_KEY")
AC_API_BASE = _get_env("AC_API_BASE")

def _headers():
    h = {"Content-Type": "application/json"}
    if AC_API_KEY:
        h["Api-Token"] = AC_API_KEY
    return h

def ac_env_status() -> Dict[str, bool]:
    ok_url = bool(AC_API_BASE)
    ok_key = bool(AC_API_KEY)
    ping = False
    if ok_url and ok_key:
        try:
            r = requests.get(f"{AC_API_BASE}/tags", headers=_headers(), timeout=8)
            ping = (r.status_code == 200)
        except Exception:
            ping = False
    return {"url": ok_url, "key": ok_key, "ping": ping}

# ---------- funções já existentes (ajuste para usar _headers) ----------
def find_contact_by_email(email: str) -> Optional[int]:
    if not AC_API_BASE or not AC_API_KEY:
        return None
    url = f"{AC_API_BASE}/contacts?email={email}"
    r = requests.get(url, headers=_headers(), timeout=10)
    if r.status_code != 200:
        return None
    data = r.json()
    contacts = data.get("contacts") or []
    if contacts:
        return int(contacts[0]["id"])
    return None

def create_contact(email: str) -> Optional[int]:
    if not AC_API_BASE or not AC_API_KEY:
        return None
    url = f"{AC_API_BASE}/contacts"
    payload = {"contact": {"email": email}}
    r = requests.post(url, headers=_headers(), json=payload, timeout=10)
    if r.status_code not in (200, 201):
        return None
    data = r.json()
    return int(data.get("contact", {}).get("id"))

def assign_tag(contact_id: int, tag_id: int) -> Dict[str, Any]:
    if not AC_API_BASE or not AC_API_KEY:
        return {"error": "ac_not_configured"}
    url = f"{AC_API_BASE}/contactTags"
    payload = {"contactTag": {"contact": contact_id, "tag": tag_id}}
    r = requests.post(url, headers=_headers(), json=payload, timeout=10)
    try:
        return r.json()
    except Exception:
        return {"status_code": r.status_code, "text": r.text}

# ---- auto buscar/criar tags (como te passei antes) ----
def fetch_all_tags() -> Dict[str, int]:
    if not AC_API_BASE or not AC_API_KEY:
        return {}
    url = f"{AC_API_BASE}/tags"
    r = requests.get(url, headers=_headers(), timeout=15)
    r.raise_for_status()
    data = r.json()
    return { (t.get("tag") or "").lower(): int(t["id"]) for t in data.get("tags", []) if t.get("id") }

_TAG_CACHE: Dict[str,int] = {}

def get_tag_id_by_name(name: str) -> Optional[int]:
    global _TAG_CACHE
    if not _TAG_CACHE:
        try:
            _TAG_CACHE = fetch_all_tags()
        except Exception:
            _TAG_CACHE = {}
    return _TAG_CACHE.get((name or "").lower().strip())

def ensure_tag_exists(name: str) -> Optional[int]:
    if not AC_API_BASE or not AC_API_KEY:
        return None
    tag_id = get_tag_id_by_name(name)
    if tag_id:
        return tag_id
    url = f"{AC_API_BASE}/tags"
    payload = {"tag": {"tag": name, "tagType": "contact"}}
    r = requests.post(url, headers=_headers(), json=payload, timeout=15)
    if r.status_code not in (200, 201):
        return None
    try:
        data = r.json()
        new_id = int(data.get("tag", {}).get("id"))
        _TAG_CACHE.clear()
        return new_id
    except Exception:
        return None

def find_or_create_contact_and_assign_tags(email: str, tags: List[str]) -> Dict[str, Any]:
    if not AC_API_BASE or not AC_API_KEY:
        return {"error": "ac_not_configured"}
    contact_id = find_contact_by_email(email)
    if not contact_id:
        contact_id = create_contact(email)
    assigned = []
    for t in tags:
        tag_id = ensure_tag_exists(t)
        if tag_id and contact_id:
            res = assign_tag(contact_id, tag_id)
            assigned.append({"tag": t, "tag_id": tag_id, "res": res})
    return {"contact_id": contact_id, "assigned": assigned}
