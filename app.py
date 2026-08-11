import streamlit as st
import pandas as pd
import json
import os
import random
from datetime import datetime, timedelta, timezone

# -----------------------------------------------------------------------------
# CONFIGURAÇÃO DE FUSO HORÁRIO E DATAS
# -----------------------------------------------------------------------------
fuso_br = timezone(timedelta(hours=-3))
hoje_dt = datetime.now(fuso_br)
data_hoje_id = hoje_dt.strftime("%Y-%m-%d")

# -----------------------------------------------------------------------------
# CONFIGURAÇÃO DA PÁGINA (TEMA ESCURO)
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Peladinha FC | Gestão Inteligente",
    page_icon="⚽",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# -----------------------------------------------------------------------------
# ESTILIZAÇÃO CSS CUSTOMIZADA
# -----------------------------------------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] { 
        font-family: 'Montserrat', sans-serif; 
        color: #F3F4F6;
    }

    .stApp {
        background-color: #111827;
        color: #F3F4F6;
    }

    .stTextInput label, .stSelectbox label, .stNumberInput label, .stFileUploader label, p, span, label {
        color: #FFFFFF !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
    }

    .app-header {
        background: #1F2937;
        padding: 20px;
        border-radius: 16px;
        margin-bottom: 20px;
        border: 1px solid #374151;
        box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.3);
    }
    .app-title {
        font-size: 1.8rem;
        font-weight: 700;
        color: #FFFFFF;
        margin: 0;
    }
    .app-subtitle {
        font-size: 0.85rem;
        color: #D1D5DB;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    .card-team {
        background: #1F2937;
        border: 1px solid #374151;
        border-top: 4px solid #881337;
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 15px;
        color: #FFFFFF;
    }

    div.stButton > button:first-child {
        background-color: #881337 !important;
        color: #FFFFFF !important;
        font-weight: 700 !important;
        border-radius: 10px !important;
        border: 1px solid #9F1239 !important;
        padding: 15px 20px !important;
        box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.2);
        width: 100%;
    }
    div.stButton > button:first-child:hover {
        background-color: #9F1239 !important;
        border-color: #BE123C !important;
    }

    .stTextInput input, .stSelectbox select, .stNumberInput input {
        background-color: #374151 !important;
        color: #FFFFFF !important;
        border: 1px solid #4B5563 !important;
        border-radius: 8px !important;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# ARQUIVOS JSON E PERSISTÊNCIA INTELIGENTE
# -----------------------------------------------------------------------------
DATA_FILE = "jogadoras.json"
PRESENCAS_FILE = "presencas.json"
AVISOS_FILE = "avisos.json"
FINANCE_FILE = "financeiro.json"
ADMINS_FILE = "administradores.json"
REGULAMENTO_FILE = "regulamento.json"
SORTEIO_FILE = "sorteio.json"
COMPROVANTES_FILE = "comprovantes.json"
UPLOAD_DIR = "comprovantes_imgs"

if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

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

def obter_nome_p(p):
    return p["nome"] if isinstance(p, dict) else p

def obter_hora_p(p):
    return p.get("hora", "") if isinstance(p, dict) else ""

def obter_tipo_p(p):
    return p.get("tipo", "Avulso") if isinstance(p, dict) else "Avulso"

# -----------------------------------------------------------------------------
# INICIALIZAÇÃO DO SESSION STATE
# -----------------------------------------------------------------------------
if "jogadoras" not in st.session_state:
    st.session_state.jogadoras = carregar_dados(DATA_FILE, [])
if "presencas" not in st.session_state:
    st.session_state.presencas = carregar_dados(PRESENCAS_FILE, [])
if "financeiro" not in st.session_state:
    st.session_state.financeiro = carregar_dados(FINANCE_FILE, [
        {"mes": "Janeiro/2026", "tipo": "Receita", "descricao": "Mensalidades", "valor": 300.00},
        {"mes": "Janeiro/2026", "tipo": "Despesa", "descricao": "Aluguel da Quadra", "valor": 200.00}
    ])
if "comprovantes" not in st.session_state:
    st.session_state.comprovantes = carregar_dados(COMPROVANTES_FILE, [])
if "administradores" not in st.session_state:
    st.session_state.administradores = carregar_dados(ADMINS_FILE, [{"nome": "Admin Principal", "login": "admin", "senha": "1980"}])
if "avisos" not in st.session_state:
    st.session_state.avisos = carregar_dados(AVISOS_FILE, {"vencimento": "Todo dia 10", "pix": "peladinhafc@email.com", "limite_vagas": 15})
if "regulamento" not in st.session_state:
    st.session_state.regulamento = carregar_dados(REGULAMENTO_FILE, [
        {"topico": "📌 1. Prioridade de Mensalistas", "regrinha": "Mensalistas confirmando até as 17:00 de segunda-feira têm prioridade nas 15 vagas."},
        {"topico": "⏳ 2. Fila de Espera de Avulsas", "regrinha": "Avulsas entram na fila de espera. Após as 17:00, se sobrarem vagas, sobem automaticamente."},
        {"topico": "⏰ 3. Fechamento da Lista", "regrinha": "A lista fecha rigidamente às 18:00 de toda segunda-feira."},
        {"topico": "🤝 4. Boa Convivência", "regrinha": "Respeito mútuo em campo e fora dele é obrigatório para todas as atletas."}
    ])
if "sorteio_oficial" not in st.session_state:
    st.session_state.sorteio_oficial = carregar_dados(SORTEIO_FILE, {})

if "pagina_atual" not in st.session_state:
    st.session_state.pagina_atual = "login"
if "usuario_logado" not in st.session_state:
    st.session_state.usuario_logado = None
if "perfil_logado" not in st.session_state:
    st.session_state.perfil_logado = None

if "versao_dados_cache" not in st.session_state:
    st.session_state.versao_dados_cache = str(len(st.session_state.presencas)) + "_" + str(len(st.session_state.jogadoras))

SENHA_MESTRE_DEV = "1980"
CODIGO_CONVITE_ADMIN = "PELADA2026"  # Senha secreta para liberar cadastro de administradores

# -----------------------------------------------------------------------------
# BOTÃO DE ATUALIZAÇÃO MANUAL INTELIGENTE (BARRA LATERAL)
# -----------------------------------------------------------------------------
with st.sidebar:
    st.write("### 🔄 Sincronização")
    if st.button("Verificar Atualizações", use_container_width=True):
        disk_presencas = carregar_dados(PRESENCAS_FILE, [])
        disk_jogadoras = carregar_dados(DATA_FILE, [])
        nova_versao = str(len(disk_presencas)) + "_" + str(len(disk_jogadoras))
        
        if nova_versao != st.session_state.versao_dados_cache:
            st.session_state.presencas = disk_presencas
            st.session_state.jogadoras = disk_jogadoras
            st.session_state.versao_dados_cache = nova_versao
            st.success("Novas atualizações encontradas e carregadas!")
            st.rerun()
        else:
            st.info("Nenhuma alteração nova nos dados.")

# -----------------------------------------------------------------------------
# TELA DE LOGIN / CADASTRO / DEV
# -----------------------------------------------------------------------------
if st.session_state.pagina_atual == "login":
    st.markdown("""
    <div class='app-header' style='text-align: center;'>
        <div class='app-subtitle'>peladinha fc</div>
        <div class='app-title'>⚽ Gestão Inteligente & Resenha</div>
    </div>
    """, unsafe_allow_html=True)

    tab_entrar, tab_cad_jogadora, tab_cad_admin, tab_dev = st.tabs(["🔑 Entrar", "📝 Criar Conta", "👑 Criar Conta Admin", "⚙️ Desenvolvedor"])

    with tab_entrar:
        st.subheader("Entrar no Sistema")
        with st.form("form_login_geral"):
            l_user = st.text_input("Usuário / Login", key="log_user")
            l_pass = st.text_input("Senha", type="password", key="log_pass")
            if st.form_submit_button("ENTRAR"):
                admin_encontrado = next((adm for adm in st.session_state.administradores if adm.get("login") == l_user and adm.get("senha") == l_pass), None)
                if admin_encontrado:
                    st.session_state.usuario_logado = admin_encontrado["nome"]
                    st.session_state.perfil_logado = "Admin"
                    st.session_state.pagina_atual = "dashboard"
                    st.rerun()
                else:
                    user_found = next((j for j in st.session_state.jogadoras if j.get("login") == l_user and j.get("senha") == l_pass), None)
                    if user_found:
                        if user_found.get("status") == "Pendente":
                            st.warning("Seu cadastro ainda aguarda aprovação de um Administrador.")
                        else:
                            st.session_state.usuario_logado = user_found["nome"]
                            st.session_state.perfil_logado = "Jogadora"
                            st.session_state.pagina_atual = "dashboard"
                            st.rerun()
                    else:
                        st.error("Usuário ou senha incorretos!")

    with tab_cad_jogadora:
        st.subheader("Cadastro de Nova Atleta")
        with st.form("form_cad_jog", clear_on_submit=True):
            c_nome = st.text_input("Seu Nome Completo *")
            c_nasc = st.text_input("Nascimento (DD/MM) *", placeholder="Ex: 15/05")
            c_tipo = st.selectbox("Tipo:", ["Avulso", "Mensalista"])
            c_user = st.text_input("Login *")
            c_pass = st.text_input("Senha *", type="password")
            if st.form_submit_button("CADASTRAR ATLETA"):
                if c_nome and c_user and c_pass:
                    if any(j.get("login") == c_user.strip() for j in st.session_state.jogadoras):
                        st.error("Este login já está em uso!")
                    else:
                        st.session_state.jogadoras.append({
                            "nome": c_nome.strip(), "nascimento": c_nasc.strip(),
                            "login": c_user.strip(), "senha": c_pass.strip(),
                            "tipo": c_tipo, "status": "Pendente", "quitado": "Não"
                        })
                        salvar_dados(DATA_FILE, st.session_state.jogadoras)
                        st.success("Cadastro realizado com sucesso! O Administrador recebeu sua solicitação.")
                else:
                    st.error("Preencha todos os campos obrigatórios!")

    with tab_cad_admin:
        st.subheader("Criar Conta Administradora")
        st.info("ℹ️ Para criar um acesso de administrador, é obrigatório informar o Código de Convite fornecido pela organização.")
        with st.form("form_cad_adm", clear_on_submit=True):
            a_nome = st.text_input("Nome do Administrador *")
            a_user = st.text_input("Login Admin *")
            a_pass = st.text_input("Senha Admin *", type="password")
            a_codigo = st.text_input("Código de Convite Secreto *", type="password")
            if st.form_submit_button("CADASTRAR ADMIN"):
                if a_nome and a_user and a_pass and a_codigo:
                    if a_codigo != CODIGO_CONVITE_ADMIN:
                        st.error("Código de convite inválido! Acesso negado para criação de administrador.")
                    elif any(adm.get("login") == a_user.strip() for adm in st.session_state.administradores):
                        st.error("Login de admin já existe!")
                    else:
                        st.session_state.administradores.append({
                            "nome": a_nome.strip(), "login": a_user.strip(), "senha": a_pass.strip()
                        })
                        salvar_dados(ADMINS_FILE, st.session_state.administradores)
                        st.success("Administrador cadastrado com sucesso! Já pode fazer login na aba 'Entrar'.")
                else:
                    st.error("Preencha todos os campos, incluindo o código de convite!")

    with tab_dev:
        st.subheader("Acesso Restrito ao Desenvolvedor")
        with st.form("form_dev_login"):
            d_pass = st.text_input("Senha Mestre do Desenvolvedor", type="password")
            if st.form_submit_button("ENTRAR COMO DEV"):
                if d_pass == SENHA_MESTRE_DEV:
                    st.session_state.usuario_logado = "Desenvolvedor"
                    st.session_state.perfil_logado = "Dev"
                    st.session_state.pagina_atual = "dashboard"
                    st.rerun()
                else:
                    st.error("Senha mestre incorreta!")

# -----------------------------------------------------------------------------
# PAINEL PRINCIPAL (DASHBOARD E TELAS)
# -----------------------------------------------------------------------------
else:
    st.markdown(f"""
    <div class='app-header'>
        <div class='app-subtitle'>peladinha fc — Olá, <b>{st.session_state.usuario_logado}</b> ({st.session_state.perfil_logado})</div>
        <div class='app-title'>Painel de Gestão</div>
    </div>
    """, unsafe_allow_html=True)

    if st.session_state.pagina_atual != "dashboard":
        if st.button("⬅️ Voltar ao Menu Principal"):
            st.session_state.pagina_atual = "dashboard"
            st.rerun()
        st.markdown("---")

    if st.session_state.pagina_atual == "dashboard":
        cards = [
            ("📜 Regulamento", "regulamento"),
            ("📌 Lista de Presença", "lista"),
            ("🔀 Sorteio de Times", "sorteio"),
            ("📋 Elenco de Jogadoras", "elenco"),
            ("💸 Pagamento Pix", "pagamento")
        ]

        if st.session_state.perfil_logado in ["Admin", "Dev"]:
            cards.append(("📊 Fluxo de Caixa", "caixa"))
            cards.append(("🛠️ Gerenciamento Geral", "gerenciamento"))

        cols = st.columns(2)
        for i, (titulo, rota) in enumerate(cards):
            with cols[i % 2]:
                if st.button(titulo, use_container_width=True):
                    st.session_state.pagina_atual = rota
                    st.rerun()

        st.markdown("---")
        if st.button("🚪 Sair da Conta", use_container_width=True):
            st.session_state.usuario_logado = None
            st.session_state.perfil_logado = None
            st.session_state.pagina_atual = "login"
            st.rerun()

    elif st.session_state.pagina_atual == "regulamento":
        st.subheader("📜 Regulamento Interno & Boa Convivência")
        for reg in st.session_state.regulamento:
            st.markdown(f"<div class='card-team'><h4 style='color: #F43F5E;'>{reg['topico']}</h4><p>{reg['regrinha']}</p></div>", unsafe_allow_html=True)

    elif st.session_state.pagina_atual == "lista":
        st.subheader("📌 Lista de Presença e Confirmações")
        limite = st.session_state.avisos.get("limite_vagas", 15)
        
        lista_atual = sorted(st.session_state.presencas, key=lambda x: x.get("dt_confirmacao", x.get("hora", "")))
        
        mensalistas = []
        avulsas = []
        
        for p in lista_atual:
            tipo = obter_tipo_p(p)
            dt_conf_str = p.get("dt_confirmacao", "")
            atrasada_mensalista = False
            if dt_conf_str:
                try:
                    dt_obj = datetime.fromisoformat(dt_conf_str)
                    if dt_obj.weekday() == 0 and dt_obj.hour >= 17:
                        atrasada_mensalista = True
                except:
                    pass
                    
            if tipo == "Mensalista" and not atrasada_mensalista:
                mensalistas.append(p)
            else:
                avulsas.append(p)
            
        confirmadas = mensalistas[:limite]
        espera = mensalistas[limite:] + avulsas

        col_l1, col_l2 = st.columns(2)
        with col_l1:
            st.write(f"### 🟢 Confirmadas ({len(confirmadas)}/{limite})")
            if not confirmadas:
                st.info("Nenhuma atleta confirmada.")
            for i, p in enumerate(confirmadas, 1):
                st.markdown(f"<div class='card-team'><b>{i}.</b> {obter_nome_p(p)} `[{obter_tipo_p(p)}]` — <i>{obter_hora_p(p)}</i></div>", unsafe_allow_html=True)

            st.write(f"### ⏳ Fila de Espera ({len(espera)})")
            if not espera:
                st.info("Fila de espera vazia.")
            for i, p in enumerate(espera, 1):
                st.markdown(f"<div class='card-team'><b>{i}º:</b> {obter_nome_p(p)} `[{obter_tipo_p(p)}]`</div>", unsafe_allow_html=True)

        with col_l2:
            if st.session_state.perfil_logado in ["Admin", "Dev"]:
                st.write("### 👑 Ações do Administrador")
                
                with st.form("form_add_manual"):
                    st.write("<b>Adicionar Atleta do Elenco</b>", unsafe_allow_html=True)
                    atativas_nomes = [j["nome"] for j in st.session_state.jogadoras if j.get("status") == "Ativo"]
                    atleta_escolhida = st.selectbox("Selecione a Atleta", atativas_nomes if atativas_nomes else ["Nenhuma cadastrada"])
                    if st.form_submit_button("Incluir do Elenco"):
                        if atativas_nomes and not any(obter_nome_p(p) == atleta_escolhida for p in st.session_state.presencas):
                            dados_j = next((j for j in st.session_state.jogadoras if j["nome"] == atleta_escolhida), None)
                            st.session_state.presencas.append({
                                "nome": atleta_escolhida, "hora": hoje_dt.strftime("%H:%M"),
                                "tipo": dados_j.get("tipo", "Avulso") if dados_j else "Avulso",
                                "dt_confirmacao": hoje_dt.isoformat()
                            })
                            salvar_dados(PRESENCAS_FILE, st.session_state.presencas)
                            st.success(f"{atleta_escolhida} incluída com sucesso!")
                            st.rerun()

                with st.form("form_add_externa"):
                    st.write("<b>Adicionar Convidada / Avulsa (Sem Cadastro)</b>", unsafe_allow_html=True)
                    nome_externa = st.text_input("Nome da Convidada")
                    tipo_externa = st.selectbox("Tipo da Convidada", ["Avulso", "Mensalista"], key="tipo_ext")
                    if st.form_submit_button("Incluir Convidada"):
                        if nome_externa.strip():
                            if not any(obter_nome_p(p) == nome_externa.strip() for p in st.session_state.presencas):
                                st.session_state.presencas.append({
                                    "nome": nome_externa.strip(), "hora": hoje_dt.strftime("%H:%M"),
                                    "tipo": tipo_externa, "dt_confirmacao": hoje_dt.isoformat()
                                })
                                salvar_dados(PRESENCAS_FILE, st.session_state.presencas)
                                st.success(f"Convidada {nome_externa.strip()} incluída!")
                                st.rerun()
                            else:
                                st.error("Esta atleta já está na lista.")
                        else
