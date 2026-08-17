import streamlit as st
import pandas as pd
import json
import os
import random
from datetime import datetime, timedelta, timezone
from urllib.parse import quote
from PIL import Image

# -----------------------------------------------------------------------------
# CONFIGURAÇÃO DE FUSO HORÁRIO E DATAS
# -----------------------------------------------------------------------------
fuso_br = timezone(timedelta(hours=-3))
hoje_dt = datetime.now(fuso_br)

# -----------------------------------------------------------------------------
# CONFIGURAÇÃO DA PÁGINA
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Peladinha FC | Mais que Futebol, Uma Conexão",
    page_icon="⚽",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# -----------------------------------------------------------------------------
# ESTILIZAÇÃO CSS CUSTOMIZADA (Corrigido o contraste dos Inputs de Texto)
# -----------------------------------------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;500;600;700;800;900&display=swap');
    
    html, body, [class*="css"] { font-family: 'Montserrat', sans-serif; color: #F3F4F6; }
    .stApp { background-color: #0B0F19; color: #F3F4F6; }
    
    .card-team {
        background: #161E2E !important;
        border: 1px solid #374151 !important;
        border-left: 5px solid #EC4899 !important;
        border-radius: 14px;
        padding: 18px;
        margin-bottom: 16px;
        color: #FFFFFF !important;
        box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.3);
    }
    
    /* Correção do fundo e cor dos campos de texto (Text Area / Text Input) para evitar tarja em branco */
    div.stTextArea textarea, div.stTextInput input {
        background-color: #0F172A !important;
        color: #FFFFFF !important;
        border: 1px solid #374151 !important;
        border-radius: 8px !important;
    }
    
    div.stButton > button:first-child {
        background: linear-gradient(135deg, #EC4899 0%, #DB2777 100%) !important;
        color: #FFFFFF !important;
        font-weight: 800 !important;
        border-radius: 12px !important;
        border: none !important;
        padding: 14px 20px !important;
        width: 100%;
        box-shadow: 0px 4px 12px rgba(236, 72, 153, 0.3);
        transition: 0.3s ease;
    }
    
    div.stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0px 6px 15px rgba(236, 72, 153, 0.5);
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# PERSISTÊNCIA DE DADOS (JSON)
# -----------------------------------------------------------------------------
DATA_FILE, PRESENCAS_FILE = "jogadoras.json", "presencas.json"
ADMINS_FILE, FINANCE_FILE = "administradores.json", "financeiro.json"
AVISOS_FILE, COMPROVANTES_FILE = "avisos.json", "comprovantes.json"
SORTEIO_FILE, CONTEUDOS_FILE = "sorteio.json", "conteudos.json"
UPLOAD_DIR, LOGO_FILE = "comprovantes_imgs", "logo_peladinha.png"

# CHAVE SECRETA DE SEGURANÇA PARA CRIAR ADMINS
CHAVE_MESTRE_ADMIN = "PeladinhaMaster2026@"

if not os.path.exists(UPLOAD_DIR): 
    os.makedirs(UPLOAD_DIR)

def carregar_dados(f, default):
    if os.path.exists(f):
        try:
            with open(f, "r", encoding="utf-8") as file: 
                return json.load(file)
        except: 
            return default
    return default

def salvar_dados(f, data):
    with open(f, "w", encoding="utf-8") as file: 
        json.dump(data, file, ensure_ascii=False, indent=4)

def file_to_base64(path):
    import base64
    with open(path, "rb") as f: 
        return base64.b64encode(f.read()).decode("utf-8")

# -----------------------------------------------------------------------------
# INICIALIZAÇÃO SESSION STATE
# -----------------------------------------------------------------------------
if "jogadoras" not in st.session_state: 
    st.session_state.jogadoras = carregar_dados(DATA_FILE, [])
if "presencas" not in st.session_state: 
    st.session_state.presencas = carregar_dados(PRESENCAS_FILE, [])
if "administradores" not in st.session_state: 
    st.session_state.administradores = carregar_dados(ADMINS_FILE, [{"nome": "Admin Principal", "login": "admin", "senha": "1980", "perfil": "Admin"}])
if "avisos" not in st.session_state: 
    st.session_state.avisos = carregar_dados(AVISOS_FILE, {"limite_vagas": 15, "pix": "peladinhafc@email.com", "vencimento": "Todo dia 10", "valor_mensalidade": 50.0, "valor_avulso": 15.0})
if "conteudos" not in st.session_state: 
    st.session_state.conteudos = carregar_dados(CONTEUDOS_FILE, {
        "regulamento": "Regulamento Oficial: Respeito mútuo, pontualidade nos horários dos jogos e pagamento da mensalidade em dia.",
        "aniversariantes": "Parabéns a todas as craques aniversariantes deste mês! Muitas felicidades e gols!",
        "dashboard_info": "Bem-vinda ao sistema oficial da nossa Peladinha FC. Selecione uma opção abaixo para navegar."
    })
if "pagina_atual" not in st.session_state: 
    st.session_state.pagina_atual = "login"
if "sub_tela_login" not in st.session_state: 
    st.session_state.sub_tela_login = "menu"
if "usuario_logado" not in st.session_state: 
    st.session_state.usuario_logado = None
if "perfil_logado" not in st.session_state: 
    st.session_state.perfil_logado = None
if "editando_card" not in st.session_state: 
    st.session_state.editando_card = None

# -----------------------------------------------------------------------------
# FUNÇÃO PARA EXIBIR A LOGO CENTRALIZADA
# -----------------------------------------------------------------------------
def exibir_topo_logo():
    if os.path.exists(LOGO_FILE):
        st.markdown(f"""<div style="text-align: center; margin-bottom: 20px;"><img src="data:image/png;base64,{file_to_base64(LOGO_FILE)}" style="width: 180px; opacity: 0.9; border-radius: 16px; box-shadow: 0px 4px 15px rgba(0,0,0,0.4);" /></div>""", unsafe_allow_html=True)
    else:
        st.markdown("<h1 style='text-align: center; color: #EC4899;'>⚽ PELADINHA FC</h1>", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# FLUXO DE TELA DE LOGIN E CADASTRO SEGURO
# -----------------------------------------------------------------------------
if st.session_state.pagina_atual == "login":
    exibir_topo_logo()
    _, col_login, _ = st.columns([1, 4, 1])
    with col_login:
        if st.session_state.sub_tela_login == "menu":
            st.markdown("<h3 style='text-align: center;'>Acesse sua Conta</h3>", unsafe_allow_html=True)
            if st.button("🔐 ENTRAR NO SISTEMA"): 
                st.session_state.sub_tela_login = "entrar"
                st.rerun()
            if st.button("📝 CADASTRAR COMO ATLETA"): 
                st.session_state.sub_tela_login = "cad_atleta"
                st.rerun()
            if st.button("🛡️ CADASTRAR COMO ADMIN / DEV (RESTRITO)"): 
                st.session_state.sub_tela_login = "cad_admin"
                st.rerun()
                
        elif st.session_state.sub_tela_login == "entrar":
            st.markdown("<h3 style='text-align: center;'>Login</h3>", unsafe_allow_html=True)
            with st.form("form_login"):
                u_input = st.text_input("Usuário ou Nome")
                p_input = st.text_input("Senha", type="password")
                btn_sub = st.form_submit_button("ACESSAR")
                
                if btn_sub:
                    admin_encontrado = next((a for a in st.session_state.administradores if a["login"].lower() == u_input.lower() and a["senha"] == p_input), None)
                    if admin_encontrado or (u_input.lower() == "admin" and p_input == "1980"):
                        st.session_state.usuario_logado = admin_encontrado["nome"] if admin_encontrado else "Administrador"
                        st.session_state.perfil_logado = admin_encontrado.get("perfil", "Admin") if admin_encontrado else "Admin"
                        st.session_state.pagina_atual = "dashboard"
                        st.rerun()
                    else:
                        atleta_encontrada = next((j for j in st.session_state.jogadoras if j["nome"].lower() == u_input.lower()), None)
                        if atleta_encontrada:
                            st.session_state.usuario_logado = atleta_encontrada["nome"]
                            st.session_state.perfil_logado = "Atleta"
                            st.session_state.pagina_atual = "dashboard"
                            st.rerun()
                        else:
                            st.error("Usuário ou senha inválidos!")
                            
            if st.button("⬅️ Voltar"):
                st.session_state.sub_tela_login = "menu"
                st.rerun()

        elif st.session_state.sub_tela_login == "cad_atleta":
            st.markdown("<h3 style='text-align: center;'>Cadastro de Atleta</h3>", unsafe_allow_html=True)
            with st.form("form_cad_atleta"):
                nome_atleta = st.text_input("Nome Completo")
                cel_atleta = st.text_input("Celular (WhatsApp)")
                pos_atleta = st.selectbox("Posição Principal", ["Linha", "Goleira"])
                btn_cad = st.form_submit_button("CADASTRAR ATLETA")
                
                if btn_cad:
                    if nome_atleta.strip():
                        nova_j = {"nome": nome_atleta, "celular": cel_atleta, "posicao": pos_atleta, "status": "Ativo"}
                        st.session_state.jogadoras.append(nova_j)
                        salvar_dados(DATA_FILE, st.session_state.jogadoras)
                        st.success("Cadastro realizado com sucesso! Faça login.")
                        st.session_state.sub_tela_login = "menu"
                        st.rerun()
                    else:
                        st.error("Preencha o nome corretamente.")
            if st.button("⬅️ Voltar"):
                st.session_state.sub_tela_login = "menu"
                st.rerun()

        elif st.session_state.sub_tela_login == "cad_admin":
            st.markdown("<h3 style='text-align: center;'>Cadastro Seguro Admin / Dev</h3>", unsafe_allow_html=True)
            st.info("⚠️ Este cadastro exige uma chave mestra de segurança fornecida apenas aos criadores do sistema.")
            with st.form("form_cad_admin"):
                nome_adm = st.text_input("Nome do Administrador")
                login_adm = st.text_input("Login de Acesso")
                senha_adm = st.text_input("Senha", type="password")
                perfil_escolhido = st.selectbox("Nível de Perfil", ["Admin", "Dev"])
                chave_secreta = st.text_input("Chave Mestra de Segurança", type="password")
                btn_cad_adm = st.form_submit_button("CADASTRAR ADMIN")
                
                if btn_cad_adm:
                    if chave_secreta == CHAVE_MESTRE_ADMIN:
                        if nome_adm.strip() and login_adm.strip() and senha_adm.strip():
                            novo_adm = {"nome": nome_adm, "login": login_adm, "senha": senha_adm, "perfil": perfil_escolhido}
                            st.session_state.administradores.append(novo_adm)
                            salvar_dados(ADMINS_FILE, st.session_state.administradores)
                            st.success("Administrador cadastrado com sucesso! Volte e faça login.")
                            st.session_state.sub_tela_login = "menu"
                            st.rerun()
                        else:
                            st.error("Preencha todos os campos obrigatórios.")
                    else:
                        st.error("Chave mestra incorreta! Acesso negado para criação de administradores.")
            if st.button("⬅️ Voltar"):
                st.session_state.sub_tela_login = "menu"
                st.rerun()

# -----------------------------------------------------------------------------
# PAINEL PRINCIPAL (DASHBOARD E TELAS COM COLUNA MESTRA CENTRALIZADA)
# -----------------------------------------------------------------------------
else:
    exibir_topo_logo()
    
    _, col_master, _ = st.columns([0.5, 9, 0.5])
    
    with col_master:
        st.markdown(f"<p style='text-align: center; color: #9CA3AF; font-size: 0.9rem;'>Logado como: <b>{st.session_state.usuario_logado}</b> ({st.session_state.perfil_logado})</p>", unsafe_allow_html=True)
        st.markdown("---")

        if st.session_state.pagina_atual != "dashboard":
            if st.button("⬅️ Voltar ao Menu Principal"):
                st.session_state.pagina_atual = "dashboard"
                st.session_state.editando_card = None
                st.rerun()
            st.markdown("---")

        # --- MENU / DASHBOARD ---
        if st.session_state.pagina_atual == "dashboard":
            if st.session_state.perfil_logado in ["Admin", "Dev"]:
                if st.session_state.editando_card == "dashboard_info":
                    with st.form("form_edit_dash"):
                        novo_texto_dash = st.text_area("Editar Mensagem de Boas-Vindas", value=st.session_state.conteudos['dashboard_info'])
                        if st.form_submit_button("💾 Salvar Alteração"):
                            st.session_state.conteudos['dashboard_info'] = novo_texto_dash
                            salvar_dados(CONTEUDOS_FILE, st.session_state.conteudos)
                            st.session_state.editando_card = None
                            st.success("Card atualizado!")
                            st.rerun()
                    if st.button("❌ Cancelar Edição"):
                        st.session_state.editando_card = None
                        st.rerun()
                else:
                    st.markdown(f"<div class='card-team' style='text-align: center;'>{st.session_state.conteudos['dashboard_info']}</div>", unsafe_allow_html=True)
                    if st.button("✏️ Editar este Card (Boas-Vindas)"):
                        st.session_state.editando_card = "dashboard_info"
                        st.rerun()
            else:
                st.markdown(f"<div class='card-team' style='text-align: center;'>{st.session_state.conteudos['dashboard_info']}</div>", unsafe_allow_html=True)
            
            if st.button("📌 Lista de Presença"):
                st.session_state.pagina_atual = "lista"
                st.rerun()
            if st.button("📜 Regulamento Interno"):
                st.session_state.pagina_atual = "regulamento"
                st.rerun()
            if st.button("🎂 Aniversariantes do Mês"):
                st.session_state.pagina_atual = "aniversariantes"
                st.rerun()
            if st.button("⚽ Sorteio de Times"):
                st.session_state.pagina_atual = "sorteio"
                st.rerun()
                    
            if st.button("🚪 Sair / Trocar Conta"):
                st.session_state.pagina_atual = "login"
                st.session_state.sub_tela_login = "menu"
                st.session_state.usuario_logado = None
                st.session_state.perfil_logado = None
                st.session_state.editando_card = None
                st.rerun()

        # --- LISTA DE PRESENÇA ---
        elif st.session_state.pagina_atual == "lista":
            st.subheader("📌 Confirmação de Presença")
            atativas_nomes = [j["nome"] for j in st.session_state.jogadoras if j.get("status") == "Ativo"]
            if atativas_nomes:
                atleta_selecionada = st.selectbox("Selecione sua Atleta", atativas_nomes)
                if st.button("Confirmar Presença na Próxima Pelada"):
                    st.success(f"Presença confirmada para {atleta_selecionada}!")
            else:
                st.warning("Nenhuma atleta cadastrada ou ativa no momento.")

        # --- REGULAMENTO ---
        elif st.session_state.pagina_atual == "regulamento":
            st.subheader("📜 Regulamento")
            
            if st.session_state.perfil_logado in ["Admin", "Dev"] and st.session_state.editando_card == "regulamento":
                with st.form("form_edit_reg"):
                    novo_reg = st.text_area("Editar Regulamento", value=st.session_state.conteudos['regulamento'], height=150)
                    if st.form_submit_button("💾 Salvar Regulamento"):
                        st.session_state.conteudos['regulamento'] = novo_reg
                        salvar_dados(CONTEUDOS_FILE, st.session_state.conteudos)
                        st.session_state.editando_card = None
                        st.success("Regulamento atualizado com sucesso!")
                        st.rerun()
                if st.button("❌ Cancelar Edição"):
                    st.session_state.editando_card = None
                    st.rerun()
            else:
                st.markdown(f"<div class='card-team'>{st.session_state.conteudos['regulamento']}</div>", unsafe_allow_html=True)
                if st.session_state.perfil_logado in ["Admin", "Dev"]:
                    if st.button("✏️ Editar este Card (Regulamento)"):
                        st.session_state.editando_card = "regulamento"
                        st.rerun()

        # --- ANIVERSARIANTES ---
        elif st.session_state.pagina_atual == "aniversariantes":
            st.subheader("🎂 Aniversariantes do Mês")
            
            if st.session_state.perfil_logado in ["Admin", "Dev"] and st.session_state.editando_card == "aniversariantes":
                with st.form("form_edit_aniv"):
                    novo_aniv = st.text_area("Editar Aniversariantes", value=st.session_state.conteudos['aniversariantes'], height=120)
                    if st.form_submit_button("💾 Salvar Aniversariantes"):
                        st.session_state.conteudos['aniversariantes'] = novo_aniv
                        salvar_dados(CONTEUDOS_FILE, st.session_state.conteudos)
                        st.session_state.editando_card = None
                        st.success("Card de aniversariantes atualizado!")
                        st.rerun()
                if st.button("❌ Cancelar Edição"):
                    st.session_state.editando_card = None
                    st.rerun()
            else:
                st.markdown(f"<div class='card-team'>{st.session_state.conteudos['aniversariantes']}</div>", unsafe_allow_html=True)
                if st.session_state.perfil_logado in ["Admin", "Dev"]:
                    if st.button("✏️ Editar este Card (Aniversariantes)"):
                        st.session_state.editando_card = "aniversariantes"
                        st.rerun()

        # --- SORTEIO DE TIMES ---
        elif st.session_state.pagina_atual == "sorteio":
            st.subheader("⚽ Sorteio de Times")
            st.markdown("<div class='card-team'>Ferramenta de divisão automática de equipes equilibradas para a partida.</div>", unsafe_allow_html=True)
