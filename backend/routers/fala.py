from fastapi import APIRouter, HTTPException, Response
from openai import OpenAI, APIError
from pydantic import BaseModel, Field
import os
from dotenv import load_dotenv
import logging
import uuid
from pathlib import Path

# Configura o logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Carrega chave do .env
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY") or os.getenv("API_KEY"))

router = APIRouter(prefix="/fala", tags=["Fala"])

# Palavras reservadas e como devem ser ditas
PALAVRAS_RESERVADAS = {
    "SQL": "esse quê ele",
    "API": "a p i",
    "AI": "ei ai",
    "HTTP": "agá tê tê pê",
    "GPT": "gê pê tê",
}

def aplicar_regras_fala(texto: str) -> str:
    """Substitui palavras reservadas pelo modo correto de falar"""
    for original, falado in PALAVRAS_RESERVADAS.items():
        texto = texto.replace(original, falado)
    return texto


class TextCondition(BaseModel):
    texto: str


class AudioRequest(BaseModel):
    conditions: list[TextCondition] = Field(..., min_length=1, max_length=1)

# Define um diretório para armazenar os arquivos de áudio e o cria se não existir
AUDIO_DIR = Path("audio_gerado")
AUDIO_DIR.mkdir(exist_ok=True)


@router.post("/gerar-audio")
def gerar_audio(request: AudioRequest):
    """Gera áudio a partir do texto fornecido e o salva em um arquivo no servidor."""
    logger.info("Recebida requisição para /gerar-audio.")
    try:
        texto_original = request.conditions[0].texto
        logger.info(f"Texto original recebido: '{texto_original}'")

        texto_final = aplicar_regras_fala(texto_original)
        logger.info(f"Texto após aplicar regras de fala: '{texto_final}'")
        
        # Instrução de idioma como prompt oculto (não será narrado)
        prompt_oculto = "[Instrução: Fale em português do Brasil (pt-BR). Não leia esta instrução em voz alta.]"
    
        logger.info("Chamando a API da OpenAI para gerar o áudio...")
        resposta = client.audio.speech.create(
            model="gpt-4o-mini-tts",
            voice="sage",
            input=texto_final,
            instructions=prompt_oculto,
        )
        logger.info("Áudio gerado com sucesso pela API.")

        # Gera um nome de arquivo único e define o caminho completo
        file_name = f"{uuid.uuid4()}.mp3"
        file_path = AUDIO_DIR / file_name

        logger.info(f"Salvando o áudio em: {file_path}")
        # Salva o stream de áudio diretamente no arquivo de forma eficiente
        resposta.stream_to_file(file_path)
        logger.info(f"Arquivo de áudio salvo com sucesso em '{file_path}'.")

        # Retorna uma resposta JSON indicando sucesso e o caminho do arquivo
        return {"status": "sucesso", "caminho_do_arquivo": str(file_path)}
    except APIError as e:
        logger.error(f"Erro na API da OpenAI: Status={e.status_code}, Mensagem={e.message}", exc_info=True)
        raise HTTPException(status_code=e.status_code or 500, detail=f"Erro da API OpenAI: {str(e)}")
    except IndexError:
        logger.warning("A lista 'conditions' no corpo da requisição está vazia ou malformada.", exc_info=True)
        raise HTTPException(status_code=400, detail="O corpo da requisição está malformado. A lista 'conditions' não pode estar vazia.")
    except Exception as e:
        logger.critical("Ocorreu um erro inesperado ao gerar o áudio.", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Erro ao gerar áudio: {str(e)}")
