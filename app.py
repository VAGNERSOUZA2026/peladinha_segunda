import streamlit as st
import pandas as pd
import json
import os
import random
import urllib.parse
import base64
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime, timezone, timedelta
import html

# -----------------------------------------------------------------------------
# FUSO HORÁRIO BRASIL (UTC-3)
# -----------------------------------------------------------------------------
FUSO_BRASIL = timezone(timedelta(hours=-3))

# -----------------------------------------------------------------------------
# CONFIGURAÇÃO DA PÁGINA (TEMA ESCURO ESTILO APP)
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Peladinha FC",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# -----------------------------------------------------------------------------
# ESTILIZAÇÃO CSS CUSTOMIZADA (LAYOUT DE CARDS GRID ESCUROS E TEXTOS CLAROS)
# -----------------------------------------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700;800&display=swap');
    
    html, body, [class*="css"] { 
        font-family: 'Poppins', sans-serif;
        background-color: #0F172A !important;
        color: #F8FAFC !important;
    }

    .stApp {
        background-color: #0F172A;
    }

    /* Títulos e Textos Claros para garantir leitura */
    h1, h2, h3, h4, h5, h6, p, span, label {
        color: #F8FAFC !important;
    }

    [data-testid="stSidebar"] {
        background-color: #111827;
        color: #F8FAFC;
    }

    /* ----------------------------------------------------------- */
    /* INTERFACE ESTILO APP (GRID DE CARDS IGUAL A FOTO)           */
    /* ----------------------------------------------------------- */
    
    .app-card {
        background-color: #1E293B;
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 15px;
        border: 1px solid #334155;
        transition: transform 0.2s, border-color 0.2s;
        cursor: pointer;
        display: block;
        color: inherit;
        text-decoration: none;
        min-height: 140px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3);
    }
    
    .app-card:hover {
        border-color: #0EA5E9;
        transform: translateY(-2px);
    }

    .card-title {
        font-size: 1.15rem;
        font-weight: 700;
        color: #F8FAFC;
        margin-top: 8px;
        margin-bottom: 4px;
    }

    .card-desc {
        font-size: 0.82rem;
        color: #94A3B8;
        line-height: 1.3;
    }

    .badge-pro {
        background-color: #0EA5E9;
        color: #FFFFFF;
        font-size: 0.65rem;
        font-weight: 800;
        padding: 2px 8px;
        border-radius: 6px;
        float: right;
        margin-top: -15px;
        margin-right: -15px;
    }

    /* Botões Streamlit em Dark Mode */
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        background-color: #38BDF8 !important;
        color: #0F172A !important;
        font-weight: 700;
        border: none;
        padding: 10px;
    }
    .stButton>button:hover {
        background-color: #7DD3FC !important;
    }

    /* Inputs e Forms em Dark Mode */
    .stTextInput>div>div>input, .stNumberInput>div>div>input, .stSelectbox>div>div>select {
        background-color: #1E293B;
        color: #F8FAFC;
        border-radius: 8px;
        border: 1px solid #334155;
    }

    /* Stat Box (Financeiro) */
    .stat-box {
        background-color: #1E293B;
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 15px;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# FUNÇÕES DE LEITURA E SALVAMENTO DE DADOS (JSON)
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
        except Exception:
            return default
    return default

def salvar_dados(filename, data):
    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    except Exception:
        pass

def formatar_nome_proprio(texto):
    if not texto: return ""
    palavras_minusculas = {'de', 'da', 'do', 'dos', 'das', 'e'}
    palavras = texto.strip().split()
    resultado = []
    for idx, palavra in enumerate(palavras):
        palavra_lower = palavra.lower()
        if idx > 0 and palavra_lower in palavras_minusculas:
            resultado.append(palavra_lower)
        else:
            resultado.append(palavra_lower.capitalize())
    return " ".join(resultado)

# -----------------------------------------------------------------------------
# INICIALIZAÇÃO DE ESTADO DO SISTEMA (PERSISTENTE NA SESSÃO)
# -----------------------------------------------------------------------------
if "jogadoras" not in st.session_state:
    st.session_state.jogadoras = carregar_dados(DATA_FILE, [])

if "presencas" not in st.session_state:
    st.session_state.presencas = carregar_dados(PRESENCAS_FILE, [])

if "financeiro" not in st.session_state:
    st.session_state.financeiro = carregar_dados(FINANCE_FILE, [])

if "comprovantes" not in st.session_state:
    st.session_state.comprovantes = carregar_dados(COMPROVANTES_FILE, [])

if "administradores" not in st.session_state:
    def_admins = [{"nome": "Vagner Souza (Admin)", "login": "admin", "senha": "1980", "principal": True}]
    st.session_state.administradores = carregar_dados(ADMINS_FILE, def_admins)

if "avisos" not in st.session_state:
    st.session_state.avisos = carregar_dados(AVISOS_FILE, {
        "vencimento": "Todo dia 10",
        "recado": "Jogos todas as segundas-feiras!",
        "pix_chave": "31989684010",
        "pix_nome": "Vagner Ferreira de Souza",
        "pix_banco": "PicPay",
        "limite_vagas": 15
    })

if "regulamento" not in st.session_state:
    st.session_state.regulamento = carregar_dados(REGULAMENTO_FILE, [
        {"topico": "📌 Prioridade Mensalistas", "regrinha": "As jogadoras MENSALISTAS têm prioridade absoluta até às 17:00 de segunda-feira."},
        {"topico": "⏳ Promoção de Diaristas", "regrinha": "Às 17:00, as vagas remanescentes são preenchidas pelas diaristas da fila de espera."},
        {"topico": "🎲 Sorteio Oficial", "regrinha": "Às 18:00 o sorteio automático dos times é realizado de forma equilibrada."},
        {"topico": "💸 Pagamentos", "regrinha": "Pagamentos via Pix para Vagner Souza. Envie o comprovante pelo app."}
    ])

if "sorteio_oficial" not in st.session_state:
    st.session_state.sorteio_oficial = carregar_dados(SORTEIO_FILE, {})

if "usuario_logado" not in st.session_state:
    st.session_state.usuario_logado = None

if "admin_logged" not in st.session_state:
    st.session_state.admin_logged = False

# IMPORTANTE: Definir tela inicial como 'Home'
if "tela_atual" not in st.session_state:
    st.session_state.tela_atual = "Home"

hoje_dt = datetime.now(FUSO_BRASIL)
hoje_str = hoje_dt.strftime("%d/%m/%Y")
mes_vigente_str = hoje_dt.strftime("%m/%Y")

# -----------------------------------------------------------------------------
# CABEÇALHO DO APP
# -----------------------------------------------------------------------------
st.title("⚽ Resenha")
st.caption("peladinhas fc")
st.markdown("---")

# -----------------------------------------------------------------------------
# ÁREA DE LOGIN E CADASTRO (PERSISTENTE NA SIDEBAR)
# -----------------------------------------------------------------------------
with st.sidebar:
    st.title("👤 Área da Jogadora")
    if st.session_state.usuario_logado:
        st.success(f"Conectada: **{st.session_state.usuario_logado}**")
        if st.button("🚪 Sair", key="btn_logout_side"):
            st.session_state.usuario_logado = None
            st.session_state.tela_atual = "Home"
            st.rerun()
    elif st.session_state.admin_logged:
        st.info("🔑 Modo Admin Ativo")
        if st.button("🚪 Sair do Admin", key="btn_logout_adm_side"):
            st.session_state.admin_logged = False
            st.session_state.tela_atual = "Home"
            st.rerun()
    else:
        st.warning("🔒 Área Restrita")
        if st.button("🔑 Fazer Login", key="btn_nav_login", use_container_width=True):
            st.session_state.tela_atual = "Login"
            st.rerun()
        if st.button("📝 Criar Conta", key="btn_nav_cad", use_container_width=True):
            st.session_state.tela_atual = "Cadastro"
            st.rerun()

# -----------------------------------------------------------------------------
# TELA DE LOGIN
# -----------------------------------------------------------------------------
if st.session_state.tela_atual == "Login":
    st.subheader("🔑 Login")
    with st.form("form_login_player"):
        l_user = st.text_input("Login (Usuário)")
        l_pass = st.text_input("Senha", type="password")
        btn_log = st.form_submit_button("Entrar", use_container_width=True)
        
        if btn_log:
            user_match = next((j for j in st.session_state.jogadoras if j.get("login") == l_user and j.get("senha") == l_pass), None)
            if user_match:
                st.session_state.usuario_logado = user_match["nome"]
                st.session_state.tela_atual = "Home"
                st.rerun()
            else:
                st.error("Login ou senha incorretos!")

    if st.button("⬅️ Voltar ao Início", key="btn_back_login"):
        st.session_state.tela_atual = "Home"
        st.rerun()

# -----------------------------------------------------------------------------
# TELA DE CADASTRO
# -----------------------------------------------------------------------------
elif st.session_state.tela_atual == "Cadastro":
    st.subheader("📝 Cadastrar Nova Jogadora")
    with st.form("form_cadastro", clear_on_submit=True):
        c_nome = st.text_input("Nome Completo *")
        c_user = st.text_input("Escolha um Login *")
        c_pass = st.text_input("Escolha uma Senha *", type="password")
        c_nasc = st.text_input("Nascimento (DD/MM)")
        st.caption("* Campos obrigatórios")
        if st.form_submit_button("Criar Minha Conta", use_container_width=True):
            if c_nome and c_user and c_pass:
                if any(j.get("login") == c_user for j in st.session_state.jogadoras):
                    st.error("Este nome de usuário já existe.")
                else:
                    st.session_state.jogadoras.append({
                        "nome": formatar_nome_proprio(c_nome),
                        "login": c_user.strip(),
                        "senha": c_pass.strip(),
                        "nascimento": c_nasc.strip(),
                        "tipo": "Diarista",
                        "status": "Ativo"
                    })
                    salvar_dados(DATA_FILE, st.session_state.jogadoras)
                    st.success(f"Conta criada para **{c_nome}**! Faça login.")
                    st.session_state.tela_atual = "Login"
                    st.rerun()
            else:
                st.error("Preencha todos os campos obrigatórios.")

    if st.button("⬅️ Voltar ao Início", key="btn_back_cad"):
        st.session_state.tela_atual = "Home"
        st.rerun()

# -----------------------------------------------------------------------------
# TELA PRINCIPAL (GRID DE CARDS IGUAL A FOTO)
# -----------------------------------------------------------------------------
elif st.session_state.tela_atual == "Home":
    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"""
        <div class='app-card'>
            <div class='card-title'>📜 Regulamento</div>
            <div class='card-desc'>Consulte as regras de presença, horários e prioridades do grupo.</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Acessar Regulamento", key="btn_card_reg"):
            st.session_state.tela_atual = "Regulamento"
            st.rerun()

        st.markdown("""
        <div class='app-card'>
            <span class='badge-pro'>PRO</span>
            <div class='card-title'>🔀 Sorteio do Time</div>
            <div class='card-desc'>Visualize os times sorteados ou realize um sorteio rápido de quadra.</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Ver Sorteio", key="btn_card_sor"):
            st.session_state.tela_atual = "Sorteio"
            st.rerun()

        st.markdown("""
        <div class='app-card'>
            <span class='badge-pro'>PRO</span>
            <div class='card-title'>💸 Pagamento Pix</div>
            <div class='card-desc'>Chave Pix Vagner Souza (PicPay) e envio de comprovantes.</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Realizar Pagamento", key="btn_card_pix"):
            st.session_state.tela_atual = "Pagamento Pix"
            st.rerun()

    with col2:
        st.markdown("""
        <div class='app-card'>
            <div class='card-title'>📌 Confirmar Presença</div>
            <div class='card-desc'>Garanta sua vaga na lista da próxima segunda-feira.</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Confirmar Vaga", key="btn_card_pre"):
            st.session_state.tela_atual = "Confirmar Presenca"
            st.rerun()

        st.markdown("""
        <div class='app-card'>
            <span class='badge-pro'>PRO</span>
            <div class='card-title'>📋 Elenco de Jogadoras</div>
            <div class='card-desc'>Lista completa de mensalistas, diaristas e status do grupo.</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Ver Elenco", key="btn_card_ele"):
            st.session_state.tela_atual = "Elenco"
            st.rerun()

        st.markdown("""
        <div class='app-card'>
            <span class='badge-pro'>PRO</span>
            <div class='card-title'>⚙️ Painel Admin</div>
            <div class='card-desc'>Gestão de elenco, fluxo de caixa e aprovação de pagamentos.</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Painel Admin", key="btn_card_adm"):
            st.session_state.tela_atual = "Painel Admin"
            st.rerun()

# -----------------------------------------------------------------------------
# OUTRAS TELAS
# -----------------------------------------------------------------------------
elif st.session_state.tela_atual == "Regulamento":
    st.subheader("📜 Regulamento Interno")
    if st.button("⬅️ Voltar"): st.session_state.tela_atual = "Home"; st.rerun()
    for r in st.session_state.regulamento:
        st.markdown(f"#### {r['topico']}"); st.write(r['regrinha'])

elif st.session_state.tela_atual == "Sorteio":
    st.subheader("🔀 Sorteio")
    if st.button("⬅️ Voltar"): st.session_state.tela_atual = "Home"; st.rerun()
    st.info("Ferramenta de sorteio em desenvolvimento.")

elif st.session_state.tela_atual == "Pagamento Pix":
    st.subheader("💸 Pagamento")
    if st.button("⬅️ Voltar"): st.session_state.tela_atual = "Home"; st.rerun()
    st.write(f"**Beneficiário:** {st.session_state.avisos['pix_nome']}")
    st.write(f"**Chave:** `{st.session_state.avisos['pix_chave']}`")

elif st.session_state.tela_atual == "Confirmar Presenca":
    st.subheader("📌 Presença")
    if st.button("⬅️ Voltar"): st.session_state.tela_atual = "Home"; st.rerun()
    st.warning("Lista de presença desabilitada para manutenção.")

elif st.session_state.tela_atual == "Elenco":
    st.subheader("📋 Elenco")
    if st.button("⬅️ Voltar"): st.session_state.tela_atual = "Home"; st.rerun()
    if st.session_state.jogadoras:
        df = pd.DataFrame(st.session_state.jogadoras)
        st.dataframe(df[["nome", "tipo", "status"]], use_container_width=True)

elif st.session_state.tela_atual == "Painel Admin":
    st.subheader("⚙️ Admin")
    if st.button("⬅️ Voltar"): st.session_state.tela_atual = "Home"; st.rerun()
    st.info("Área administrativa.")

# -----------------------------------------------------------------------------
# RODAPÉ
# -----------------------------------------------------------------------------
st.markdown("<div style='text-align:center; padding:20px; color:#94A3B8; font-size:0.85rem;'>Peladinha FC • Gestão Inteligente</div>", unsafe_allow_html=True)
