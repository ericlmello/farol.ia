# streamlit_app.py
import os
from contextlib import suppress
import streamlit as st

# ========= CONFIG =========
BACKEND_PUBLIC_URL = os.getenv("BACKEND_PUBLIC_URL", "http://localhost:8011")
st.set_page_config(
    page_title="FAROL.IA",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ========= THEME / CSS =========
st.markdown(
    """
    <style>
      :root{
        --bg:#add8e6;   /* Azul claro */
        --bg-2:#bde0f0; /* Azul claro um pouco diferente */
        --card:#ffffff; 
        --card-2:#f0f8ff;
        --muted:#334155; 
        --txt:#0f172a;  /* Texto escuro para contraste */
        --edge:#1c2435;
        --accent:#7c3aed; 
        --accent-2:#6d28d9;
        --success: #28a745;
      }
      html,body,[data-testid="stAppViewContainer"]{ background:var(--bg)!important; color:var(--txt)!important; }
      [data-testid="stHeader"]{ background:transparent; }
      .card{ background:linear-gradient(180deg,var(--card),var(--card-2));
          border:1px solid var(--edge); border-radius:16px; padding:16px 18px; box-shadow:0 6px 18px rgba(0,0,0,.28);}
      .title-lg{ font-weight:800; font-size:1.3rem; }
      .kpis{ display:grid; gap:12px; grid-template-columns: repeat(4, minmax(0,1fr)); }
      .kpi{ background:#0f1626; border:1px solid var(--edge); border-radius:14px; padding:14px; }
      .kpi .v{ font-size:1.6rem; font-weight:800; }
      .divider{ height:1px; background:linear-gradient(90deg, transparent, #22304a, transparent); margin:10px 0 16px; }
      .page-title{ font-size:1.4rem; font-weight:800; margin:0 0 6px 0; }

      .stProgress > div > div > div > div { background-color: var(--success); }

      .skill-tag {
        display: inline-block;
        background-color: #1f2a41;
        color: #cbd5e1;
        padding: 4px 10px;
        border-radius: 15px;
        font-size: 0.8rem;
        font-weight: 500;
        margin-right: 6px;
        margin-bottom: 6px;
      }

      section[data-testid="stSidebar"] { background:#0a1220; border-right:1px solid #111827; }
      .sb-header{ padding:10px 6px 6px 6px; }
      .sb-badge{
        display:inline-flex; align-items:center; gap:8px; padding:8px 12px; border-radius:999px;
        border:1px solid #21314d; background:#0e1523; color:#cbd5e1; font-weight:700;
      }

      section[data-testid="stSidebar"] .nav-btn > button {
        width:100%;
        text-align:left;
        padding:14px 14px;
        margin:8px 0;
        border-radius:14px;
        border:1px solid #1f2a41;
        background:#0c1526;
        color:#e5e7eb;
        font-weight:700;
      }
      section[data-testid="stSidebar"] .nav-btn > button:hover {
        background:#0f1b34; border-color:#2f3e60;
      }
      section[data-testid="stSidebar"] .nav-btn.active > button {
        background:linear-gradient(180deg,#1b2438,#0f1b2f);
        border-color:#334155; box-shadow:0 0 0 2px #334155 inset;
      }

      section[data-testid="stSidebar"] .action-btn > button{
        width:100%; padding:14px 12px; border-radius:12px; font-weight:700;
        background:#1b2438; border:1px solid #334155; color:#e5e7eb;
      }
      section[data-testid="stSidebar"] .action-btn > button:hover{
        background:#222d47; border-color:#3b4d6e;
      }
    </style>
    """,
    unsafe_allow_html=True,
)

# ========= PÁGINAS =========
PAGES = [
    ("Boas-vindas", "👋"),
    ("Cadastro por Voz", "📝"),
    ("Home", "🏠"),
    ("Vagas", "💼"),
    ("Hub de Desenvolvimento", "🧩"),
    ("Análise de Matches", "🎯"),
    ("Entrevista (Realtime)", "🎙️"),
    ("Simulação em Andamento", "🟢"),
    ("Feedback", "📊"),
]

if "page" not in st.session_state:
    st.session_state.page = PAGES[0][0]

# ========= CARD =========
def card(title, body_md, page_dest=None, footer=None):
    """
    Cria um card (clicável se page_dest for passado).
    """
    if page_dest:
        if st.button(f"{title}", key=f"cardbtn_{title}", use_container_width=True):
            st.session_state.page = page_dest
            st.rerun()

    st.markdown(f'<div class="card"><div class="title-lg">{title}</div>', unsafe_allow_html=True)
    st.markdown(body_md, unsafe_allow_html=True)
    if footer:
        st.markdown(footer, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ========= PÁGINAS =========
def page_boas_vindas():
    st.markdown('<div class="page-title">Bem-vindo ao <b>Farol - Conectando Talentos. Removendo Barreiras</b></div>', unsafe_allow_html=True)
    st.caption("Navegação por voz, descrição de tela e preparação para entrevistas — tudo em um só lugar.")

    c1, c2, c3 = st.columns(3)
    with c1:
        card("Cadastro guiado", "Preencha seu perfil **falando**.", page_dest="Cadastro por Voz")
    with c2:
        card("Assistente de carreira", "Recomenda **vagas** e **cursos**.", page_dest="Vagas")
    with c3:
        card("Simulador de entrevista", "Converse em **tempo real** e receba **feedback**.", page_dest="Entrevista (Realtime)")

def page_cadastro():
    st.markdown('<div class="page-title">Cadastro guiado por voz</div>', unsafe_allow_html=True)
    with st.form("cadastro_voz"):
        st.text_input("Seu nome", key="cad_nome")
        st.text_input("Objetivo/cargo desejado", placeholder="Ex.: Desenvolvedor(a) Front-end Acessível", key="cad_cargo")
        st.text_input("Preferência de local/remote/híbrido", key="cad_loc")
        st.multiselect("Necessidades de acessibilidade", ["Leitor de tela","Alto contraste","Navegação por voz","Subtítulos automáticos"], key="cad_acess")
        st.text_area("Resumo da experiência", height=120, key="cad_exp")
        if st.form_submit_button("Salvar e continuar →"):
            st.success("Cadastro salvo!")

def page_home():
    st.markdown('<div class="page-title">Seu painel</div>', unsafe_allow_html=True)
    st.caption("Resumo do seu progresso e recomendações.")
    st.markdown('<div class="kpis">', unsafe_allow_html=True)
    for label, val, hint in [
        ("Progresso no Hub", "42%", "Módulos finalizados"),
        ("Entrevistas concluídas", "3", "Última há 2 dias"),
        ("Vagas alinhadas", "12", "filtradas para seu perfil"),
        ("Feedback médio", "8.5", "de 0 a 10"),
    ]:
        st.markdown(f'<div class="kpi"><div style="color:#9fb3c8">{label}</div><div class="v">{val}</div><div style="color:#9fb3c8">{hint}</div></div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

def page_vagas():
    st.markdown('<div class="page-title">Busca de Vagas</div>', unsafe_allow_html=True)
    colf = st.columns(4)
    with colf[0]: st.selectbox("Área", ["Desenvolvimento","QA","Design","Dados"])
    with colf[1]: st.selectbox("Nível", ["Júnior","Pleno","Sênior"])
    with colf[2]: st.selectbox("Modelo", ["Remoto","Híbrido","Presencial"])
    with colf[3]: st.multiselect("Acessibilidade", ["Leitor de tela","Alto contraste","Navegação por voz"])
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    cols = st.columns(3)
    for i in range(6):
        with cols[i%3]:
            card(
                f"Vaga #{i+1} — Dev Acessível",
                "Empresa X · Remoto · **Pleno**\n\nRequisitos: WAI-ARIA, acessibilidade web, testes automatizados.",
                '<a href="#" style="text-decoration:none" class="btn">Candidatar-se</a>'
            )

def page_hub():
    st.markdown('<div class="page-title">Hub de Desenvolvimento</div>', unsafe_allow_html=True)
    st.caption("Trilhas, cursos e desafios práticos.")
    
    # ====== Cursos principais ======
    cols = st.columns(4)
    items = [
        ("Trilha ARIA Essentials", "Domine papéis, estados e propriedades."),
        ("Acessibilidade em React", "Padrões, focos e atalhos."),
        ("Testes automatizados", "axe-core + Playwright."),
        ("Navegação por voz", "Comandos e SR."),
        ("Escrita inclusiva", "Tom, legibilidade e UX writing."),
        ("WAI e WCAG 2.2", "Critérios e checklists."),
        ("Leitor de tela", "NVDA/JAWS — boas práticas."),
        ("Portfólio acessível", "Componentes e exemplos."),
    ]
    for i,(t,d) in enumerate(items):
        with cols[i%4]:
            card(t, d, '<a class="btn" href="#">Iniciar</a>')
    
    # ====== NOVA SEÇÃO ======
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="page-title">📚 Cursos Recomendados</div>', unsafe_allow_html=True)
    st.caption("Sugestões extras para aprofundar seus conhecimentos.")

    cols_rec = st.columns(3)
    rec_items = [
        ("Introdução ao HTML5 Semântico", "Aprenda a estruturar páginas com acessibilidade desde o início."),
        ("Design Inclusivo", "Princípios de UX focados em diversidade e inclusão."),
        ("Python para Análise de Dados", "Manipulação de dados acessível e análise exploratória."),
        ("Comunicação Efetiva", "Melhore suas soft skills e apresentações."),
        ("Introdução ao Machine Learning", "Fundamentos e primeiros passos em ML."),
        ("Git e Versionamento", "Controle de versões e colaboração em projetos."),
    ]
    for i,(t,d) in enumerate(rec_items):
        with cols_rec[i%3]:
            card(t, d, '<a class="btn" href="#">Ver mais</a>')


def page_matches():
    st.markdown('<div class="page-title">Análise de Matches</div>', unsafe_allow_html=True)
    st.caption("Análise de compatibilidade simulada entre vagas e candidatos.")
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        card(
            "Desenvolvedor Java Sênior (PJe)",
            """
            **Candidato:** Mariana Silva
            
            **Compatibilidade: 92%**
            """
        )
        st.progress(92)
        st.markdown(
            """
            <div style="margin-top: -10px;">
                <span class="skill-tag">Java</span>
                <span class="skill-tag">SQL</span>
                <span class="skill-tag">Banco de Dados PJe</span>
                <span class="skill-tag">Comunicação</span>
            </div>
            """,
            unsafe_allow_html=True
        )

    with c2:
        card(
            "Frontend Developer Pleno (Angular)",
            """
            **Candidato:** Rafael Costa
            
            **Compatibilidade: 85%**
            """
        )
        st.progress(85)
        st.markdown(
            """
            <div style="margin-top: -10px;">
                <span class="skill-tag">Angular</span>
                <span class="skill-tag">TypeScript</span>
                <span class="skill-tag">CSS</span>
                <span class="skill-tag">Trabalho em Equipe</span>
            </div>
            """,
            unsafe_allow_html=True
        )

def page_entrevista():
    st.markdown('<div class="page-title">Simulador de Entrevistas (voz em tempo real)</div>', unsafe_allow_html=True)
    st.caption("Ao carregar, o navegador pode pedir permissão de microfone. As respostas tocam automaticamente.")
    st.components.v1.html(
    f"""
    <iframe
      src="{BACKEND_PUBLIC_URL}/webrtc"
      title="Farol Realtime"
      width="100%"
      height="380"
      style="border-radius:16px;border:1px solid rgba(255,255,255,.1);"
      allow="microphone; autoplay; clipboard-read; clipboard-write"
    ></iframe>
    """,
    height=420,
)
    st.info("Se o áudio não tocar, clique na página para liberar o autoplay do navegador.")

def page_simulacao():
    st.markdown('<div class="page-title">Simulação em andamento</div>', unsafe_allow_html=True)
    st.caption("Acompanhe suas falas e as respostas do agente enquanto a entrevista ocorre.")

def page_feedback():
    st.markdown('<div class="page-title">Feedback da Simulação</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        card("Pontos fortes", "- Comunicação clara\n- Conceitos ARIA corretos\n- Boa senioridade em testes")
    with c2:
        card("Oportunidades de melhoria", "- Estruturar STAR\n- Detalhar métricas de impacto\n- Falar de trade-offs")

# ========= SIDEBAR / NAV =========
def sidebar_nav():
    st.markdown('<div class="sb-header"><span class="sb-badge">  🧭 FAROL.IA</span></div>', unsafe_allow_html=True)

    use_option_menu = False
    with suppress(Exception):
        from streamlit_option_menu import option_menu
        use_option_menu = True

    if use_option_menu:
        icons = ["hand-thumbs-up","pencil-square","house","briefcase","puzzle","bullseye","mic","record-circle","bar-chart"]
        current = option_menu(
            menu_title=None,
            options=[n for n,_ in PAGES],
            icons=icons,
            default_index=[n for n,_ in PAGES].index(st.session_state.page),
            orientation="vertical",
            styles={
                "container": {"padding": "8px 0 8px 0"},
                "nav-link": {
                    "font-weight": "700",
                    "padding": "16px 16px",
                    "border-radius": "14px",
                    "margin": "8px 0",
                    "background-color": "#0c1526",
                    "border": "1px solid #1f2a41",
                    "color": "#e5e7eb",
                },
                "nav-link-hover": {"background-color": "#0f1b34", "border-color": "#2f3e60"},
                "nav-link-selected": {
                    "background": "linear-gradient(180deg,#1b2438,#0f1b2f)",
                    "border-color": "#334155",
                    "box-shadow": "0 0 0 2px #334155 inset",
                },
                "icon": {"color": "#cbd5e1"},
            },
        )
        if current != st.session_state.page:
            st.session_state.page = current
            st.rerun()
    else:
        for name, icon in PAGES:
            active_cls = " active" if st.session_state.page == name else ""
            st.markdown(f'<div class="nav-btn{active_cls}">', unsafe_allow_html=True)
            if st.button(f"{icon}  {name}", key=f"navbtn_{name}", use_container_width=True):
                st.session_state.page = name
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

    st.divider()
    st.markdown('<div class="action-btn">', unsafe_allow_html=True)
    if st.button("Ir para Entrevista 🎙️", use_container_width=True):
        st.session_state.page = "Entrevista (Realtime)"
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    st.caption("Dica: o simulador pedirá acesso ao microfone.")

with st.sidebar:
    sidebar_nav()

# ========= ROTEAMENTO =========
page = st.session_state.page
if page == "Boas-vindas":
    page_boas_vindas()
elif page == "Cadastro por Voz":
    page_cadastro()
elif page == "Home":
    page_home()
elif page == "Vagas":
    page_vagas()
elif page == "Hub de Desenvolvimento":
    page_hub()
elif page == "Análise de Matches":
    page_matches()
elif page == "Entrevista (Realtime)":
    page_entrevista()
elif page == "Simulação em Andamento":
    page_simulacao()
elif page == "Feedback":
    page_feedback()



