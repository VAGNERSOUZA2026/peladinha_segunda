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
# PERSISTÊNCIA E DADOS (JSON)
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
    st.session_state.usuario_logado = "kelly" # Usuário atual logado

if "admin_logged" not in st.session_state:
    st.session_state.admin_logged = False

if "tela_atual" not in st.session_state:
    st.session_state.tela_atual = "Home"

# -----------------------------------------------------------------------------
# CABEÇALHO DO APP
# -----------------------------------------------------------------------------
st.title("⚽ Peladinha FC")
st.markdown("---")

# -----------------------------------------------------------------------------
# BARRA LATERAL (AUTENTICAÇÃO E PERFIS)
# -----------------------------------------------------------------------------
with st.sidebar:
    st.header("👤 Status da Conta")
    
    if st.session_state.admin_logged:
        st.success("🔑 Logado como: **ADMINISTRADOR**")
        if st.button("🚪 Sair do Modo Admin"):
            st.session_state.admin_logged = False
            st.rerun()
    elif st.session_state.usuario_logado:
        st.info(f"⚽ Logada como: **{st.session_state.usuario_logado}**")
        if st.button("🚪 Sair da Conta"):
            st.session_state.usuario_logado = None
            st.rerun()
    else:
        st.warning("⚠️ Você não está logada(o)")

    st.markdown("---")
    st.subheader("🔑 Alternar Login")
    
    col_l1, col_l2 = st.columns(2)
    with col_l1:
        if st.button("Entrar Admin"):
            st.session_state.admin_logged = True
            st.session_state.usuario_logado = None
            st.rerun()
    with col_l2:
        if st.button("Entrar Kelly"):
            st.session_state.usuario_logado = "kelly"
            st.session_state.admin_logged = False
            st.rerun()

    st.markdown("---")
    if st.button("🏠 Inicio (Home)", use_container_width=True):
        st.session_state.tela_atual = "Home"
        st.rerun()

# -----------------------------------------------------------------------------
# TELA 1: HOME
# -----------------------------------------------------------------------------
if st.session_state.tela_atual == "Home":
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
# TELA 2: LISTA DE PRESENÇA (REGRAS DE SEGURANÇA CORRIGIDAS)
# -----------------------------------------------------------------------------
elif st.session_state.tela_atual == "Confirmar Presenca":
    st.subheader("📌 Lista de Presença")

    # REGRA DE SEGURANÇA
    if st.session_state.admin_logged:
        st.info("💡 Modo Admin: Você tem permissão para confirmar ou remover qualquer jogadora.")
        lista_nomes = [j["nome"] for j in st.session_state.jogadoras]
        jogadora_para_confirmar = st.selectbox("Selecione a jogadora:", lista_nomes)
    elif st.session_state.usuario_logado:
        jogadora_para_confirmar = st.session_state.usuario_logado
        st.success(f"Confirmando presença para: **{jogadora_para_confirmar}**")
    else:
        st.warning("🔒 Você precisa fazer login para confirmar sua presença.")
        jogadora_para_confirmar = None

    if jogadora_para_confirmar:
        if st.button(f"✅ Confirmar Presença de {jogadora_para_confirmar}"):
            if jogadora_para_confirmar not in st.session_state.presencas:
                st.session_state.presencas.append(jogadora_para_confirmar)
                salvar_dados(PRESENCAS_FILE, st.session_state.presencas)
                st.success(f"Presença de {jogadora_para_confirmar} confirmada!")
                st.rerun()
            else:
                st.warning(f"{jogadora_para_confirmar} já está na lista!")

    st.markdown("---")
    
    # EXIBIÇÃO DAS VAGAS
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
                # Só o Admin ou a própria pessoa pode cancelar
                pode_cancelar = st.session_state.admin_logged or (st.session_state.usuario_logado == nome)
                if pode_cancelar:
                    if st.button("❌ Remover", key=f"del_{nome}"):
                        st.session_state.presencas.remove(nome)
                        salvar_dados(PRESENCAS_FILE, st.session_state.presencas)
                        st.rerun()
    else:
        st.info("Nenhuma jogadora confirmou presença ainda.")

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
    st.subheader("📜 Regulamento Interno")
    st.write("1. Mensalistas têm prioridade de vaga na lista até as 17h de Segunda-Feira.")
    st.write("2. Tolerância máxima de atraso: 15 minutos.")
    st.markdown("---")
    if st.button("⬅️ Voltar ao Início"): st.session_state.tela_atual = "Home"; st.rerun()

elif st.session_state.tela_atual == "Sorteio":
    st.subheader("🔀 Sorteio de Times")
    if len(st.session_state.presencas) < 4:
        st.warning("Mínimo de 4 jogadoras confirmadas na lista para sortear.")
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
    st.subheader("📋 Elenco")
    st.dataframe(pd.DataFrame(st.session_state.jogadoras)[["nome", "tipo", "status"]], use_container_width=True)
    st.markdown("---")
    if st.button("⬅️ Voltar ao Início"): st.session_state.tela_atual = "Home"; st.rerun()

elif st.session_state.tela_atual == "Painel Admin":
    st.subheader("⚙️ Painel do Administrador")
    if not st.session_state.admin_logged:
        st.error("🔒 Acesso restrito ao Administrador. Mude a conta na barra lateral.")
    else:
        st.success("Bem-vindo, Vagner!")
        if st.button("🚨 Limpar Lista de Presença"):
            st.session_state.presencas = []
            salvar_dados(PRESENCAS_FILE, [])
            st.success("Lista limpa com sucesso!")
            st.rerun()

    st.markdown("---")
    if st.button("⬅️ Voltar ao Início"): st.session_state.tela_atual = "Home"; st.rerun()
