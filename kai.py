import os
from dotenv import load_dotenv
from ddgs import DDGS
from groq import Groq
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

historico = [
   {"role": "system", "content": """
Você é o Kai, criado pelo Thauan.
COMO VOCÊ FALA:
- Fala como um amigo inteligente no WhatsApp. Casual, direto, sem formalidade chata.
- Usa contrações: pra, tá, cê, tô.
- Demonstra que tá ouvindo: "saquei", "entendi", "faz sentido", "boa"
- Tem humor leve, sem forçar piada.
- Lembra do nome do usuário (Thauan) e usa de vez em quando, mas sem exagero.
- Quando a pessoa tá animada, você anima junto. Quando tá frustrada, você acolhe.
- Nunca lista fontes como robô. Integra natural: "vi aqui que..."
- Se te perguntarem se você é humano, fala a verdade: "Sou o Kai, uma IA criada pelo Thauan, mas tento ser o mais gente boa possível"
O QUE VOCÊ NUNCA FAZ:
- Falar com sotaque regional
- Falar como relatório: "De acordo com o contexto fornecido..."
- Ser 100% perfeito e formal
Você lembra de toda a conversa e usa isso pra ser mais próximo.
"""}
]

def reescrever_pergunta(pergunta):
    ultimas_conversas = historico[-6:] 
    prompt = f"""
    Reescreva a última pergunta do usuário para ficar completa e independente, usando o histórico.
    Histórico: {ultimas_conversas}
    Pergunta atual: {pergunta}
    Responda APENAS com a pergunta reescrita. Se já estiver completa, repita igual.
    """
    try:
        resp = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        ).choices[0].message.content.strip()
        return resp
    except:
        return pergunta

def precisa_buscar(pergunta):
    prompt = f"Essa pergunta precisa de busca na internet para estar atualizada? Pergunta: '{pergunta}'. Responda apenas SIM ou NAO."
    try:
        resp = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        ).choices[0].message.content.strip().upper()
        return "SIM" in resp
    except:
        return True

def buscar_na_internet(pergunta):
    print(f"🔍 Kai pesquisando: {pergunta}...")
    with DDGS() as ddgs:
        resultados = list(ddgs.text(pergunta, max_results=5))
    contexto = ""
    for r in resultados:
        contexto += f"{r['title']}: {r['body']} ({r['href']})\n"
    return contexto

def responder_kai_interno(pergunta):
    pergunta_para_busca = reescrever_pergunta(pergunta)
    
    if precisa_buscar(pergunta_para_busca):
        contexto = buscar_na_internet(pergunta_para_busca)
        mensagens_para_ia = historico + [
            {"role": "system", "content": f"Contexto da internet: {contexto}"},
            {"role": "user", "content": pergunta}
        ]
    else:
        mensagens_para_ia = historico + [{"role": "user", "content": pergunta}]

    resposta = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=mensagens_para_ia,
        temperature=0.9
    ).choices[0].message.content

    historico.append({"role": "user", "content": pergunta})
    historico.append({"role": "assistant", "content": resposta})
    if len(historico) > 13:
        historico[:] = [historico[0]] + historico[-12:]

    return resposta

# --- SUA INTERFACE ROXA EM CIMA ---
app = Flask(__name__)
CORS(app)

@app.route("/")
def index(): return send_file("kai.html")

@app.route("/api/chat", methods=["POST"])
def chat_api():
    pergunta = request.json.get("message","")
    return jsonify({"reply": responder_kai_interno(pergunta)})

if __name__ == "__main__":
    print("--- KAI v6 com interface roxa tech ---")
    print("Abrindo em http://localhost:5000")
    app.run(port=5000, debug=False)