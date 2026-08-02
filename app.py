import streamlit as st
import pandas as pd
import json
import os

# -----------------------------------------------------------------------------
# CONFIGURAÇÃO DA PÁGINA
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Peladinha FC",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------------------------------------------------------
# DADOS E ARQUIVOS (JSON)
# -----------------------------------------------------------------------------
DATA_FILE = "jogadoras.json"
PRESENCAS_FILE = "presencas.json"

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

# Lista Padrão (só usada se o arquivo jogadoras.json não existir)
ELENCO_PADRAO = [
    {"nome": "Carol", "login": "carol", "senha": "123", "tipo": "Mensalista", "status": "Ativo"},
    {"nome": "Debora", "login": "debora", "senha": "123", "tipo": "Mensalista", "status": "Ativo"},
    {"nome": "Barbara", "login": "barbara", "senha": "123", "tipo": "Mensalista", "status": "Ativo"},
    {"nome": "Michele", "login": "michele", "senha": "123", "tipo": "Mensalista", "status": "Ativo"},
    {"nome": "Duda", "login": "duda", "senha": "123", "tipo": "Mensalista", "status": "Ativo"},
    {"nome": "Luzinete", "login": "luzinete", "senha": "123", "tipo": "Mensalista", "status": "Ativo"},
    {"nome": "Cicera", "login": "cicera", "senha": "123", "tipo": "Mensalista", "status": "Ativo"},
    {"nome": "Dani", "login": "dani", "senha": "123", "tipo": "Mensalista", "status": "Ativo"},
    {"nome": "Luciana", "login": "luciana", "senha": "123", "tipo": "Mensalista", "status": "Ativo"},
    {"nome": "Amanda", "login": "amanda", "senha": "123", "tipo": "Diarista", "status": "Ativo"},
    {"nome": "kelly", "login": "kelly", "senha": "123", "tipo": "Diarista", "status": "Ativo"}
]

if "jogadoras" not in st.session_state:
    st.session_state.jogadoras = carregar_dados(DATA_FILE, ELENCO_PADRAO)

if "presencas" not in st.session_state:
    st.session_state.presencas = carregar_dados(PRESENCAS_FILE, [])

if "usuario_logado" not in st.session_state:
    st.session_state.usuario_logado = None  # NINGUÉM LOGADO POR PADRÃO

if "admin_logged" not in st.session_state:
    st.session_state.admin_logged = False  # ADMIN DESLOGADO POR PADRÃO

if "tela_atual" not in st.session_state:
    st.session_state.tela_atual = "Home"

# -----------------------------------------------------------------------------
# CABEÇALHO
# -----------------------------------------------------------------------------
st.title("⚽ Peladinha FC")
st.markdown("---")

# -----------------------------------------------------------------------------
# BARRA LATERAL (MENU LIMPO)
# -----------------------------------------------------------------------------
with st.sidebar:
    st.header("👤 Área de Acesso")
    
    if st.session_state.admin_logged:
        st.success("🔑 Conectado: **ADMINISTRADOR**")
        if st.button("🚪 Sair do Admin", use_container_width=True):
            st.session_state.admin_logged = False
            st.session_state.tela_atual = "Home"
            st.rerun()

    elif st.session_state.usuario_logado:
        st.info(f"⚽ Jogadora: **{st.session_state.usuario_logado}**")
        if st.button("🚪 Sair da Conta", use_container_width=True):
            st.session_state.usuario_logado = None
            st.session_state.tela_atual = "Home"
            st.rerun()

    else:
        st.warning("🔒 Ninguém Conectado")
        if st.button("🔑 Entrar (Jogadora)", use_container_width=True):
            st.session_state.tela_atual = "Login Jogadora"
            st.rerun()
            
        if st.button("🔐 Entrar como Admin", use_container_width=True):
            st.session_state.tela_atual = "Login Admin"
            st.rerun()

    st.markdown("---")
    if st.button("🏠 Inicio (Home)", use_container_width=True):
        st.session_state.tela_atual = "Home"
        st.rerun()

