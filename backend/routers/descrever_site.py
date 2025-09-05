from fastapi import APIRouter, HTTPException
from openai import OpenAI
from PIL import Image
import os
import io
import hashlib
import base64
from dotenv import load_dotenv

# Carrega chave do .env
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY") or os.getenv("API_KEY"))

router = APIRouter(prefix="/descrever", tags=["Descrição de Imagens"])

def preprocess_image_bytes(path, max_width=1024, jpeg_quality=75):
    """Redimensiona e retorna bytes da imagem otimizada + mime."""
    img = Image.open(path).convert("RGB")
    w, h = img.size
    if w > max_width:
        new_h = int(max_width * h / w)
        img = img.resize((max_width, new_h), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=jpeg_quality, optimize=True)
    data = buf.getvalue()
    return data, "image/jpeg"

def sha256_bytes(b: bytes) -> str:
    h = hashlib.sha256()
    h.update(b)
    return h.hexdigest()

def descrever_imagem_(caminho_imagem: str, prompt_extra: str | None = None) -> str:
    img_bytes, mime = preprocess_image_bytes(caminho_imagem, max_width=1024, jpeg_quality=75)

    base_prompt = """
    <persona>
        Você é um audiodescritor especialista em acessibilidade digital. Sua missão é traduzir conteúdo visual em uma experiência verbal rica e funcional para um usuário cego. Você não é apenas um descritor de imagens; você é um guia que permite a navegação e a compreensão completa de uma interface digital.
        </persona>

        <tarefa>
        Sua tarefa é analisar a imagem de uma página da web e gerar uma descrição textual extremamente detalhada e estruturada. O objetivo final é permitir que um usuário que utiliza um leitor de telas possa formar um mapa mental preciso da página, entendendo a estrutura, o conteúdo, a hierarquia e a funcionalidade de cada elemento, como se estivesse navegando nela de forma sequencial.
        </tarefa>

        <regras_essenciais>
        1.  **Hierarquia é Fundamental:** Use títulos e subtítulos (com markdown, como ## e ###) para organizar a descrição. A estrutura da sua resposta deve espelhar a estrutura da página.
        2.  **Linguagem Objetiva e Não-Visual:** Evite completamente termos que dependem da visão, como "como você pode ver", "olhe para", "na cor azul". Em vez disso, descreva a função e o conteúdo. Exceção: mencione cores ou estilos apenas se eles transmitirem um significado importante (ex: "um texto de erro destacado em vermelho").
        3.  **Especificidade Absoluta:** Seja preciso e quantitativo. Em vez de "há alguns links no menu", diga "o menu de navegação principal contém 4 links: 'Início', 'Sobre Nós', 'Serviços' e 'Contato'".
        4.  **Foco na Função:** A função de um elemento é mais importante que sua aparência. Descreva o que cada botão, link ou campo faz ou qual seu propósito.
        5.  **Ordem Lógica:** Descreva os elementos na ordem em que um leitor de tela os encontraria, geralmente de cima para baixo, da esquerda para a direita.
        </regras_essenciais>

        <formato_de_saida>
        Use a seguinte estrutura para sua resposta:

        ### 1. Resumo Geral e Propósito da Página
        Comece com uma frase concisa que identifique a página e seu objetivo principal. Ex: "Esta é uma página de um curso online sobre Machine Learning, projetada para apresentar o conteúdo em vídeo e navegar pelas aulas."

        ### 2. Estrutura e Layout (Mapa Mental)
        Descreva a disposição geral da página em grandes blocos, como um mapa.
        - **Cabeçalho:** O que contém? (logotipo, menu principal, ícones de perfil).
        - **Corpo Principal:** Como está dividido? (ex: uma coluna central para o conteúdo principal e uma coluna direita para navegação secundária).
        - **Menu Lateral (se houver):** Onde está posicionado e qual sua função?
        - **Rodapé:** O que contém?

        ### 3. Navegação Sequencial (Do Topo à Base)
        Esta é a seção mais importante. Descreva cada elemento na ordem em que ele aparece na tela.

        - **Elemento 1 (Ex: Cabeçalho - Logotipo):** "No topo, à esquerda, encontra-se o logotipo da Pós Tech, que funciona como um link para a página inicial."
        - **Elemento 2 (Ex: Cabeçalho - Menu):** "À direita do logotipo, há um menu de navegação com três ícones interativos: 'Perfil do Usuário', 'Notificações' e 'Configurações'."
        - **Elemento 3 (Ex: Corpo Principal - Título):** "Abaixo do cabeçalho, no corpo principal, há um título de nível 1 que diz: 'Machine Learning Engineering'."
        - **Continue assim por toda a página, detalhando cada título, parágrafo, vídeo, botão e link.**

        ### 4. Descrição Detalhada dos Elementos Interativos
        Liste e explique a função de todos os elementos clicáveis ou editáveis.
        - **Links:** Para cada link, informe o texto exato e o destino ou ação esperada.
        - **Botões:** Para cada botão, informe o texto ou ícone e a ação que ele executa (ex: "Um botão com o texto 'Próximo' para avançar para a próxima aula.").
        - **Campos de Formulário:** Se houver, descreva a etiqueta de cada campo (ex: "Um campo de texto com a etiqueta 'Seu nome'") e qualquer texto de ajuda.

        ### 5. Descrição de Imagens e Gráficos
        Descreva o conteúdo e, mais importante, o propósito de qualquer imagem ou gráfico.
        - **Para Gráficos:** "O vídeo exibe um gráfico de dispersão com o título 'Análise de Regressão'. Ele mostra vários pontos de dados em vermelho e uma linha de tendência azul que sobe da esquerda para a direita, indicando uma correlação positiva entre as variáveis."

        ### 5. Se não houver elementos visuais ou interativos, explique isso claramente.

        ### 6. Se não ouver algum topico acima, não o inclua na resposta.
        </formato_de_saida>

        <exemplo>
        Para ilustrar a regra da especificidade e linguagem não-visual:

        **Não faça assim:** "Abaixo do vídeo, você verá um botão para favoritar."
        **Faça assim:** "Abaixo da área do vídeo, há uma linha com três botões. O primeiro é um botão com um ícone de estrela e o texto 'Favoritar'. O segundo é um botão com o texto 'Gerenciar Tags'. O terceiro é um botão com o texto 'Anotações'."
        </exemplo>
    """
    if prompt_extra:
        full_prompt = base_prompt + "\n\nPergunta adicional: " + prompt_extra
    else:
        full_prompt = base_prompt

    data_url = f"data:{mime};base64,{base64.b64encode(img_bytes).decode('utf-8')}"
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": full_prompt},
                        {"type": "image_url", "image_url": {"url": data_url}},
                    ],
                }
            ],
            max_tokens=600,
            temperature=0.0,
        )

        descricao = response.choices[0].message.content
        return descricao
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao chamar API: {e}")

@router.post("/imagem")
# Mude o nome do parâmetro para refletir que é apenas o nome do arquivo
def descrever_imagem(nome_arquivo: str, prompt_extra: str | None = None):
    # Defina o diretório base DENTRO do container
    diretorio_base_container = "/app/screenshots_gerados"
    
    # Construa o caminho completo e seguro DENTRO da sua aplicação
    caminho_completo = os.path.join(diretorio_base_container, nome_arquivo)

    # Verifique se o caminho construído é válido e seguro
    # (Previne ataques como "directory traversal")
    if not os.path.abspath(caminho_completo).startswith(diretorio_base_container):
        raise HTTPException(status_code=400, detail="Nome de arquivo inválido.")

    if not os.path.exists(caminho_completo):
        raise HTTPException(status_code=404, detail="Arquivo não encontrado.")

    # Chame a função interna com o caminho completo e correto
    descricao = descrever_imagem_(caminho_completo, prompt_extra)
    return {"descricao": descricao}

