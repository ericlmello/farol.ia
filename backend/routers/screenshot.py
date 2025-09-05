# app/routers/screenshot.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, HttpUrl
# --- 1. Importe a versão assíncrona ---
from playwright.async_api import async_playwright
from pathlib import Path
import uuid
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/screenshot", tags=["Screenshot"])

SCREENSHOT_DIR = Path("screenshots_gerados")
SCREENSHOT_DIR.mkdir(exist_ok=True)

class ScreenshotRequest(BaseModel):
    url: HttpUrl

# A função já era 'async', agora o conteúdo dela também será.
async def take_screenshot_async(url: str) -> str:
    """Função assíncrona usando a API Async do Playwright."""
    logger.info(f"Iniciando Playwright async para {url} ...")
    try:
        # --- 2. Use 'async with' e 'async_playwright' ---
        async with async_playwright() as p:
            logger.info("Playwright async iniciado com sucesso.")
            # --- 3. Use 'await' para cada operação I/O (rede, processo, etc) ---
            browser = await p.chromium.launch(headless=True)
            logger.info("Navegador Chromium iniciado em modo headless.")
            page = await browser.new_page()
            logger.info(f"Navegando para {url} ...")
            await page.goto(url, wait_until="networkidle", timeout=60000)
            
            file_name = f"{uuid.uuid4()}.png"
            file_path = SCREENSHOT_DIR / file_name
            
            logger.info(f"Tirando screenshot e salvando em {file_path} ...")
            await page.screenshot(path=str(file_path), full_page=True)
            await browser.close()
            logger.info("Navegador fechado com sucesso.")
            return str(file_name)
    except Exception as e:
        logger.exception("Erro no take_screenshot_async")
        # O traceback original do Playwright é mais útil aqui
        raise HTTPException(status_code=500, detail=f"Erro ao tirar screenshot: {str(e)}")

# Este endpoint é síncrono e não é usado pelo agente, mas vamos deixar como está
@router.post("/tirar-print")
async def tirar_print(request: ScreenshotRequest):
    logger.info(f"Recebida requisição para tirar print da URL: {request.url}")
    try:
        # Agora este endpoint também precisa ser async para poder usar 'await'
        file_path = await take_screenshot_async(str(request.url))
        logger.info(f"Screenshot salvo com sucesso em {file_path}.")
        return {"status": "sucesso", "caminho_do_arquivo": file_path}
    except HTTPException as http_exc:
        logger.error(f"Erro HTTP ao tirar print: {http_exc.detail}")
        raise http_exc
    except Exception as e:
        logger.error(f"Erro inesperado ao tirar print: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Erro inesperado: {str(e)}")