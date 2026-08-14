import streamlit as st
import pandas as pd
import json
import os
import random
from datetime import datetime, timedelta, timezone

# -----------------------------------------------------------------------------
# CONFIGURAÇÃO DE DATAS
# -----------------------------------------------------------------------------
fuso_br = timezone(timedelta(hours=-3))
hoje_dt = datetime.now(fuso_br)
hoje_str = hoje_dt.strftime("%d/%m")
mes_vigente_str = hoje_dt.strftime("%m/%Y")
ano_vigente_str = hoje_dt.strftime("%Y")

st.set_page_config(page_title="Peladinha FC", page_icon="⚽")

# -----------------------------------------------------------------------------
# PERSISTÊNCIA DE DADOS
# -----------------------------------------------------------------------------
DATA_FILE = "jogadoras.json"
PRESENCAS_FILE = "presencas.json"
AVISOS_FILE = "avisos.json"
FINANCE_FILE = "financeiro.json"
ADMINS_FILE = "administradores.json"
REGULAMENTO_FILE = "regulamento.json"
SORTEIO_FILE = "sorteio.json"
COMPROVANTES_FILE = "comprovantes.json"

def carregar_dados(filename, default):
    if os.path.exists(filename):
        try:
            with open(filename, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return default
    return default

def salvar_dados(filename, data):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# Inicialização do Session State
if "jogadoras" not in st.session_state: st.session_state.jogadoras = carregar_dados(DATA_FILE, [])
if "presencas" not in st.session_state: st.session_state.presencas = carregar_dados(PRESENCAS_FILE, [])
if "financeiro" not in st.session_state: st.session_state.financeiro = carregar_dados(FINANCE_FILE, [])
if "comprovantes" not in st.session_state: st.session_state.comprovantes = carregar_dados(COMPROVANTES_FILE, [])
if "administradores" not in st.session_state: 
    st.session_state.administradores = carregar_dados(ADMINS_FILE, [{"nome": "Admin", "login": "admin", "senha": "123"}])
if "avisos" not in st.session_state: 
    st.session_state.avisos = carregar_dados(AVISOS_FILE, {"limite_vagas": 15, "valor_mensalidade": 80.0})
if "regulamento" not in st.session_state: st.session_state.regulamento = carregar_dados(REGULAMENTO_FILE, [])
if "sorteio_oficial" not in st.session_state: st.session_state.sorteio_oficial = carregar_dados(SORTEIO_FILE, {})

if "pagina_atual" not in st.session_state: st.session_state.pagina_atual = "🏠 Início"
if "usuario_logado" not in st.session_state: st.session_state.usuario_logado = None
if "cargo_logado" not in st.session_state: st.session_state.cargo_logado = None

# -----------------------------------------------------------------------------
# TELA DE LOGIN (SEM CSS CUSTOMIZADO)
# -----------------------------------------------------------------------------
if not st.session_state.usuario_logado:
    st.title("⚽ Peladinha FC")
    tab1, tab2 = st.tabs(["🔑 Entrar", "📝 Cadastro"])
    
    with tab1:
        u = st.text_input("Usuário")
        s = st.text_input("Senha", type="password")
        if st.button("Entrar"):
            # Lógica simples de verificação
            st.session_state.usuario_logado = u
            st.session_state.cargo_logado = "Admin" if u == "admin" else "Jogadora"
            st.rerun()
    with tab2:
        st.write("Cadastro de nova jogadora.")
        # Campos de cadastro...
    st.stop()

# -----------------------------------------------------------------------------
# INTERFACE PRINCIPAL (PADRÃO)
# -----------------------------------------------------------------------------
st.header("Bem-vindo, " + str(st.session_state.usuario_logado))

if st.button("Sair"):
    st.session_state.usuario_logado = None
    st.rerun()

menu = st.radio("Navegação", ["🏠 Início", "📌 Presença", "📋 Elenco"])

if menu == "🏠 Início":
    st.write("Use o menu para navegar.")

elif menu == "📌 Presença":
    st.subheader("Lista de Presença")
    if st.button("Confirmar Presença"):
        st.session_state.presencas.append({"nome": st.session_state.usuario_logado})
        salvar_dados(PRESENCAS_FILE, st.session_state.presencas)
        st.success("Presença registrada!")
    
    for p in st.session_state.presencas:
        st.text("- " + p['nome'])

elif menu == "📋 Elenco":
    st.subheader("Elenco")
    for j in st.session_state.jogadoras:
        st.text("- " + j['nome'])
