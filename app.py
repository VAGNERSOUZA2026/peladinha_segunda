import streamlit as st
import json
import os
from datetime import datetime, timezone, timedelta

# Configurações de Página
st.set_page_config(page_title="Peladinha FC | Gestão", layout="centered", initial_sidebar_state="collapsed")

# --- CSS Customizado para os Cards ---
st.markdown("""
<style>
    .stApp { background-color: #111827; color: #F3F4F6; }
    div[data-testid="stButton"] button {
        background-color: #881337 !important;
        color: white !important;
        border-radius: 10px !important;
        padding: 20px !important;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# --- Inicialização de Estado ---
if "pagina" not in st.session_state: st.session_state.pagina = "login"
if "user" not in st.session_state: st.session_state.user = None
if "perfil" not in st.session_state: st.session_state.perfil = None

# --- Funções de Tela ---
def tela_login():
    st.title("⚽ PELADINHA FC")
    tab1, tab2, tab3 = st.tabs(["🔑 Entrar", "📝 Criar Conta", "⚙️ Dev"])
    
    with tab1:
        user = st.text_input("Usuário")
        pwd = st.text_input("Senha", type="password")
        if st.button("ENTRAR"):
            # Lógica de verificação no arquivo JSON aqui
            st.session_state.user = user
            st.session_state.perfil = "Jogadora" # Exemplo: verificar cargo no JSON
            st.session_state.pagina = "dashboard"
            st.rerun()

    with tab2:
        st.text_input("Nome Completo")
        st.text_input("Login")
        st.text_input("Senha", type="password")
        if st.button("CADASTRAR"):
            st.info("Cadastro enviado para aprovação do Administrador.")

    with tab3:
        dev_pwd = st.text_input("Senha Mestre", type="password")
        if st.button("ACESSAR DEV"):
            if dev_pwd == "123": # Altere para sua senha segura
                st.session_state.user = "Desenvolvedor"
                st.session_state.perfil = "Dev"
                st.session_state.pagina = "dashboard"
                st.rerun()

def dashboard():
    st.title(f"Bem-vinda, {st.session_state.user}! 👋")
    
    # Definição dos cards disponíveis por perfil
    cards = ["📜 Regulamento", "📌 Lista de Presença", "🔀 Sorteio de Times", "📋 Elenco de Jogadoras", "💸 Pagamento Pix"]
    
    if st.session_state.perfil in ["Admin", "Dev"]:
        cards.extend(["📊 Fluxo de Caixa", "🛠️ Gerenciamento Geral"])
    
    # Layout dos Cards
    cols = st.columns(2)
    for i, nome in enumerate(cards):
        with cols[i % 2]:
            if st.button(nome, use_container_width=True):
                st.session_state.pagina = nome
                st.rerun()
                
    if st.button("🚪 Sair"):
        st.session_state.user = None
        st.session_state.pagina = "login"
        st.rerun()

# --- Fluxo de Navegação ---
if st.session_state.pagina == "login":
    tela_login()
else:
    dashboard()
