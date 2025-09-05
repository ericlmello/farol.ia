import os
import httpx
import json
import asyncio
import websockets
from dotenv import load_dotenv

# --- INÍCIO DO SCRIPT DE TESTE AVANÇADO ---

# Tenta carregar o ficheiro .env da pasta atual.
print("A tentar carregar o ficheiro .env...")
load_dotenv()

# Lê todas as variáveis de ambiente relevantes.
api_key = os.getenv("OPENAI_API_KEY")
model = os.getenv("MODEL", "gpt-4o") # Usa gpt-4o como padrão se não for encontrado
voice = os.getenv("VOICE", "marin") # Usa marin como padrão se não for encontrado

print("\n--- 1. Verificação das Variáveis de Ambiente ---")
if api_key:
    print(f"✅ Sucesso! A variável OPENAI_API_KEY foi encontrada.")
    print(f"   - Início da chave: {api_key[:7]}...")
    print(f"   - Fim da chave: ...{api_key[-4:]}")
else:
    print("❌ Falha! A variável OPENAI_API_KEY não foi encontrada.")
    print("   Por favor, verifique o seu ficheiro '.env'.")

print(f"   - Modelo a ser usado: {model}")
print(f"   - Voz a ser usada: {voice}")
print("------------------------------------------------\n")


# --- 2. Teste de Validação da API ---
def test_openai_api_authentication():
    if not api_key:
        print("--- 2. Teste de Autenticação Ignorado (Chave não encontrada) ---")
        return False

    print("--- 2. A tentar validar a chave com a API da OpenAI... ---")
    
    headers = { "Authorization": f"Bearer {api_key}" }
    url = "https://api.openai.com/v1/models"
    
    try:
        with httpx.Client(timeout=20.0) as client:
            response = client.get(url, headers=headers)
            print(f"   - Status da resposta da API: {response.status_code}")
            
            if response.status_code == 200:
                print("✅ Sucesso! A sua chave de API é válida.")
                return True
            elif response.status_code == 401:
                print("❌ Falha de Autenticação! A sua chave de API é inválida ou foi revogada.")
            else:
                print(f"❌ Falha! A API retornou um erro inesperado. Detalhes: {response.text[:200]}")
    except httpx.RequestError as e:
        print(f"❌ Falha de Conexão! Não foi possível contactar a OpenAI.")
        print(f"   - Detalhes do erro: {e}")
    
    return False

# --- 3. Teste de Sessão de Voz em Tempo Real (Método Seguro) ---
def test_realtime_voice_session():
    print("\n--- 3. A tentar criar uma Sessão de Voz (Método Seguro)... ---")
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "OpenAI-Beta": "realtime=v1",
    }
    payload = {
        "model": model,
        "voice": voice,
        "input_audio_format": "pcm16",
    }
    url = "https://api.openai.com/v1/realtime/sessions"

    try:
        with httpx.Client(timeout=20.0) as client:
            response = client.post(url, headers=headers, json=payload)
            print(f"   - Status da resposta da API: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                if "websocket" in data and "url" in data["websocket"]:
                    print("✅ Sucesso! O método seguro funciona com a sua conta.")
                else:
                    print("❌ FALHA DE ACESSO! A sua conta não tem permissão para esta funcionalidade (método seguro).")
            else:
                print(f"❌ Falha! A API retornou um erro ao tentar criar a sessão. Detalhes: {response.text[:300]}")

    except httpx.RequestError as e:
        print(f"❌ Falha de Conexão! Não foi possível contactar a OpenAI.")

# --- 4. Teste de Ligação Direta (Método Inseguro da Documentação) ---
async def test_insecure_websocket_connection():
    print("\n--- 4. A tentar ligar diretamente via WebSocket (Método Inseguro)... ---")
    if not api_key:
        print("   - Teste ignorado (Chave não encontrada).")
        return

    # AVISO: Este método expõe a sua chave de API. Não use em produção.
    uri = f"wss://api.openai.com/v1/realtime?model={model}"
    subprotocols = ["realtime", f"openai-insecure-api-key.{api_key}"]

    try:
        async with websockets.connect(uri, subprotocols=subprotocols) as ws:
            print("✅ SUCESSO FINAL! A sua conta tem acesso à API de Voz através do método de ligação direta.")
            print("   - Isto confirma que o problema está na forma como a OpenAI gere as sessões seguras para a sua conta.")
            print("   - SOLUÇÃO: Será necessário adaptar a aplicação principal para usar este método (com os devidos cuidados de segurança).")
            await ws.close()
    except websockets.exceptions.InvalidStatusCode as e:
        print(f"❌ FALHA DE ACESSO! O servidor rejeitou a ligação (Status: {e.status_code}).")
        print("   - Isto confirma que a sua conta não tem acesso a esta funcionalidade, independentemente do método.")
        print("   - SOLUÇÃO FINAL: Verifique o seu plano na OpenAI ou contacte o suporte deles.")
    except Exception as e:
        print(f"❌ Falha! Ocorreu um erro inesperado ao tentar a ligação direta. Detalhes: {e}")

# --- Execução dos Testes ---
if test_openai_api_authentication():
    test_realtime_voice_session()
    asyncio.run(test_insecure_websocket_connection())

print("\n------------------------------------------------------------------")
print("Diagnóstico concluído.")
# --- FIM DO SCRIPT DE TESTE ---
