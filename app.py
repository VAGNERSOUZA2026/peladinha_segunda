import streamlit as st
import json
import os
import random
from datetime import datetime, timezone, timedelta
from urllib.parse import quote

# -----------------------------------------------------------------------------
# CONFIGURAÇÕES E PERSISTÊNCIA
# -----------------------------------------------------------------------------
fuso_br = timezone(timedelta(hours=-3))
hoje_dt = datetime.now(fuso_br)
DATA_FILE, PRESENCAS_FILE = "jogadoras.json", "presencas.json"
ADMINS_FILE, FINANCE_FILE = "administradores.json", "financeiro.json"
AVISOS_FILE, COMPROVANTES_FILE = "avisos.json", "comprovantes.json"
SORTEIO_FILE, CONTEUDOS_FILE = "sorteio.json", "conteudos.json"
UPLOAD_DIR, LOGO_FILE = "comprovantes_imgs", "logo_peladinha.png"

for d in [UPLOAD_DIR]: 
    if not os.path.exists(d): os.makedirs(d)

def carregar_dados(f, default):
    if os.path.exists(f):
        try:
            with open(f, "r", encoding="utf-8") as file: return json.load(file)
        except: return default
    return default

def salvar_dados(f, data):
    with open(f, "w", encoding="utf-8") as file: json.dump(data, file, ensure_ascii=False, indent=4)

# -----------------------------------------------------------------------------
# ESTILIZAÇÃO E ESTRUTURA
# -----------------------------------------------------------------------------
st.set_page_config(page_title="Peladinha FC", layout="centered")

st.markdown("""
<style>
    .stApp { background-color: #0B0F19; color: #F3F4F6; font-family: sans-serif; }
    .card-team { background: #161E2E !important; border: 1px solid #374151 !important; border-left: 5px solid #EC4899 !important; border-radius: 14px; padding: 18px; margin-bottom: 16px; color: #FFFFFF !important; }
    div.stButton > button { background: linear-gradient(135deg, #EC4899 0%, #DB2777 100%) !important; color: white !important; font-weight: 800 !important; border-radius: 12px !important; border: none !important; width: 100%; }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# ESTADO DA SESSÃO
# -----------------------------------------------------------------------------
if "jogadoras" not in st.session_state: st.session_state.jogadoras = carregar_dados(DATA_FILE, [])
if "presencas" not in st.session_state: st.session_state.presencas = carregar_dados(PRESENCAS_FILE, [])
if "conteudos" not in st.session_state: st.session_state.conteudos = carregar_dados(CONTEUDOS_FILE, {
    "regulamento": "Regra principal: respeito acima de tudo.",
    "aniversariantes": "Parabéns às aniversariantes do mês!",
    "financeiro_msg": "Faça seu pagamento via Pix."
})
if "pagina_atual" not in st.session_state: st.session_state.pagina_atual = "dashboard"
if "usuario_logado" not in st.session_state: st.session_state.usuario_logado = "Admin"
if "perfil_logado" not in st.session_state: st.session_state.perfil_logado = "Admin"

# -----------------------------------------------------------------------------
# INTERFACE PRINCIPAL
# -----------------------------------------------------------------------------
# Coluna centralizada (90%) para manter o alinhamento
_, col_master, _ = st.columns([0.5, 9, 0.5])

with col_master:
    st.markdown("<div style='text-align: center;'><h2>⚽ PELADINHA FC</h2></div>", unsafe_allow_html=True)
    
    if st.session_state.pagina_atual != "dashboard":
        if st.button("⬅️ Voltar"): st.session_state.pagina_atual = "dashboard"; st.rerun()

    # --- DASHBOARD ---
    if st.session_state.pagina_atual == "dashboard":
        if st.button("📜 Regulamento"): st.session_state.pagina_atual = "regulamento"; st.rerun()
        if st.button("🎂 Aniversariantes"): st.session_state.pagina_atual = "aniversariantes"; st.rerun()
        if st.button("🛠️ Gerenciamento"): st.session_state.pagina_atual = "gerenciamento"; st.rerun()

    # --- PÁGINAS DINÂMICAS ---
    elif st.session_state.pagina_atual == "regulamento":
        st.markdown(f"<div class='card-team'>{st.session_state.conteudos['regulamento']}</div>", unsafe_allow_html=True)

    elif st.session_state.pagina_atual == "aniversariantes":
        st.markdown(f"<div class='card-team'>{st.session_state.conteudos['aniversariantes']}</div>", unsafe_allow_html=True)

    # --- GERENCIAMENTO (EDITÁVEL) ---
    elif st.session_state.pagina_atual == "gerenciamento":
        st.subheader("🛠️ Editar Conteúdo dos Cards")
        with st.form("edit_conteudos"):
            st.session_state.conteudos['regulamento'] = st.text_area("Texto do Regulamento", value=st.session_state.conteudos['regulamento'])
            st.session_state.conteudos['aniversariantes'] = st.text_area("Texto Aniversariantes", value=st.session_state.conteudos['aniversariantes'])
            
            if st.form_submit_button("Salvar Alterações"):
                salvar_dados(CONTEUDOS_FILE, st.session_state.conteudos)
                st.success("Cards atualizados com sucesso!")
                st.rerun()
