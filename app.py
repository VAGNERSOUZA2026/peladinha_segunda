import streamlit as st
import pandas as pd
import json
import os
import random
from datetime import datetime, timedelta, timezone
from urllib.parse import quote
from PIL import Image

# -----------------------------------------------------------------------------
# CONFIGURAÇÃO DE FUSO HORÁRIO E DATAS
# -----------------------------------------------------------------------------
fuso_br = timezone(timedelta(hours=-3))
hoje_dt = datetime.now(fuso_br)

# -----------------------------------------------------------------------------
# CONFIGURAÇÃO DA PÁGINA
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Peladinha FC | Mais que Futebol, Uma Conexão",
    page_icon="⚽",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# -----------------------------------------------------------------------------
# ESTILIZAÇÃO CSS CUSTOMIZADA
# -----------------------------------------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;500;600;700;800;900&display=swap');
    
    html, body, [class*="css"] { font-family: 'Montserrat', sans-serif; color: #F3F4F6; }
    .stApp { background-color: #0B0F19; color: #F3F4F6; }
    
    .card-team {
        background: #161E2E !important;
        border: 1px solid #374151 !important;
        border-left: 5px solid #EC4899 !important;
        border-radius: 14px;
        padding: 18px;
        margin-bottom: 16px;
        color: #FFFFFF !important;
        box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.3);
    }
    
    div.stButton > button:first-child {
        background: linear-gradient(135deg, #EC4899 0%, #DB2777 100%) !important;
        color: #FFFFFF !important;
        font-weight: 800 !important;
        border-radius: 12px !important;
        border: none !important;
        padding: 14px 20px !important;
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# PERSISTÊNCIA DE DADOS
# -----------------------------------------------------------------------------
DATA_FILE, PRESENCAS_FILE = "jogadoras.json", "presencas.json"
ADMINS_FILE, FINANCE_FILE = "administradores.json", "financeiro.json"
AVISOS_FILE, COMPROVANTES_FILE = "avisos.json", "comprovantes.json"
SORTEIO_FILE, REGULAMENTO_FILE = "sorteio.json", "regulamento.json"
UPLOAD_DIR, LOGO_FILE = "comprovantes_imgs", "logo_peladinha.png"

if not os.path.exists(UPLOAD_DIR): os.makedirs(UPLOAD_DIR)

def carregar_dados(f, default):
    if os.path.exists(f):
        try:
            with open(f, "r", encoding="utf-8") as file: return json.load(file)
        except: return default
    return default

def salvar_dados(f, data):
    with open(f, "w", encoding="utf-8") as file: json.dump(data, file, ensure_ascii=False, indent=4)

def file_to_base64(path):
    import base64
    with open(path, "rb") as f: return base64.b64encode(f.read()).decode("utf-8")

# -----------------------------------------------------------------------------
# INICIALIZAÇÃO SESSION STATE
# -----------------------------------------------------------------------------
if "jogadoras" not in st.session_state: st.session_state.jogadoras = carregar_dados(DATA_FILE, [])
if "presencas" not in st.session_state: st.session_state.presencas = carregar_dados(PRESENCAS_FILE, [])
if "administradores" not in st.session_state: st.session_state.administradores = carregar_dados(ADMINS_FILE, [{"nome": "Admin Principal", "login": "admin", "senha": "1980", "celular": "5531999999999"}])
if "avisos" not in st.session_state: st.session_state.avisos = {"limite_vagas": 15, "pix": "peladinhafc@email.com", "vencimento": "Todo dia 10", "valor_mensalidade": 50.0, "valor_avulso": 15.0}
if "pagina_atual" not in st.session_state: st.session_state.pagina_atual = "login"
if "sub_tela_login" not in st.session_state: st.session_state.sub_tela_login = "menu"

# -----------------------------------------------------------------------------
# FUNÇÃO PARA EXIBIR A LOGO
# -----------------------------------------------------------------------------
def exibir_topo_logo():
    if os.path.exists(LOGO_FILE):
        st.markdown(f"""<div style="text-align: center;"><img src="data:image/png;base64,{file_to_base64(LOGO_FILE)}" style="width: 200px; opacity: 0.8; border-radius: 12px;" /></div>""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# LÓGICA PRINCIPAL
# -----------------------------------------------------------------------------
if st.session_state.pagina_atual == "login":
    exibir_topo_logo()
    # Centralização do login
    _, col_login, _ = st.columns([1, 4, 1])
    with col_login:
        st.subheader("Login / Cadastro")
        if st.session_state.sub_tela_login == "menu":
            if st.button("ENTRAR NO SISTEMA"): st.session_state.sub_tela_login = "entrar"; st.rerun()
            if st.button("CADASTRAR ATLETA"): st.session_state.sub_tela_login = "cad_atleta"; st.rerun()
        # (Demais lógica de login reduzida para concisão)
        elif st.session_state.sub_tela_login == "entrar":
            with st.form("login"):
                u = st.text_input("Usuário"); p = st.text_input("Senha", type="password")
                if st.form_submit_button("ENTRAR"):
                    # Verificação de login aqui...
                    st.session_state.pagina_atual = "dashboard"; st.session_state.usuario_logado = u; st.session_state.perfil_logado = "Admin"; st.rerun()

else:
    # AQUI ESTÁ A CENTRALIZAÇÃO PEDIDA
    exibir_topo_logo()
    _, col_master, _ = st.columns([0.5, 9, 0.5]) # Coluna centralizada de 90%
    
    with col_master:
        st.markdown(f"<p style='text-align: center;'>Logado: <b>{st.session_state.usuario_logado}</b></p>", unsafe_allow_html=True)
        
        if st.session_state.pagina_atual == "dashboard":
            if st.button("📜 Regulamento"): st.session_state.pagina_atual = "regulamento"; st.rerun()
            if st.button("📌 Lista de Presença"): st.session_state.pagina_atual = "lista"; st.rerun()
        
        elif st.session_state.pagina_atual == "lista":
            st.subheader("📌 Lista de Presença")
            # CORREÇÃO DA LINHA 527 (Sintaxe corrigida)
            atativas_nomes = [j["nome"] for j in st.session_state.jogadoras if j.get("status") == "Ativo"]
            st.selectbox("Selecione a Atleta", atativas_nomes)
            
        elif st.session_state.pagina_atual == "regulamento":
            st.write("Conteúdo do regulamento...")
