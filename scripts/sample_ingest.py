# scripts/sample_ingest.py
import os
import requests
from dotenv import load_dotenv

load_dotenv()
API_URL = os.getenv("API_URL", "http://localhost:8000/tag")

samples = [
    "Paciente procura implante dentário, alta prioridade, interessado em parcelamento",
    "Calça jeans masculina tamanho M, lavagem escura, ótimo estado",
    "Cliente reclama sobre atraso no serviço e pede reembolso",
    "Procura consulta odontológica urgente, sangramento nas gengivas",
    "Interessado em financiamento, renda comprovada, pretende comprar em 6x",
    "Produto eletrônico com defeito, quer trocar por outro modelo",
    "Deseja limpeza dental e clareamento, primeira consulta",
    "Lead vindo do Facebook Ads, interage com oferta 'primeira consulta grátis'",
    "Procura aparelho ortodôntico invisível, procura preço",
    "Cliente quer orçamento para prótese removível",
    "Marcações de consulta para check-up anual, prefere manhã",
    "Usuário pergunta sobre formas de pagamento: cartão ou boleto",
    "Serviço de estética: aplicação de botox, procura disponibilidade",
    "Busca por emagrecimento: coach e dieta personalizada",
    "Contato comercial: revenda de equipamentos odontológicos",
    "Pergunta sobre prazo de entrega de produto",
    "Lead que respondeu positivamente à campanha de Natal",
    "Cliente insatisfeito com atendimento, solicita gerente",
    "Interesse em limpeza profunda e remoção de tártaro",
    "Paciente com urgência: dente quebrado após acidente",
]

def send(text):
    resp = requests.post(API_URL, json={"text": text})
    return resp.json()

if __name__ == "__main__":
    for s in samples:
        res = send(s)
        print("TEXT:", s)
        print("TAGS:", res.get("tags"))
        print("CONF:", res.get("confidence"))
        print("-" * 40)