# -----------------------------------------------------------------------------
# TELAS DE LOGIN DE VERDADE (COM SENHA)
# -----------------------------------------------------------------------------
if st.session_state.tela_atual == "Login Jogadora":
    st.subheader("🔑 Login da Jogadora")
    with st.form("form_login_player"):
        u = st.text_input("Usuário (ex: kelly, carol, debora)")
        s = st.text_input("Senha", type="password")
        if st.form_submit_button("Entrar"):
            user = next((j for j in st.session_state.jogadoras if j.get("login") == u.strip().lower() and j.get("senha") == s), None)
            if user:
                st.session_state.usuario_logado = user["nome"]
                st.session_state.admin_logged = False
                st.session_state.tela_atual = "Home"
                st.rerun()
            else:
                st.error("Usuário ou senha incorretos!")

elif st.session_state.tela_atual == "Login Admin":
    st.subheader("🔐 Login do Administrador")
    with st.form("form_login_admin"):
        u_adm = st.text_input("Login do Administrador")
        s_adm = st.text_input("Senha do Administrador", type="password")
        if st.form_submit_button("Acessar Painel"):
            # Credenciais do Admin: admin / 1980
            if u_adm.strip() == "admin" and s_adm == "1980":
                st.session_state.admin_logged = True
                st.session_state.usuario_logado = None
                st.session_state.tela_atual = "Home"
                st.rerun()
            else:
                st.error("Credenciais de administrador incorretas!")

# -----------------------------------------------------------------------------
# TELA 1: HOME
# -----------------------------------------------------------------------------
elif st.session_state.tela_atual == "Home":
    c1, c2 = st.columns(2)

    with c1:
        if st.button("📌 CONFIRMAR PRESENÇA", use_container_width=True):
            st.session_state.tela_atual = "Confirmar Presenca"
            st.rerun()

        if st.button("📜 REGULAMENTO", use_container_width=True):
            st.session_state.tela_atual = "Regulamento"
            st.rerun()

        if st.button("🔀 SORTEIO DE TIMES", use_container_width=True):
            st.session_state.tela_atual = "Sorteio"
            st.rerun()

    with c2:
        if st.button("💸 PAGAMENTO PIX", use_container_width=True):
            st.session_state.tela_atual = "Pagamento Pix"
            st.rerun()

        if st.button("📋 ELENCO DE JOGADORAS", use_container_width=True):
            st.session_state.tela_atual = "Elenco"
            st.rerun()

        if st.button("⚙️ PAINEL ADMIN", use_container_width=True):
            st.session_state.tela_atual = "Painel Admin"
            st.rerun()

# -----------------------------------------------------------------------------
# TELA 2: LISTA DE PRESENÇA
# -----------------------------------------------------------------------------
elif st.session_state.tela_atual == "Confirmar Presenca":
    st.subheader("📌 Lista de Presença")

    if st.session_state.admin_logged:
        st.info("💡 Modo Admin: Escolha qualquer jogadora para confirmar.")
        lista_nomes = [j["nome"] for j in st.session_state.jogadoras]
        jogadora_alvo = st.selectbox("Selecione a jogadora:", lista_nomes)
    elif st.session_state.usuario_logado:
        jogadora_alvo = st.session_state.usuario_logado
        st.success(f"Confirmando vaga para: **{jogadora_alvo}**")
    else:
        st.warning("🔒 Você precisa fazer login para confirmar sua presença na lista.")
        jogadora_alvo = None

    if jogadora_alvo:
        if st.button(f"✅ Confirmar Presença ({jogadora_alvo})"):
            if jogadora_alvo not in st.session_state.presencas:
                st.session_state.presencas.append(jogadora_alvo)
                salvar_dados(PRESENCAS_FILE, st.session_state.presencas)
                st.success(f"Presença de {jogadora_alvo} confirmada!")
                st.rerun()
            else:
                st.warning("Esta jogadora já está na lista de presença.")

    st.markdown("---")
    
    LIMITE_VAGAS = 12
    confirmadas = st.session_state.presencas[:LIMITE_VAGAS]
    espera = st.session_state.presencas[LIMITE_VAGAS:]

    st.markdown(f"### 📋 Vagas Confirmadas ({len(confirmadas)}/{LIMITE_VAGAS})")
    if confirmadas:
        for idx, nome in enumerate(confirmadas, start=1):
            col_nome, col_del = st.columns([4, 1])
            with col_nome:
                st.write(f"**{idx}. {nome}** ✅")
            with col_del:
                # Cancelamento permitido se for Admin ou a própria jogadora logada
                if st.session_state.admin_logged or (st.session_state.usuario_logado == nome):
                    if st.button("❌ Remover", key=f"del_{nome}"):
                        st.session_state.presencas.remove(nome)
                        salvar_dados(PRESENCAS_FILE, st.session_state.presencas)
                        st.rerun()
    else:
        st.info("Nenhuma jogadora na lista ainda.")

    if espera:
        st.markdown(f"### ⏳ Fila de Espera ({len(espera)})")
        for idx, nome in enumerate(espera, start=1):
            st.write(f"{idx}. {nome}")

    st.markdown("---")
    if st.button("⬅️ Voltar ao Início"):
        st.session_state.tela_atual = "Home"
        st.rerun()

