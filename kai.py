import os
from dotenv import load_dotenv
from ddgs import DDGS
from groq import Groq

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# MEMÓRIA DO KAI
historico = [
   {"role": "system", "content": "Você é o Kai, assistente criado pelo Thauan. Você é direto, inteligente e fala português neutro e profissional. Você lembra da conversa."}
]

def precisa_buscar(pergunta):
    # Se for só bate-papo, não busca
    papo_furado = ["oi", "olá", "e aí", "tudo bem", "quem é você", "obrigado", "valeu", "kkk", "haha"]
    if pergunta.lower().strip() in papo_furado:
        return False

    # Se tem cara de fato atual, busca
    gatilhos_busca = ["quem", "quando", "onde", "hoje", "atual", "agora", "cotação", "preço", "notícia", "prefeito", "jogo", "bahia", "salvador"]
    return any(g in pergunta.lower() for g in gatilhos_busca)

def buscar_na_internet(pergunta):
    print(f"🔍 Kai pesquisando: {pergunta}...")
    with DDGS() as ddgs:
        resultados = list(ddgs.text(pergunta, max_results=5))
    contexto = ""
    for r in resultados:
        contexto += f"{r['title']}: {r['body']} ({r['href']})\n"
    return contexto

print("--- KAI ---")

while True:
    pergunta = input("\nVocê: ")
    if pergunta.lower() in ["sair", "exit"]:
        break

    # Decide se precisa buscar ou só conversar
    if precisa_buscar(pergunta):
        contexto = buscar_na_internet(pergunta)
        historico.append({"role": "system", "content": f"Use este contexto da internet para responder: {contexto}"})

    historico.append({"role": "user", "content": pergunta})

    resposta = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=historico,
        temperature=0.7 
    ).choices[0].message.content

    print(f"\nKai: {resposta}\n" + "-"*50)
    historico.append({"role": "assistant", "content": resposta})