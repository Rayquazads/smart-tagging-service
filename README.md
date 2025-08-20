# Smart Tagging Service

API para gerar tags a partir de textos (leads / produtos), salvar auditoria no Supabase e (opcional) aplicar tags no ActiveCampaign.

## Quickstart

1. Clone / crie pasta do projeto.
2. Crie e ative virtualenv:
   - Windows PowerShell:
     ```powershell
     python -m venv .venv
     .\.venv\Scripts\Activate.ps1
     ```
   - macOS / Linux:
     ```bash
     python -m venv .venv
     source .venv/bin/activate
     ```
3. Instale dependências:
```bash
pip install -r requirements.txt
