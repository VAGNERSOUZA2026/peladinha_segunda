import streamlit as st
import pandas as pd
import json
import os
import random
import urllib.parse

# -----------------------------------------------------------------------------
# CONFIGURAÇÃO DA PÁGINA
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Peladinha FC | Gestão de Futebol Feminino",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------------------------------------------------------
# ESTILIZAÇÃO CSS CUSTOMIZADA (LAYOUT MODERNO & FEMININO)
# -----------------------------------------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;800&display=swap');
    html, body, [class*="css"] {
        font-family: 'Poppins', sans-serif;
    }

    /* Banner Principal */
    .hero-banner {
        background: linear-gradient(rgba(15, 23, 42, 0.75), rgba(15, 23, 42, 0.85)), 
                    url('https://images.unsplash.com/photo-1518091043644-c1d4457512c6?q=80&w=1200&auto=format&fit=crop');
        background-size: cover;
        background-position: center;
        border-radius: 16px;
        padding: 30px 20px;
        text-align: center;
        color: #FFFFFF;
        box-shadow: 0px 8px 20px rgba(0, 0, 0, 0.15);
        margin-bottom: 25px;
    }
    .hero-title { font-size: 2.2rem; font-weight: 800; margin-bottom: 5px; color: #FFFFFF; }
    .hero-subtitle { font-size: 1.0rem; font-weight: 300; color: #E2E8F0; }

    /* Cards Informativos */
    .card-notice {
        background: linear-gradient(135deg, #FFFBEB 0%, #FEF3C7 100%);
        border-left: 6px solid #F59E0B;
        padding: 18px;
        border-radius: 12px;
        margin-bottom: 20px;
    }
    
    .card-pix {
        background: linear-gradient(135deg, #ECFDF5 0%, #D1FAE5 100%);
        border: 2px dashed #10B981;
        padding: 25px;
        border-radius: 16px;
        text-align: center;
        margin-bottom: 20px;
    }

    .card-team {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-top: 5px solid #EC4899;
        border-radius: 14px;
        padding: 18px;
        margin-bottom: 15px;
        box-shadow: 0px 4px 12px rgba(0,0,0,0.05);
    }

    .card-alert {
        background-color: #EFF6FF;
        border-left: 6px solid #3B82F6;
        padding: 15px;
        border-radius: 10px;
        margin-top: 15px;
        margin-bottom: 15px;
    }

    /* Rodapé Customizado */
    .developer-footer {
        background: #0F172A;
        color: #94A3B8;
        text-align: center;
        padding: 15px;
        border-radius: 12px;
        margin-top: 40px;
        font-size: 0.9rem;
    }
    .developer-footer b { color: #38BDF8; }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# TRATAMENTO DE DADOS (ARQUIVOS JSON)
# -----------------------------------------------------------------------------
DATA_FILE = "jogadoras.json"
PRESENCAS_FILE = "presencas.json"
AVISOS_FILE = "avisos.json"
FINANCE_FILE = "financeiro.json"

def carregar_dados(filename, default):
    if os.path.exists(filename):
        try:
            with open(filename, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return default
    return default

def salvar_dados(filename, data):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

if "jogadoras" not in st.session_state:
    st.session_state.jogadoras = carregar_dados(DATA_FILE, [])

if "presencas" not in st.session_state:
    st.session_state.presencas = carregar_dados(PRESENCAS_FILE, [])

if "financeiro" not in st.session_state:
    st.session_state.financeiro = carregar_dados(FINANCE_FILE, [])

if "avisos" not in st.session_state:
    st.session_state.avisos = carregar_dados(AVISOS_FILE, {
        "vencimento": "Todo dia 10 de cada mês",
        "recado": "Favor chegarem 10 minutos antes para organizar o jogo!",
        "pix": "peladinhafc@email.com",
        "limite_vagas": 10
    })

if "usuario_logado" not in st.session_state:
    st.session_state.usuario_logado = None

if "admin_logged" not in st.session_state:
    st.session_state.admin_logged = False

# Lista filtrada de jogadoras ativas
jogadoras_cadastradas_ativas = [j["nome"] for j in st.session_state.jogadoras if j.get("status", "Ativo") == "Ativo"]
presencas_validas = [nome for nome in st.session_state.presencas if nome in jogadoras_cadastradas_ativas]

# -----------------------------------------------------------------------------
# BANNER DA APLICAÇÃO
# -----------------------------------------------------------------------------
st.markdown("""
<div class='hero-banner'>
    <div class='hero-title'>⚽ PELADINHA FC</div>
    <div class='hero-subtitle'>Gestão Inteligente & Sorteio de Futebol Feminino</div>
</div>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# MENU LATERAL & ÁREA DE LOGIN DA JOGADORA
# -----------------------------------------------------------------------------
st.sidebar.title("👤 Área do Usuário")

if st.session_state.usuario_logado:
    st.sidebar.success(f"Logada como: **{st.session_state.usuario_logado}**")
    if st.sidebar.button("🚪 Sair do Perfil"):
        st.session_state.usuario_logado = None
        st.rerun()
else:
    tab_login, tab_cadastro = st.sidebar.tabs(["Entrar", "Criar Conta"])
    
    with tab_login:
        login_input = st.text_input("Login", key="l_user")
        senha_input = st.text_input("Senha", type="password", key="l_pass")
        if st.button("🔑 Entrar"):
            user_found = next((j for j in st.session_state.jogadoras if j.get("login") == login_input and j.get("senha") == senha_input), None)
            if user_found:
                st.session_state.usuario_logado = user_found["nome"]
                st.sidebar.success(f"Bem-vinda, {user_found['nome']}!")
                st.rerun()
            else:
                st.sidebar.error("Login ou senha incorretos!")

    with tab_cadastro:
        cad_nome = st.text_input("Seu Nome Completo")
        cad_user = st.text_input("Escolha um Login")
        cad_pass = st.text_input("Escolha uma Senha", type="password")
        cad_tipo = st.selectbox("Categoria", ["Mensalista", "Avulso"])
        cad_contato = st.text_input("WhatsApp")

        if st.button("📝 Cadastrar"):
            if cad_nome and cad_user and cad_pass:
                if any(j.get("login") == cad_user for j in st.session_state.jogadoras):
                    st.sidebar.error("Esse login já está em uso!")
                else:
                    st.session_state.jogadoras.append({
                        "nome": cad_nome.strip(),
                        "login": cad_user.strip(),
                        "senha": cad_pass.strip(),
                        "tipo": cad_tipo,
                        "contato": cad_contato.strip(),
                        "status": "Ativo"
                    })
                    salvar_dados(DATA_FILE, st.session_state.jogadoras)
                    st.sidebar.success("Conta criada! Agora faça seu login.")
                    st.rerun()
            else:
                st.sidebar.error("Preencha Nome, Login e Senha!")

st.sidebar.markdown("---")
st.sidebar.title("📌 Navegação")
menu = st.sidebar.radio("Ir para:", [
    "📌 Presença no Jogo", 
    "🔀 Sorteio de Times", 
    "📊 Fluxo de Caixa",
    "💸 Pagamento & Pix",
    "📜 Regulamento",
    "📋 Elenco de Jogadoras", 
    "⚙️ Painel Admin"
])

# LOGIN ADMIN
st.sidebar.markdown("---")
st.sidebar.subheader("🔒 Acesso Restrito (Admin)")
if not st.session_state.admin_logged:
    senha_admin = st.sidebar.text_input("Senha Admin", type="password")
    if st.sidebar.button("Entrar como Admin"):
        if senha_admin == "1980":
            st.session_state.admin_logged = True
            st.sidebar.success("Modo Admin Ativo!")
            st.rerun()
        else:
            st.sidebar.error("Senha incorreta")
else:
    st.sidebar.info("🔑 Modo Admin Ativado")
    if st.sidebar.button("Sair do Admin"):
        st.session_state.admin_logged = False
        st.rerun()

# CRÉDITOS DO DESENVOLVEDOR NA SIDEBAR
st.sidebar.markdown("---")
st.sidebar.markdown("""
<div style='font-size: 0.85rem; color: #64748B; text-align: center;'>
    👨‍💻 <b>Desenvolvido por:</b><br>
    <span style='color: #0284C7; font-weight: 600;'>Vagner Souza / Ciência da Computação</span>
</div>
""", unsafe_allow_html=True)
                               