# -----------------------------------------------------------------------------
# DEMAIS TELAS
# -----------------------------------------------------------------------------
elif st.session_state.tela_atual == "Regulamento":
    st.subheader("📜 Regulamento")
    st.write("1. Mensalistas têm prioridade de vaga na lista até as 17h de Segunda-Feira.")
    st.write("2. Tolerância de atraso: 15 minutos.")
    st.markdown("---")
    if st.button("⬅️ Voltar ao Início"): st.session_state.tela_atual = "Home"; st.rerun()

elif st.session_state.tela_atual == "Sorteio":
    st.subheader("🔀 Sorteio de Times")
    if len(st.session_state.presencas) < 4:
        st.warning("É preciso pelo menos 4 jogadoras confirmadas para sortear.")
    else:
        if st.button("🎲 Realizar Sorteio"):
            import random
            lista = list(st.session_state.presencas)
            random.shuffle(lista)
            m = len(lista) // 2
            st.session_state.t_a = lista[:m]
            st.session_state.t_b = lista[m:]
        
        if "t_a" in st.session_state:
            ca, cb = st.columns(2)
            with ca:
                st.markdown("### 🟢 Time A")
                for p in st.session_state.t_a: st.write(f"- {p}")
            with cb:
                st.markdown("### 🔵 Time B")
                for p in st.session_state.t_b: st.write(f"- {p}")

    st.markdown("---")
    if st.button("⬅️ Voltar ao Início"): st.session_state.tela_atual = "Home"; st.rerun()

elif st.session_state.tela_atual == "Pagamento Pix":
    st.subheader("💸 Pagamento via Pix")
    st.write("**Titular:** Vagner Ferreira de Souza")
    st.write("**Chave Pix:** 31989684010 (PicPay)")
    st.markdown("---")
    if st.button("⬅️ Voltar ao Início"): st.session_state.tela_atual = "Home"; st.rerun()

elif st.session_state.tela_atual == "Elenco":
    st.subheader("📋 Elenco Cadastrado")
    st.dataframe(pd.DataFrame(st.session_state.jogadoras)[["nome", "tipo", "status"]], use_container_width=True)
    st.markdown("---")
    if st.button("⬅️ Voltar ao Início"): st.session_state.tela_atual = "Home"; st.rerun()

elif st.session_state.tela_atual == "Painel Admin":
    st.subheader("⚙️ Painel do Administrador")
    if not st.session_state.admin_logged:
        st.error("🔒 Você precisa fazer login como Administrador para acessar esta página.")
    else:
        st.success("Painel do Administrador ativo!")
        if st.button("🚨 Zerar/Limpar Lista de Presença"):
            st.session_state.presencas = []
            salvar_dados(PRESENCAS_FILE, [])
            st.success("Lista limpa!")
            st.rerun()

    st.markdown("---")
    if st.button("⬅️ Voltar ao Início"): st.session_state.tela_atual = "Home"; st.rerun()
