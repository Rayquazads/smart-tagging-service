# app/main.py (topo do arquivo)

from dotenv import load_dotenv
load_dotenv()  # <-- carrega .env antes de importar os services

import os, json
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, Query
from pydantic import BaseModel

from app.services.openai_client import generate_tags_openai
from app.services.supabase_client import save_log_to_supabase, supabase_env_status
from app.services.ac_client import find_or_create_contact_and_assign_tags, ac_env_status

load_dotenv()
MOCK_OPENAI = os.getenv("MOCK_OPENAI", "true").lower() in ("1","true","yes")
app = FastAPI(title="Smart Tagging Service")

class TagRequest(BaseModel):
    text: str
    context: Optional[Dict[str, Any]] = {}
    source: Optional[str] = "lead"
    external_id: Optional[str] = None
    email: Optional[str] = None

class TagResponse(BaseModel):
    tags: List[str]
    confidence: float
    raw: Dict[str, Any] = {}

class BatchItem(TagRequest): pass


def simple_keyword_tags(text: str) -> List[str]:
    t = text.lower()
    tags = set()
    keywords = {
        "implante": "implante",
        "consulta": "intencao:marcar-consulta",
        "parcelamento": "financeiro:parcelamento",
        "credito": "financeiro:credito",
        "barato": "faixa_preco:baixo",
        "caro": "faixa_preco:alto",
        "urgente": "lead:urgente",
        "emagrecimento": "interesse:emagrecimento",
        "ortodontia": "especialidade:ortodontia",
        "extracao": "procedimento:extracao",
    }
    for kw, tag in keywords.items():
        if kw in t:
            tags.add(tag)
    if not tags:
        parts = [p for p in t.split() if len(p) >= 3]
        tags.update(parts[:3])
    return list(tags)

@app.get("/health")
async def health():
    return {
        "status": "ok",
        "mock": MOCK_OPENAI,
        "openai_key": bool(os.getenv("OPENAI_API_KEY")),
        "supabase": supabase_env_status(),
        "activecampaign": ac_env_status(),
    }

@app.post("/tag")
async def tag_endpoint(req: TagRequest, debug: bool = Query(False)):
    text = req.text.strip()
    result = await generate_tags_openai(text)

    # loga no supabase (não quebra se falhar)
    supa = save_log_to_supabase({
        "source": "lead",
        "external_id": None,
        "input_text": text,
        "tags": json.dumps(result["tags"]),
        "confidence": result.get("confidence", 0.0),
        "model_response": {"openai": {k: v for k, v in result.items() if k != "raw_api"}},
        "processed": True,
    })

    ac = None
    if req.email:
        ac = find_or_create_contact_and_assign_tags(req.email, result["tags"])

    # resposta enxuta por padrão
    resp = {"tags": result["tags"], "confidence": result.get("confidence", 0.0)}
    if debug:
        resp["raw"] = {"model": result}                # inclui raw_api só no debug
        resp["supabase"] = supa
        resp["activecampaign"] = ac
    return resp

@app.post("/tag/batch")
async def tag_batch(items: List[BatchItem], debug: bool = Query(False)):
    out = []
    for it in items:
        out.append(await tag_endpoint(it, debug=debug))
    return {"count": len(out), "items": out}