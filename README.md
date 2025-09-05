# Farol Realtime (voz-para-voz com OpenAI Realtime)

Projeto com dois serviços Docker (backend FastAPI + frontend Streamlit) para conversa em voz em tempo real usando a OpenAI Realtime API, modelo `gpt-realtime-2025-08-28`. Nenhum botão “Iniciar”: a página pede o microfone no carregamento e escuta continuamente. A resposta falada do modelo toca imediatamente no navegador.

## Estrutura

```
farol-realtime/
  backend/
    app.py
    requirements.txt
    Dockerfile
    templates/
      webrtc.html
    static/
      webrtc.css
      webrtc.js
  frontend_streamlit/
    streamlit_app.py
    requirements.txt
    Dockerfile
  docker-compose.yml
  .env.example
  README.md
```

## Backend (FastAPI)

- Endpoints:
  - `GET /health` → `{ "status": "ok" }`
  - `POST /session` → Cria sessão efêmera Realtime na OpenAI e retorna o JSON (inclui `client_secret.value`).
  - `GET /webrtc` → Página com UI de alto contraste que pede o microfone, negocia WebRTC e toca o áudio remoto.
- Lê a chave preferencialmente do secret Swarm em `/run/secrets/openai_api_key`; fallback para env `OPENAI_API_KEY`.
- Configuração por env: `MODEL` (padrão `gpt-realtime-2025-08-28`), `VOICE` (padrão `marin`), `SILENCE_MS` (padrão `600`) e `INSTRUCTIONS` (persona Farol).

## Frontend (Streamlit)

- Tema escuro, alto contraste e fontes legíveis.
- Nenhum botão “Iniciar”: ao abrir, a página embeda a rota `/webrtc` do backend em um `<iframe>` com `allow="microphone; autoplay"` para que o navegador permita microfone e áudio remoto.
- Mostra um cabeçalho e texto explicativo; a UI dinâmica (status/áudio) está na página do backend embutida.

## Docker Compose (local)

1. Na pasta `farol-realtime/`, crie um arquivo `openai_api_key.txt` contendo apenas sua chave `sk-...` (sem quebra de linha extra) ou defina `OPENAI_API_KEY` no ambiente para fallback local.
2. Opcional: copie `.env.example` para `.env` e ajuste variáveis.
3. Suba os serviços:

   ```bash
   docker compose up --build
   ```

4. Abra: http://localhost:8501 (o backend estará em http://localhost:${BACKEND_HOST_PORT:-8011})

Se a porta estiver ocupada, ajuste `BACKEND_HOST_PORT` no `.env` para um valor livre (ex.: 8015) e o compose já repassa para o iframe (`BACKEND_PUBLIC_URL`).

## Swarm/Swarmpit (produção/demo)

### Criar secret para a OpenAI API Key

- Via CLI:

  ```bash
  echo -n "sk-..." | docker secret create openai_api_key -
  ```

- Via Swarmpit UI: Secrets → Create → Name: `openai_api_key` → Conteúdo: sua chave `sk-...`.

### Descrever serviços (exemplo usando `docker service create`)

```bash
# Backend (monta secret em /run/secrets/openai_api_key)
docker service create \
  --name farol-backend \
  --secret source=openai_api_key,target=/run/secrets/openai_api_key,mode=0440 \
  -p 8000:8000 \
  -e MODEL=gpt-realtime-2025-08-28 \
  -e VOICE=marin \
  -e SILENCE_MS=600 \
  farol-backend

# Frontend
docker service create \
  --name farol-frontend \
  -p 8501:8501 \
  -e BACKEND_PUBLIC_URL=http://farol-backend:8000 \
  farol-frontend
```

No Swarmpit você pode criar ambos os serviços no UI, adicionando o secret ao backend e definindo o env `BACKEND_PUBLIC_URL` no frontend.

## Healthcheck

- Backend expõe `GET /health`. O Dockerfile já define `HEALTHCHECK` usando `curl`.

## Observações de autoplay e áudio

- Navegadores podem bloquear autoplay de áudio não silenciado. A página `/webrtc` tenta reproduzir automaticamente e, se bloqueado, solicitará uma interação mínima (clique/tecla) para liberar o áudio — sem botão “Iniciar”. O microfone é solicitado automaticamente no carregamento.

## Segurança

- O frontend nunca vê sua `OPENAI_API_KEY`. Ele usa apenas o `client_secret.value` efêmero retornado pelo backend (`/session`).

## Variáveis de ambiente

- Backend:
  - `OPENAI_API_KEY` (apenas local; em produção use o secret `openai_api_key` em `/run/secrets/openai_api_key`)
  - `MODEL` (padrão `gpt-realtime-2025-08-28`)
  - `VOICE` (padrão `marin`)
  - `SILENCE_MS` (padrão `600`)

- Frontend:
  - `BACKEND_PUBLIC_URL` (ex.: `http://backend:8000` no Swarm; `http://localhost:8000` local)

## Testes manuais (critérios de aceite)

- Sem botão: ao abrir o Streamlit, o navegador pede permissão do microfone; após conceder, o app escuta continuamente.
- Realtime: fale e ouça a resposta do modelo em voz com baixa latência; o áudio remoto toca automaticamente (ou após uma interação mínima caso o navegador bloqueie autoplay).
- Acessível: UI de alto contraste e status textual claro na página embutida.
- Segurança: o frontend nunca recebe a `OPENAI_API_KEY`.
- Containers: dois serviços independentes nas portas `8000` (backend) e `8501` (frontend).
- Healthcheck do backend respondendo `ok`.
