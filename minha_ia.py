from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
import requests, urllib.parse

def buscar_wikipedia(pergunta):
    try:
        termo = pergunta.lower()
        for p in ["quem é", "quem e", "me fala sobre", "fale sobre", "o que é", "o que e", "sobre", "quem foi"]:
            if p in termo:
                termo = termo.split(p)[-1].strip()
                break

        print(f" [Debug] Buscando por: '{termo}'")

        headers = {"User-Agent": "minha-primeira-ia/1.0"}

        # Tenta direto
        url = f"https://pt.wikipedia.org/api/rest_v1/page/summary/{urllib.parse.quote(termo)}"
        r = requests.get(url, headers=headers, timeout=10)

        # Se não achou, procura o título correto
        if r.status_code == 404:
            print(" [Debug] Não achou direto, procurando título correto...")
            search_url = f"https://pt.wikipedia.org/w/api.php?action=query&list=search&srsearch={urllib.parse.quote(termo)}&format=json&srlimit=1"
            busca = requests.get(search_url, headers=headers, timeout=10).json()
            if busca["query"]["search"]:
                titulo_certo = busca["query"]["search"][0]["title"]
                print(f" [Debug] Encontrei: '{titulo_certo}'")
                url = f"https://pt.wikipedia.org/api/rest_v1/page/summary/{urllib.parse.quote(titulo_certo)}"
                r = requests.get(url, headers=headers, timeout=10)

        dados = r.json()
        if "extract" in dados and dados["extract"]:
            return dados["extract"]
        else:
            return f"Não encontrei '{termo}' na Wikipedia."

    except Exception as e:
        return f"Erro técnico: {e}"

def pegar_dolar():
    try:
        dados = requests.get("https://economia.awesomeapi.com.br/last/USD-BRL", timeout=5).json()
        return f"O dólar hoje está R$ {float(dados['USDBRL']['bid']):.2f}"
    except:
        return "Não consegui pegar o dólar agora."

# --- Treino ---
frases = ["oi", "ola", "bom dia", "quanto custa o dolar", "cotacao dolar", "quem e einstein", "quem foi einstein", "me fala sobre python", "tchau"]
intencoes = ["saudacao", "saudacao", "saudacao", "dolar", "dolar", "wikipedia", "wikipedia", "wikipedia", "despedida"]

vet = TfidfVectorizer()
modelo = MultinomialNB()
modelo.fit(vet.fit_transform(frases), intencoes)

print("--- IA v3.1 CORRIGIDA ---")
while True:
    texto = input("\nVocê: ")
    if texto.lower() == "sair":
        break
    intencao = modelo.predict(vet.transform([texto]))[0]

    if intencao == "saudacao":
        print("Bot: Oi! Pergunte sobre dólar ou qualquer coisa da Wikipedia.")
    elif intencao == "dolar":
        print(f"Bot: {pegar_dolar()}")
    elif intencao == "wikipedia":
        print(f"Bot: {buscar_wikipedia(texto)}")