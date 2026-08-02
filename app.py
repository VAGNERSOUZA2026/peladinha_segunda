import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime, timezone, timedelta

# -----------------------------------------------------------------------------
# FUSO HORÁRIO BRASIL (UTC-3)
# -----------------------------------------------------------------------------
FUSO_BRASIL = timezone(timedelta(hours=-3))

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
# ESTILIZAÇÃO CSS CUSTOMIZADA (LAYOUT LIMPO, ESCURO E VISÍVEL)
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

    /* Textos sempre claros */
    h1, h2, h3, h4, h5, h6, p, label, span {
        color: #F8FAFC !important;
    }

    /* Cards/Botões Clicáveis da Home */
    div.stButton > button {
        width: 100% !important;
        min-height: 90px !important;
        background-color: #1E293B !important;
        color: #F8FAFC !important;
        border: 1px solid #334155 !important;
        border-radius: 12px !important;
        font-size: 1.05rem !important;
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
        transform: translateY(-2px) !important;
    }

    /* Inputs e Selects legíveis em Dark Mode */
    .stTextInput input, .stSelectbox div[role="combobox"] {
        background-color: #1E293B !important;
        color: #F8FAFC !important;
        border: 1px solid #334155 !important;
    }

    /* Ajuste visual da Tabela */
    [data-testid="stDataFrame"] {
        background-color: #1E293B !important;
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

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

# Lista padrão de jogadoras do seu elenco se não houver arquivo salvo
ELENCO_PADRAO = [
    {"nome": "Carol", "tipo": "Mensalista", "status": "Ativo"},
    {"nome": "Debora", "tipo": "Mensalista", "status": "Ativo"},
    {"nome": "Barbara", "tipo": "Mensalista", "status": "Ativo"},
    {"nome": "Michele", "tipo": "Mensalista", "status": "Ativo"},
    {"nome": "Duda", "tipo": "Mensalista", "status": "Ativo"},
    {"nome": "Luzinete", "tipo": "Mensalista", "status": "Ativo"},
    {"nome": "Cicera", "tipo": "Mensalista", "status": "Ativo"},
    {"nome": "Dani", "tipo": "Mensalista", "status": "Ativo"},
    {"nome": "Luciana", "tipo": "Mensalista", "status": "Ativo"},
    {"nome": "Amanda", "tipo": "Diarista", "status": "Ativo"},
    {"nome": "kelly", "tipo": "Diarista", "status": "Ativo"}
]

if "jogadoras" not in st.session_state:
    st.session_state.jogadoras = carregar_dados(DATA_FILE, ELENCO_PADRAO)

if "presencas" not in st.session_state:
    st.session_state.presencas = carregar_dados(PRESENCAS_FILE, [])

if "usuario_logado" not in st.session_state:
    st.session_state.usuario_logado = "kelly"

if "admin_logged" not in st.session_state:
    st.session_state.admin_logged = True

if "tela_atual" not in st.session_state:
    st.session_state.tela_atual = "Home"

# -----------------------------------------------------------------------------
# CABEÇALHO DO APP
# -----------------------------------------------------------------------------
st.title("⚽ Resenha")
st.caption("peladinhas fc")
st.markdown("---")

# -----------------------------------------------------------------------------
# BARRA LATERAL (MENU DE NAVEGAÇÃO E ACESSO)
# -----------------------------------------------------------------------------
with st.sidebar:
    st.title("👤 Menu de Acesso")
    
    if st.session_state.usuario_logado:
        st.success(f"Conectada: **{st.session_state.usuario_logado}**")
    
    if st.session_state.admin_logged:
        st.info("🔑 Modo Administrador Ativo")

    st.markdown("---")
    if st.button("🏠 Inicio (Home)", key="btn_side_home"):
        st.session_state.tela_atual = "Home"
        st.rerun()

    modo_acesso = st.radio("Modo de Acesso:", ["Jogadora", "Administrador"])
    if modo_acesso == "Administrador":
        st.session_state.admin_logged = True
    else:
        st.session_state.admin_logged = False

# -----------------------------------------------------------------------------
# TELA 1: HOME (CARDS GRANDES E DIRECT-CLICK)
# -----------------------------------------------------------------------------
if st.session_state.tela_atual == "Home":
    c1, c2 = st.columns(2)

    with c1:
        if st.button("📌 CONFIRMAR PRESENÇA\n\nGaranta sua vaga para a próxima segunda"):
            st.session_state.tela_atual = "Confirmar Presenca"
            st.rerun()

        if st.button("📜 REGULAMENTO\n\nConsulte regras, horários e tolerâncias"):
            st.session_state.tela_atual = "Regulamento"
            st.rerun()

        if st.button("🔀 SORTEIO DE TIMES\n\nSorteio automático das equipes"):
            st.session_state.tela_atual = "Sorteio"
            st.rerun()

    with c2:
        if st.button("💸 PAGAMENTO PIX\n\nChave Pix e comprovantes"):
            st.session_state.tela_atual = "Pagamento Pix"
            st.rerun()

        if st.button("📋 ELENCO DE JOGADORAS\n\nLista do grupo de mensalistas e diaristas"):
            st.session_state.tela_atual = "Elenco"
            st.rerun()

        if st.button("⚙️ PAINEL ADMINISTRATIVO\n\nGerenciar elenco e lista de presença"):
            st.session_state.tela_atual = "Painel Admin"
            st.rerun()

# -----------------------------------------------------------------------------
# TELA 2: LISTA DE PRESENÇA (INTERATIVA E OPERACIONAL)
# -----------------------------------------------------------------------------
elif st.session_state.tela_atual == "Confirmar Presenca":
    st.subheader("📌 Lista de Presença da Próxima Segunda")
    
    # Selecionar jogadora para confirmar
    lista_nomes = [j["nome"] for j in st.session_state.jogadoras]
    
    c_sel, c_btn = st.columns([2, 1])
    with c_sel:
        jogadora_selecionada = st.selectbox("Selecione seu nome para confirmar:", lista_nomes)
    
    with c_btn:
        st.write("")
        st.write("")
        if st.button("✅ Confirmar Vaga"):
            if jogadora_selecionada not in st.session_state.presencas:
                st.session_state.presencas.append(jogadora_selecionada)
                salvar_dados(PRESENCAS_FILE, st.session_state.presencas)
                st.success(f"{jogadora_selecionada} confirmada com sucesso!")
                st.rerun()
            else:
                st.warning("Esta jogadora já está na lista de presença!")

    st.markdown("---")
    
    # Exibição das Confirmadas (Vagas 0/12)
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
                if st.button("❌ Cancelar", key=f"del_{nome}"):
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
# TELA 3: REGULAMENTO
# -----------------------------------------------------------------------------
elif st.session_state.tela_atual == "Regulamento":
    st.subheader("📜 Regulamento Interno do Grupo")
    st.markdown("""
    * **📌 Prioridade Mensalistas:** As jogadoras Mensalistas possuem vaga garantida até as 17:00 de Segunda-Feira.
    * **⏳ Vagas Diaristas:** Às 17:00, as vagas remanescentes são liberas para as diaristas da fila de espera.
    * **⏰ Tolerância:** 15 minutos de tolerância para atrasos no horário do jogo.
    * **💸 Pagamento:** Pagamentos por jogo/mês devem ser feitos via Pix diretamente para Vagner Souza.
    """)
    st.markdown("---")
    if st.button("⬅️ Voltar ao Início"):
        st.session_state.tela_atual = "Home"
        st.rerun()

# -----------------------------------------------------------------------------
# TELA 4: SORTEIO DE TIMES
# -----------------------------------------------------------------------------
elif st.session_state.tela_atual == "Sorteio":
    st.subheader("🔀 Sorteio Automático de Times")
    
    if len(st.session_state.presencas) < 4:
        st.warning("São necessárias pelo menos 4 jogadoras confirmadas na lista para realizar o sorteio.")
    else:
        if st.button("🎲 Realizar Novo Sorteio"):
            import random
            lista_sorteio = list(st.session_state.presencas)
            random.shuffle(lista_sorteio)
            
            meio = len(lista_sorteio) // 2
            st.session_state.time_a = lista_sorteio[:meio]
            st.session_state.time_b = lista_sorteio[meio:]

        if "time_a" in st.session_state and "time_b" in st.session_state:
            col_a, col_b = st.columns(2)
            with col_a:
                st.markdown("### 🟢 Time A")
                for p in st.session_state.time_a:
                    st.write(f"- {p}")
            with col_b:
                st.markdown("### 🔵 Time B")
                for p in st.session_state.time_b:
                    st.write(f"- {p}")

    st.markdown("---")
    if st.button("⬅️ Voltar ao Início"):
        st.session_state.tela_atual = "Home"
        st.rerun()

# -----------------------------------------------------------------------------
# TELA 5: PAGAMENTO PIX
# -----------------------------------------------------------------------------
elif st.session_state.tela_atual == "Pagamento Pix":
    st.subheader("💸 Pagamento via Pix")
    
    st.markdown("""
    **Dados do Recebedor:**
    * **Titular:** Vagner Ferreira de Souza
    * **Banco:** PicPay
    * **Chave Pix (Telefone):** `31989684010`
    """)
    
    st.text_input("Chave Pix para copiar:", "31989684010")
    
    st.markdown("---")
    st.write("### 📤 Enviar Comprovante")
    arquivo_comp = st.file_uploader("Envie a foto/PDF do comprovante de pagamento:", type=["png", "jpg", "jpeg", "pdf"])
    if arquivo_comp:
        st.success("Comprovante enviado com sucesso para validação!")

    st.markdown("---")
    if st.button("⬅️ Voltar ao Início"):
        st.session_state.tela_atual = "Home"
        st.rerun()

# -----------------------------------------------------------------------------
# TELA 6: ELENCO DE JOGADORAS
# -----------------------------------------------------------------------------
elif st.session_state.tela_atual == "Elenco":
    st.subheader("📋 Elenco Cadastrado")
    if st.session_state.jogadoras:
        df = pd.DataFrame(st.session_state.jogadoras)
        st.dataframe(df, use_container_width=True)
    else:
        st.info("Nenhuma jogadora cadastrada.")

    st.markdown("---")
    if st.button("⬅️ Voltar ao Início"):
        st.session_state.tela_atual = "Home"
        st.rerun()

# -----------------------------------------------------------------------------
# TELA 7: PAINEL ADMIN
# -----------------------------------------------------------------------------
elif st.session_state.tela_atual == "Painel Admin":
    st.subheader("⚙️ Painel do Administrador (Vagner)")
    
    tab1, tab2 = st.tabs(["➕ Adicionar Jogadora", "🧹 Limpar Lista de Presença"])
    
    with tab1:
        with st.form("add_player_admin"):
            novo_nome = st.text_input("Nome da Jogadora:")
            novo_tipo = st.selectbox("Tipo:", ["Mensalista", "Diarista"])
            if st.form_submit_button("Cadastrar no Elenco"):
                if novo_nome:
                    st.session_state.jogadoras.append({"nome": novo_nome, "tipo": novo_tipo, "status": "Ativo"})
                    salvar_dados(DATA_FILE, st.session_state.jogadoras)
                    st.success(f"{novo_nome} adicionada com sucesso ao elenco!")
                    st.rerun()

    with tab2:
        st.warning("Esta ação removerá todas as jogadoras salvas na lista de presença atual.")
        if st.button("🚨 Limpar Lista de Presença"):
            st.session_state.presencas = []
            salvar_dados(PRESENCAS_FILE, [])
            st.success("Lista de presença zerada para o próximo jogo!")
            st.rerun()

    st.markdown("---")
    if st.button("⬅️ Voltar ao Início"):
        st.session_state.tela_atual = "Home"
        st.rerun()

# -----------------------------------------------------------------------------
# RODAPÉ
# -----------------------------------------------------------------------------
st.markdown("<br><hr><center><small>Peladinha FC • Sistema de Gestão</small></center>", unsafe_allow_html=True)
