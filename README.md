# 🧠 Smart Tagging Service

Microserviço em **FastAPI** que usa **OpenAI** para analisar textos de leads e gerar **tags inteligentes** automaticamente.  
As tags e os metadados são salvos no **Supabase** e (opcionalmente) aplicados no **ActiveCampaign** para segmentação/automação.

## ✨ Funcionalidades

- 🔎 Classificação de textos com IA → gera **tags** e **confiança**  
- 🗄️ Persistência no **Supabase** (histórico e auditoria)  
- 🎯 Integração com **ActiveCampaign** (aplica tags no contato)  
- 📦 **/tag/batch** para processar vários itens de uma vez  
- 🧰 Documentação automática em `/docs` (Swagger)

## 📁 Estrutura

```
smart-tagging-service/
│── app/
│ ├── main.py # Endpoints FastAPI
│ └── services/
│ ├── openai_client.py # OpenAI (geração de tags)
│ ├── supabase_client.py # Supabase (persistência)
│ └── ac_client.py # ActiveCampaign (contatos/tags)
│── scripts/
│ └── sample_ingest.py # Exemplo de ingestão em lote
│── .env.example # Modelo de variáveis de ambiente
│── requirements.txt # Dependências
│── docker-compose.yml # Subir com Docker
│── Dockerfile # Build da imagem
│── README.md # Este arquivo
```
> **Importante:** mantenha **`.env` fora do Git** (já coberto no `.gitignore`).  
> Comite **`.env.example`** para servir de referência.

## 🔧 Pré-requisitos

- Python **3.10+**
- Conta/keys de **OpenAI**
- Projeto **Supabase** (URL + service role)
- (Opcional) Conta **ActiveCampaign** (API URL + API Token)
- Git / Docker (opcional)

## ⚙️ Configuração

### 1) Clonar o repositório
```bash
git clone https://github.com/<seu-usuario>/smart-tagging-service.git
cd smart-tagging-service
```
### 2) Criar e preencher o .env 
```bash
cp .env.example .env
```
# OpenAI
OPENAI_API_KEY=

# ActiveCampaign
AC_API_KEY=
AC_API_BASE=https://<sua-conta>.api-us1.com/api/3

# Supabase
SUPABASE_URL=https://<seu-projeto>.supabase.co
SUPABASE_KEY=<service_role_key>

# Comportamento
MOCK_OPENAI=false
API_URL=http://localhost:8000/tag

### 3) (Supabase) Criar tabela de logs
```SQL
create table if not exists public.tag_logs (
  id bigserial primary key,
  created_at timestamptz default now(),
  source text,
  external_id text,
  email text,
  input_text text,
  tags jsonb,
  confidence numeric,
  model_response jsonb,
  ac_response jsonb,
  processed boolean default false
);
create index if not exists idx_tag_logs_created_at on public.tag_logs (created_at desc);
```
### 4) Instalar dependências
```bash
python -m venv .venv
```
# Windows
```bash
.\.venv\Scripts\activate
```
# macOS/Linux
```bash
source .venv/bin/activate
```
```bash
pip install -r requirements.txt
```
### 5) Subir a API
``` bash
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

---

### 6) — ▶️ Exemplos de Uso
### Healthcheck
```bash
curl http://127.0.0.1:8000/health
```

**Classificar um texto**
```bash
curl -X POST "http://127.0.0.1:8000/tag" \
  -H "Content-Type: application/json" \
  -d '{"text":"Paciente procura implante dentário, quer parcelar"}'
```
**Classificar + aplicar tags no ActiveCampaign**
```bash
curl -X POST "http://127.0.0.1:8000/tag?debug=true" \
  -H "Content-Type: application/json" \
  -d '{"text":"Paciente procura implante dentário, quer parcelar", "email":"lead@exemplo.com"}'
```

**Lote (/tag/batch)**
```bash
curl -X POST "http://127.0.0.1:8000/tag/batch" \
  -H "Content-Type: application/json" \
  -d '[{"text":"Paciente quer implante e parcelamento"},
      {"text":"Clareamento e limpeza"}]'
```
  
---


---

### **7) — Boas práticas**
```markdown
## 🔐 Boas práticas

- **Nunca** comite `.env` ou chaves → use `.env.example` como referência.  
- Em produção, defina as variáveis de ambiente no provedor (Render, Railway, Fly, etc.).  
- Use `MOCK_OPENAI=true` para testar sem custo.  
- No Windows, evite `--reload` se notar processos “presos” (use uma porta alternativa ou reinicie).
```

## 🗺️ Roadmap

- [ ] Testes unitários/integração (pytest)  
- [ ] Normalização de tags (acentos/variações)  
- [ ] Fila assíncrona para alto volume (RQ/Celery)  
- [ ] Dashboard de métricas no Supabase / Metabase  
- [ ] Webhook para processar leads de formulários/WhatsApp

 ## 🙋‍♂️ Autor

**Gabriel Costa**  
LinkedIn: https://www.linkedin.com/in/gabriel-costa-a565a5331/

---

## 📄 Licença

Este projeto pode ser usado livremente para fins de estudo e demonstração.  
Adapte a licença conforme sua necessidade (MIT é uma boa opção).



