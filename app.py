import streamlit as st
import pandas as pd
import json
import os
import random
from datetime import datetime, timedelta, timezone

# [Manter as configurações de fuso horário, dados, salvar/carregar igual ao anterior]
# ... (manter todas as funções carregar_dados, salvar_dados, etc.)

st.set_page_config(
    page_title="Peladinha FC | Resenha & Gestão",
    page_icon="⚽",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ESTILIZAÇÃO COM FUNDO FIXO E LEITURA OTIMIZADA
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] { 
        font-family: 'Montserrat', sans-serif; 
    }

    /* Imagem de fundo aplicada ao app com filtro de escurecimento */
    .stApp {
        background: linear-gradient(rgba(15, 15, 19, 0.85), rgba(15, 15, 19, 0.85)), 
                    url('images (1).jpg');
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }

    .app-header {
        background: rgba(24, 24, 32, 0.8);
        padding: 20px;
        border-radius: 16px;
        border: 1px solid rgba(236, 72, 153, 0.3);
        text-align: center;
        backdrop-filter: blur(5px);
    }
    
    .card-team {
        background: rgba(30, 30, 40, 0.85) !important;
        border: 1px solid rgba(236, 72, 153, 0.3) !important;
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 15px;
        color: #FFFFFF !important;
        backdrop-filter: blur(5px);
    }
    
    /* Garantir que inputs e botões tenham destaque */
    div.stButton > button {
        background-color: #EC4899 !important;
        color: #FFFFFF !important;
    }
    
    .stTextInput input, .stSelectbox select {
        background-color: rgba(0,0,0,0.3) !important;
        color: white !important;
        border: 1px solid #EC4899 !important;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# TELA DE LOGIN (Sem imagem lateral, agora com fundo geral)
# -----------------------------------------------------------------------------
if not st.session_state.usuario_logado:
    st.markdown("<div class='app-header'><h1>⚽ Peladinha FC</h1></div>", unsafe_allow_html=True)
    
    # Apenas o formulário centralizado
    tab_entrar, tab_cadastrar = st.tabs(["🔑 Entrar", "📝 Cadastrar"])
    with tab_entrar:
        with st.form("form_login"):
            u_login = st.text_input("Usuário")
            u_senha = st.text_input("Senha", type="password")
            if st.form_submit_button("ENTRAR"):
                # ... (Lógica de autenticação)
                st.rerun()
    # ... resto do código igual
