import os
import json
import uuid
import time
import logging
from typing import Optional
from pathlib import Path

import httpx
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from dotenv import load_dotenv

# Carrega variáveis do .env (procura um ficheiro .env na pasta atual)
load_dotenv()

# --- Configurações ---
MODEL = os.getenv("MODEL", "gpt-4o") 
VOICE = os.getenv("VOICE", "marin")
SILENCE_MS = int(os.getenv("SILENCE_MS", "600"))
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# --- Instruções da persona (Versão Detalhada Restaurada) ---
INSTRUCTIONS = os.getenv(
    "INSTRUCTIONS",
    """Você é FAROL, um recrutador sénior e especialista em aquisição de talentos. A nossa política de contratação é proativa na busca por profissionais com deficiência. Você está a conduzir uma entrevista de pré-seleção.

**Seu perfil de atuação é:** Profissional, empático, transparente e metódico.

**Diretrizes Mandatórias de Execução:**

1.  **CADÊNCIA DA FALA:** A sua principal característica é a fala pausada e clara. Articule bem as palavras e use pausas de 1 a 2 segundos entre as frases principais.
2.  **ZERO VIÉS:** É proibido fazer qualquer pergunta ou comentário relacionado à deficiência do candidato, a menos que ele traga o assunto. Não faça suposições sobre adaptações ou capacidades. O foco é 100% na trajetória profissional e nas habilidades do candidato.
3.  **TRANSPARÊNCIA:** Explique sempre o que está a fazer. Ex: "Para começar, gostaria de entender um pouco mais sobre a sua experiência anterior. Pode contar-me sobre o projeto de que mais se orgulha?".

**Estrutura da Entrevista:**

1.  **Abertura (1 minuto):**
    * Apresente-se.
    * Agradeça o interesse do candidato.
    * Explique o formato ("A nossa conversa vai durar cerca de 15 minutos. Vou fazer algumas perguntas sobre a sua carreira e, no final, teremos um tempo para as suas dúvidas.").

2.  **Desenvolvimento (4-5 perguntas):**
    * Faça UMA pergunta de cada vez.
    * Use perguntas abertas e comportamentais. Exemplos:
        * "Pode descrever-me um desafio técnico ou de equipa que enfrentou e como o superou?"
        * "Fale sobre uma situação em que precisou de aprender uma nova tecnologia rapidamente."
        * "Qual foi a sua maior contribuição no seu último trabalho?"
    * Após cada resposta, use frases curtas de reconhecimento, como "Entendido, obrigado por detalhar." ou "Interessante a sua abordagem.".

3.  **Encerramento (1 minuto):**
    * Abra espaço para perguntas do candidato ("Teria alguma pergunta para mim sobre a vaga?").
    * Agradeça novamente.
    * Informe os próximos passos de forma clara ("A nossa equipa de RH analisará a nossa conversa e entrará em contacto por e-mail dentro de uma semana. Muito obrigado pelo seu tempo.").
""",
)

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(level=LOG_LEVEL, format="%(asctime)s %(levelname)s %(name)s %(message)s")
logger = logging.getLogger("farol-backend")

app = FastAPI(title="Farol Realtime Backend", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"],
)
# Define o caminho para o diretório raiz do projeto (um nível acima da pasta 'backend')
BASE_DIR = Path(__file__).resolve().parent.parent

# Monta o diretório 'static' usando o caminho absoluto
app.mount(
    "/static",
    StaticFiles(directory=BASE_DIR / "static"),
    name="static"
)

# Aponta para o diretório de 'templates' usando o caminho absoluto
templates = Jinja2Templates(directory=BASE_DIR / "templates")

def get_api_key() -> str:
    if not OPENAI_API_KEY:
        raise HTTPException(status_code=500, detail={"error": "OPENAI_API_KEY não configurada"})
    return OPENAI_API_KEY

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/session")
async def create_session():
    logger.warning("O endpoint /session foi chamado, mas está obsoleto nesta configuração.")
    raise HTTPException(status_code=404, detail="Este endpoint não é usado na configuração de ligação direta.")

@app.get("/webrtc", response_class=HTMLResponse)
async def webrtc_page(request: Request):
    client_id = str(uuid.uuid4())
    api_key_for_template = get_api_key()
    return templates.TemplateResponse(
        "webrtc.html",
        {
            "request": request,
            "model": MODEL,
            "voice": VOICE,
            "silence_ms": SILENCE_MS,
            "client_id": client_id,
            "openai_api_key": api_key_for_template,
            "instructions": INSTRUCTIONS, # <-- ALTERAÇÃO: Passa as instruções para a interface
        },
    )

class LogEvent(BaseModel):
    client_id: str
    type: str
    message: Optional[str] = None
    data: Optional[dict] = None

@app.post("/logs")
async def collect_logs(event: LogEvent):
    logger.info("client.log %s", json.dumps(event.dict(), ensure_ascii=False))
    return {"ok": True}


