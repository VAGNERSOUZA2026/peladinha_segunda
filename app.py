import streamlit as st
import pandas as pd
import json
import os
import random
from datetime import datetime, timedelta, timezone

# -----------------------------------------------------------------------------
# CONFIGURAÇÃO DE FUSO HORÁRIO E DATAS
# -----------------------------------------------------------------------------
fuso_br = timezone(timedelta(hours=-3))
hoje_dt = datetime.now(fuso_br)
hoje_str = hoje_dt.strftime("%d/%m")
mes_vigente_str = hoje_dt.strftime("%m/%Y")
data_hoje_id = hoje_dt.strftime("%Y-%m-%d")

# -----------------------------------------------------------------------------
# CONFIGURAÇÃO DA PÁGINA (TEMA ESCURO)
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Peladinha FC | Gestão Inteligente",
    page_icon="⚽",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# -----------------------------------------------------------------------------
# ESTILIZAÇÃO CSS CUSTOMIZADA (BOTÕES LEGÍVEIS)
# -----------------------------------------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] { 
        font-family: 'Montserrat', sans-serif; 
    }

    .stApp {
        background-color: #111827;
        color: #F3F4F6;
    }

    .app-header {
        background: #1F2937;
        padding: 20px;
        border-radius: 16px;
        margin-bottom: 20px;
        border: 1px solid #374151;
        box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.3);
    }
    .app-title {
        font-size: 1.6rem;
        font-weight: 700;
        color: #FFFFFF;
        margin: 0;
    }
    .app-subtitle {
        font-size: 0.85rem;
        color: #9CA3AF;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    .dashboard-card {
        background-color: #1F2937;
        border: 1px solid #374151;
        border-radius: 16px;
        padding: 20px;
        height: 100%;
        color: #FFFFFF;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.2);
        transition: all 0.2s ease-in-out;
        margin-bottom: 15px;
    }
    .dashboard-card:hover {
        border-color: #0D9488;
        transform: translateY(-3px);
        box-shadow: 0px 6px 15px rgba(13, 148, 136, 0.2);
    }
    .dashboard-card h3 {
        font-size: 1.15rem;
        font-weight: 700;
        color: #FFFFFF;
        margin-top: 8px;
        margin-bottom: 6px;
    }
    .dashboard-card p {
        font-size: 0.82rem;
        color: #9CA3AF;
        margin: 0;
        line-height: 1.4;
    }
    .card-icon {
        font-size: 1.6rem;
        margin-bottom: 5px;
    }

    .card-notice {
        background: #1F2937;
        border-left: 5px solid #0D9488;
        padding: 16px;
        border-radius: 12px;
        margin-bottom: 20px;
        color: #E5E7EB;
        border-top: 1px solid #374151;
        border-right: 1px solid #374151;
        border-bottom: 1px solid #374151;
    }

    .card-team {
        background: #1F2937;
        border: 1px solid #374151;
        border-top: 4px solid #0D9488;
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 15px;
    }

    /* CORREÇÃO DE LEGIBILIDADE DOS BOTÕES NO MODO ESCURO */
    div.stButton > button:first-child {
        background-color: #0D9488 !important; /* Fundo Verde */
        color: #FFFFFF !important; /* Texto Branco */
        font-weight: 700 !important;
        border-radius: 10px !important;
        border: 1px solid #14B8A6 !important;
        padding: 10px 20px !important;
        box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.2);
    }
    div.stButton > button:first-child:hover {
        background-color: #0F766E !important;
        border-color: #2DD4BF !important;
    }
    /* Botão de cancelar com contraste */
    div.stButton > button:last-child {
         background-color: #4B5563 !important;
         color: #FFFFFF !important;
    }
    div.stButton > button:last-child:hover {
         background-color: #6B7280 !important;
    }

    .stTextInput input, .stSelectbox select, .stNumberInput input {
        background-color: #374151 !important;
        color: #FFFFFF !important;
        border: 1px solid #4B5563 !important;
        border-radius: 8px !important;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# TRATAMENTO DE DADOS (ARQUIVOS JSON)
# -----------------------------------------------------------------------------
DATA_FILE = "jogadoras.json"
PRESENCAS_FILE = "presencas.json"
AVISOS_FILE = "avisos.json"
FINANCE_FILE = "financeiro.json"
ADMINS_FILE = "administradores.json"
REGULAMENTO_FILE = "regulamento.json"
SORTEIO_FILE = "sorteio.json"
COMPROVANTES_FILE = "comprovantes.json"
UPLOAD_DIR = "comprovantes_imgs"

if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

def carregar_dados(filename, default):
    if os.path.exists(filename):
        try:
            with open(filename, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return default
    return default

def salvar_dados(filename, data):
    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    except Exception:
        pass

def obter_nome_p(p):
    return p["nome"] if isinstance(p, dict) else p

def obter_hora_p(p):
    return p.get("hora", "") if isinstance(p, dict) else ""

def obter_tipo_p(p):
    return p.get("tipo", "Avulso") if isinstance(p, dict) else "Avulso"

# Carregar estado da sessão
if "jogadoras" not in st.session_state:
    st.session_state.jogadoras = carregar_dados(DATA_FILE, [])
if "presencas" not in st.session_state:
    st.session_state.presencas = carregar_dados(PRESENCAS_FILE, [])
if "financeiro" not in st.session_state:
    st.session_state.financeiro = carregar_dados(FINANCE_FILE, [])
if "comprovantes" not in st.session_state:
    st.session_state.comprovantes = carregar_dados(COMPROVANTES_FILE, [])
if "administradores" not in st.session_state:
    def_admins = [{"nome": "Admin Principal", "login": "admin", "senha": "1980", "principal": True}]
    st.session_state.administradores = carregar_dados(ADMINS_FILE, def_admins)
if "avisos" not in st.session_state:
    st.session_state.avisos = carregar_dados(AVISOS_FILE, {
        "vencimento": "Todo dia 10 de cada mês",
        "recado": "Favor chegarem 10 minutos antes para organizar o jogo!",
        "pix": "peladinhafc@email.com",
        "limite_vagas": 15
    })
if "regulamento" not in st.session_state:
    st.session_state.regulamento = carregar_dados(REGULAMENTO_FILE, [
        {"topico": "📌 1. Prioridade", "regrinha": "Mensalistas confirmando até as 17:00 de segunda têm prioridade."},
        {"topico": "⏳ 2. Fila de Espera", "regrinha": "Jogadoras avulsas entram na fila de espera por ordem de chegada."},
    ])
if "sorteio_oficial" not in st.session_state:
    st.session_state.sorteio_oficial = carregar_dados(SORTEIO_FILE, {})

if "usuario_logado" not in st.session_state:
    st.session_state.usuario_logado = None
if "admin_logged" not in st.session_state:
    st.session_state.admin_logged = False
if "admin_nome" not in st.session_state:
    st.session_state.admin_nome = ""
if "msg_cadastro_sucesso" not in st.session_state:
    st.session_state.msg_cadastro_sucesso = False
if "pagina_ativa" not in st.session_state:
    st.session_state.pagina_ativa = "📌 Presença no Jogo"

# -----------------------------------------------------------------------------
# BARRA LATERAL (LOGIN E CADASTRO)
# -----------------------------------------------------------------------------
with st.sidebar:
    st.title("⚙️ Acesso & Contas")
    
    if st.session_state.usuario_logado:
        st.success(f"Jogadora: **{st.session_state.usuario_logado}**")
        if st.button("🚪 Sair da Conta", use_container_width=True):
            st.session_state.usuario_logado = None
            st.rerun()
    else:
        st.subheader("🔑 Entrar na Jogadora")
        if st.session_state.msg_cadastro_sucesso:
            st.success("Cadastro realizado! Faça login abaixo.")
            st.session_state.msg_cadastro_sucesso = False
            
        with st.form("form_login_player"):
            l_user = st.text_input("Login")
            l_pass = st.text_input("Senha", type="password")
            if st.form_submit_button("Entrar", use_container_width=True):
                user_found = next((j for j in st.session_state.jogadoras if j.get("login") == l_user and j.get("senha") == l_pass), None)
                if user_found:
                    st.session_state.usuario_logado = user_found["nome"]
                    st.rerun()
                else:
                    st.error("Login ou senha incorretos!")

        st.markdown("---")
        st.subheader("📝 Cadastrar Nova Jogadora")
        with st.form("form_cad_player", clear_on_submit=True):
            c_nome = st.text_input("Seu Nome *")
            c_nasc = st.text_input("Nascimento (DD/MM) *", placeholder="Ex: 15/05")
            c_tipo = st.selectbox("Tipo:", ["Avulso", "Mensalista"])
            c_user = st.text_input("Login *")
            c_pass = st.text_input("Senha *", type="password")
            if st.form_submit_button("Criar Conta", use_container_width=True):
                if c_nome and c_user and c_pass:
                    if any(j.get("login") == c_user.strip() for j in st.session_state.jogadoras):
                        st.error("Este Login já está em uso. Escolha outro!")
                    else:
                        st.session_state.jogadoras.append({
                            "nome": c_nome.strip(), "nascimento": c_nasc.strip(),
                            "login": c_user.strip(), "senha": c_pass.strip(),
                            "tipo": c_tipo, "status": "Ativo"
                        })
                        salvar_dados(DATA_FILE, st.session_state.jogadoras)
                        st.session_state.msg_cadastro_sucesso = True
                        st.rerun()
                else:
                    st.error("Preencha Nome, Login e Senha!")

    st.markdown("---")
    st.subheader("🔒 Área do Administrador")
    if not st.session_state.admin_logged:
        with st.form("form_login_admin"):
            adm_user = st.text_input("Login Admin")
            adm_pass = st.text_input("Senha Admin", type="password")
            if st.form_submit_button("Acessar Admin", use_container_width=True):
                admin_encontrado = next((adm for adm in st.session_state.administradores if adm.get("login") == adm_user and adm.get("senha") == adm_pass), None)
                if admin_encontrado:
                    st.session_state.admin_logged = True
                    st.session_state.admin_nome = admin_encontrado["nome"]
                    st.rerun()
                else:
                    st.error("Credenciais de Admin incorretas!")
    else:
        st.info(f"Logado como Admin: **{st.session_state.admin_nome}**")
        if st.button("Sair do Admin", use_container_width=True):
            st.session_state.admin_logged = False
            st.session_state.admin_nome = ""
            st.rerun()

# -----------------------------------------------------------------------------
# PÁGINA DE PRESENÇA (A Lógica do Sistema)
# -----------------------------------------------------------------------------
st.markdown("""
<div class='app-header'>
    <div class='app-title'>⚽ PELADINHA FC</div>
    <div class='app-subtitle'>Gestão Inteligente & Sorteio</div>
</div>
""", unsafe
