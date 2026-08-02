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
# ESTILIZAÇÃO CSS CUSTOMIZADA (TRANSFORMA OS BOTÕES EM CARDS CLICÁVEIS)
# -----------------------------------------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap');
    
    html, body, [class*="css"] { 
        font-family: 'Poppins', sans-serif;
        background-color: #0F172A !important;
        color: #F8FAFC !important;
    }

    .stApp {
        background-color: #0F172A;
    }

    /* Transformando os botões nativos do Streamlit em CARDS Clicáveis */
    div.stButton > button {
        width: 100% !important;
        height: 110px !important;
        background-color: #1E293B !important;
        color: #F8FAFC !important;
        border: 1px solid #334155 !important;
        border-radius: 12px !important;
        font-size: 1.1rem !important;
        font-weight: 600 !important;
        text-align: center !important;
        white-space: pre-wrap !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3) !important;
        transition: all 0.2s ease-in-out !important;
    }

    div.stButton > button:hover {
        border-color: #38BDF8 !important;
        background-color: #334155 !important;
        color: #38BDF8 !important;
        transform: translateY(-3px) !important;
    }

    /* Ajuste para botões secundários (Voltar/Sair) */
    .btn-voltar div.stButton > button {
        height: 45px !important;
        background-color: #0EA5E9 !important;
        color: #FFFFFF !important;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# ARQUIVOS E CARREGAMENTO DE DADOS
# -----------------------------------------------------------------------------
DATA_FILE = "jogadoras.json"
ADMINS_FILE = "administradores.json"

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

# -----------------------------------------------------------------------------
# INICIALIZAÇÃO DO ESTADO DA SESSÃO
# -----------------------------------------------------------------------------
if "jogadoras" not in st.session_state:
    st.session_state.jogadoras = carregar_dados(DATA_FILE, [])

if "administradores" not in st.session_state:
    def_admins = [{"nome": "Vagner Souza", "login": "admin", "senha": "1980"}]
    st.session_state.administradores = carregar_dados(ADMINS_FILE, def_admins)

if "usuario_logado" not in st.session_state:
    st.session_state.usuario_logado = None

if "admin_logged" not in st.session_state:
    st.session_state.admin_logged = False

if "tela_atual" not in st.session_state:
    st.session_state.tela_atual = "Home"

# -----------------------------------------------------------------------------
# CABEÇALHO
# -----------------------------------------------------------------------------
st.title("⚽ Resenha")
st.caption("peladinhas fc")
st.markdown("---")

# -----------------------------------------------------------------------------
# BARRA LATERAL (ÁREA DA JOGADORA E ADMIN)
# -----------------------------------------------------------------------------
with st.sidebar:
    st.title("👤 Menu de Acesso")
    
    if st.session_state.usuario_logado:
        st.success(f"Jogadora: **{st.session_state.usuario_logado}**")
        if st.button("🚪 Sair da Conta", key="btn_out_player"):
            st.session_state.usuario_logado = None
            st.session_state.tela_atual = "Home"
            st.rerun()

    elif st.session_state.admin_logged:
        st.info("🔑 Modo Administrador Ativo")
        if st.button("🚪 Sair do Modo Admin", key="btn_out_adm"):
            st.session_state.admin_logged = False
            st.session_state.tela_atual = "Home"
            st.rerun()

    else:
        st.warning("Nenhum usuário logado")
        aba_access = st.radio("Selecione o tipo de acesso:", ["Acesso Jogadora", "Acesso Administrador"])
        
        if aba_access == "Acesso Jogadora":
            if st.button("🔑 Entrar (Jogadora)", key="btn_nav_log_p"):
                st.session_state.tela_atual = "Login Jogadora"
                st.rerun()
            if st.button("📝 Criar Conta", key="btn_nav_cad_p"):
                st.session_state.tela_atual = "Cadastro"
                st.rerun()
        else:
            if st.button("🔐 Entrar como Admin", key="btn_nav_log_adm"):
                st.session_state.tela_atual = "Login Admin"
                st.rerun()

# -----------------------------------------------------------------------------
# TELAS DE LOGIN / CADASTRO
# -----------------------------------------------------------------------------
if st.session_state.tela_atual == "Login Jogadora":
    st.subheader("🔑 Login da Jogadora")
    with st.form("form_log_j"):
        u_p = st.text_input("Usuário")
        s_p = st.text_input("Senha", type="password")
        if st.form_submit_button("Entrar"):
            user = next((j for j in st.session_state.jogadoras if j.get("login") == u_p and j.get("senha") == s_p), None)
            if user:
                st.session_state.usuario_logado = user["nome"]
                st.session_state.tela_atual = "Home"
                st.rerun()
            else:
                st.error("Usuário ou senha inválidos.")
    if st.button("⬅️ Voltar"):
        st.session_state.tela_atual = "Home"
        st.rerun()

elif st.session_state.tela_atual == "Login Admin":
    st.subheader("🔐 Login do Administrador")
    with st.form("form_log_a"):
        u_a = st.text_input("Login Admin")
        s_a = st.text_input("Senha Admin", type="password")
        if st.form_submit_button("Acessar Painel Admin"):
            adm = next((a for a in st.session_state.administradores if a.get("login") == u_a and a.get("senha") == s_a), None)
            if adm:
                st.session_state.admin_logged = True
                st.session_state.tela_atual = "Painel Admin"
                st.rerun()
            else:
                st.error("Credenciais de administrador incorretas.")
    if st.button("⬅️ Voltar"):
        st.session_state.tela_atual = "Home"
        st.rerun()

elif st.session_state.tela_atual == "Cadastro":
    st.subheader("📝 Cadastrar Nova Jogadora")
    with st.form("form_cad"):
        n_cad = st.text_input("Nome Completo")
        u_cad = st.text_input("Login")
        s_cad = st.text_input("Senha", type="password")
        if st.form_submit_button("Cadastrar"):
            if n_cad and u_cad and s_cad:
                st.session_state.jogadoras.append({"nome": n_cad, "login": u_cad, "senha": s_cad, "tipo": "Diarista", "status": "Ativo"})
                salvar_dados(DATA_FILE, st.session_state.jogadoras)
                st.success("Cadastro realizado com sucesso!")
                st.session_state.tela_atual = "Login Jogadora"
                st.rerun()
            else:
                st.error("Preencha todos os campos.")
    if st.button("⬅️ Voltar"):
        st.session_state.tela_atual = "Home"
        st.rerun()

# -----------------------------------------------------------------------------
# TELA PRINCIPAL - GRID DE CARDS 100% CLICÁVEIS
# -----------------------------------------------------------------------------
elif st.session_state.tela_atual == "Home":
    c1, c2 = st.columns(2)

    with c1:
        if st.button("📜 REGULAMENTO\n\nConsulte regras de presença e horários"):
            st.session_state.tela_atual = "Regulamento"
            st.rerun()

        if st.button("🔀 SORTEIO DE TIMES\n\nVeja as equipes e distribuições da rodada"):
            st.session_state.tela_atual = "Sorteio"
            st.rerun()

        if st.button("💸 PAGAMENTO PIX\n\nChave Pix e envio de comprovantes"):
            st.session_state.tela_atual = "Pagamento Pix"
            st.rerun()

    with c2:
        if st.button("📌 LISTA DE PRESENÇA\n\nConfirme sua presença para o próximo jogo"):
            st.session_state.tela_atual = "Confirmar Presenca"
            st.rerun()

        if st.button("📋 ELENCO DE JOGADORAS\n\nLista de mensalistas e diaristas"):
            st.session_state.tela_atual = "Elenco"
            st.rerun()

        if st.button("⚙️ PAINEL ADMINISTRATIVO\n\nGestão do grupo e aprovação de lista"):
            if st.session_state.admin_logged:
                st.session_state.tela_atual = "Painel Admin"
            else:
                st.session_state.tela_atual = "Login Admin"
            st.rerun()

# -----------------------------------------------------------------------------
# DEMAIS TELAS
# -----------------------------------------------------------------------------
elif st.session_state.tela_atual == "Regulamento":
    st.subheader("📜 Regulamento")
    st.write("1. Mensalistas têm prioridade na lista até as 17h de Segunda-Feira.")
    st.write("2. Tolerância de atraso: 15 minutos.")
    if st.button("⬅️ Voltar ao Início"): st.session_state.tela_atual = "Home"; st.rerun()

elif st.session_state.tela_atual == "Sorteio":
    st.subheader("🔀 Sorteio dos Times")
    st.info("Times serão sorteados na Segunda-feira às 18:00.")
    if st.button("⬅️ Voltar ao Início"): st.session_state.tela_atual = "Home"; st.rerun()

elif st.session_state.tela_atual == "Pagamento Pix":
    st.subheader("💸 Pagamento via Pix")
    st.write("**Chave Pix:** 31989684010")
    st.write("**Titular:** Vagner Ferreira de Souza (PicPay)")
    if st.button("⬅️ Voltar ao Início"): st.session_state.tela_atual = "Home"; st.rerun()

elif st.session_state.tela_atual == "Confirmar Presenca":
    st.subheader("📌 Lista de Presença")
    st.success("Sua presença pode ser confirmada direto aqui.")
    if st.button("⬅️ Voltar ao Início"): st.session_state.tela_atual = "Home"; st.rerun()

elif st.session_state.tela_atual == "Elenco":
    st.subheader("📋 Elenco do Grupo")
    if st.session_state.jogadoras:
        st.dataframe(pd.DataFrame(st.session_state.jogadoras)[["nome", "tipo", "status"]], use_container_width=True)
    else:
        st.info("Nenhuma jogadora cadastrada ainda.")
    if st.button("⬅️ Voltar ao Início"): st.session_state.tela_atual = "Home"; st.rerun()

elif st.session_state.tela_atual == "Painel Admin":
    if not st.session_state.admin_logged:
        st.session_state.tela_atual = "Login Admin"
        st.rerun()
    st.subheader("⚙️ Painel do Administrador")
    st.success("Bem-vindo ao Painel de Controle, Vagner!")
    if st.button("⬅️ Voltar ao Início"): st.session_state.tela_atual = "Home"; st.rerun()

st.markdown("<br><hr><center><small>Peladinha FC • Sistema de Gestão</small></center>", unsafe_allow_html=True)
