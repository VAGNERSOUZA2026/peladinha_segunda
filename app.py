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
data_hoje_id = hoje_dt.strftime("%Y-%m-%d")

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
# ESTILIZAÇÃO CSS CUSTOMIZADA
# -----------------------------------------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;500;600;700;800;900&display=swap');
    
    html, body, [class*="css"] { 
        font-family: 'Montserrat', sans-serif; 
        color: #F3F4F6;
    }

    .stApp {
        background-color: #0B0F19;
        color: #F3F4F6;
    }

    .stTextInput label, .stSelectbox label, .stNumberInput label, .stFileUploader label, p, span, label {
        color: #FFFFFF !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
    }

    /* Cartões de Conteúdo e Menu Mobile Style */
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
    .card-team h3, .card-team h4, .card-team p, .card-team b, .card-team span, .card-team small {
        color: #FFFFFF !important;
    }
    .card-team code {
        background-color: #0B0F19 !important;
        color: #F472B6 !important;
        padding: 4px 8px !important;
        border-radius: 6px !important;
        font-weight: 700 !important;
    }

    /* Botões Principais Rosa Pink */
    div.stButton > button:first-child {
        background: linear-gradient(135deg, #EC4899 0%, #DB2777 100%) !important;
        color: #FFFFFF !important;
        font-weight: 800 !important;
        border-radius: 12px !important;
        border: none !important;
        padding: 14px 20px !important;
        box-shadow: 0px 6px 15px rgba(236, 72, 153, 0.4);
        width: 100%;
        transition: all 0.3s ease;
    }
    div.stButton > button:first-child:hover {
        background: linear-gradient(135deg, #DB2777 0%, #BE185D 100%) !important;
        box-shadow: 0px 8px 20px rgba(236, 72, 153, 0.6);
        transform: translateY(-2px);
    }

    /* Inputs e Formulários */
    .stTextInput input, .stSelectbox select, .stNumberInput input {
        background-color: #1F2937 !important;
        color: #FFFFFF !important;
        border: 1px solid #4B5563 !important;
        border-radius: 10px !important;
    }

    [data-testid="stFileUploader"] {
        background-color: #1F2937 !important;
        border: 2px dashed #4B5563 !important;
        border-radius: 12px !important;
        padding: 15px !important;
    }
    [data-testid="stFileUploader"] section {
        background-color: #1F2937 !important;
    }
    [data-testid="stFileUploader"] section div, [data-testid="stFileUploader"] span, [data-testid="stFileUploader"] small {
        color: #FFFFFF !important;
    }
    [data-testid="stFileUploader"] button {
        background: #EC4899 !important;
        color: #FFFFFF !important;
        border: none !important;
        font-weight: 700 !important;
        border-radius: 8px !important;
    }
    
    div.stFormSubmitButton > button:first-child {
        background: linear-gradient(135deg, #EC4899 0%, #DB2777 100%) !important;
        color: #FFFFFF !important;
        font-weight: 800 !important;
        border-radius: 12px !important;
        border: none !important;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# ARQUIVOS JSON E PERSISTÊNCIA
# -----------------------------------------------------------------------------
DATA_FILE = "jogadoras.json"
PRESENCAS_FILE = "presencas.json"
AVISOS_FILE = "avisos.json"
FINANCE_FILE = "financeiro.json"
ADMINS_FILE = "administradores.json"
ADMIN_REQUESTS_FILE = "solicitacoes_admin.json"
REGULAMENTO_FILE = "regulamento.json"
SORTEIO_FILE = "sorteio.json"
COMPROVANTES_FILE = "comprovantes.json"
UPLOAD_DIR = "comprovantes_imgs"
LOGO_FILE = "logo_peladinha.png"

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
    st.session_state.administradores = carregar_dados(
        ADMINS_FILE,
        [{"nome": "Admin Principal", "login": "admin", "senha": "1980", "celular": "5531999999999"}]
    )
if "solicitacoes_admin" not in st.session_state:
    st.session_state.solicitacoes_admin = carregar_dados(ADMIN_REQUESTS_FILE, [])
if "avisos" not in st.session_state:
    st.session_state.avisos = carregar_dados(AVISOS_FILE, {
        "vencimento": "Todo dia 10", 
        "pix": "peladinhafc@email.com", 
        "limite_vagas": 15,
        "valor_mensalidade": 50.00,
        "valor_avulso": 15.00
    })
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
if "sub_tela_login" not in st.session_state:
    st.session_state.sub_tela_login = "menu"
if "usuario_logado" not in st.session_state:
    st.session_state.usuario_logado = None
if "perfil_logado" not in st.session_state:
    st.session_state.perfil_logado = None

# Senha Mestra do Desenvolvedor atualizada para vivo6194
SENHA_MESTRE_DEV = "vivo6194"

# -----------------------------------------------------------------------------
# FUNÇÃO PARA EXIBIR A LOGO NO TOPO
# -----------------------------------------------------------------------------
def exibir_topo_logo():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if os.path.exists(LOGO_FILE):
            st.markdown(
                f"""
                <div style="text-align: center; margin-bottom: 10px;">
                    <img src="data:image/png;base64,{file_to_base64(LOGO_FILE)}" 
                         style="width: 100%; max-width: 220px; opacity: 0.45; border-radius: 12px; display: block; margin: 0 auto;" />
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            st.markdown("<h2 style='text-align: center; color: #EC4899; opacity: 0.5;'>PELADINHA FC</h2>", unsafe_allow_html=True)
        
        if st.session_state.perfil_logado == "Dev":
            with st.expander("⚙️ [DEV] Alterar/Enviar Logo"):
                upl_logo = st.file_uploader("Envie a nova imagem da Logo (.png ou .jpg)", type=["png", "jpg", "jpeg"], key="up_logo_topo")
                if upl_logo:
                    with open(LOGO_FILE, "wb") as f:
                        f.write(upl_logo.getbuffer())
                    st.success("Logo atualizada com sucesso! Recarregando...")
                    st.rerun()

def file_to_base64(file_path):
    import base64
    with open(file_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

# -----------------------------------------------------------------------------
# TELA DE LOGIN / CARDS ESTILO APP MOBILE
# -----------------------------------------------------------------------------
if st.session_state.pagina_atual == "login":
    exibir_topo_logo()
    st.markdown("<p style='text-align: center; color: #9CA3AF; margin-bottom: 25px;'>Mais que Futebol, Uma Conexão!</p>", unsafe_allow_html=True)

    if st.session_state.sub_tela_login != "menu":
        if st.button("⬅️ Voltar ao Menu Inicial"):
            st.session_state.sub_tela_login = "menu"
            st.rerun()
        st.markdown("---")

    if st.session_state.sub_tela_login == "menu":
        if st.button("🔑 ENTRAR NO SISTEMA", key="btn_card_entrar"):
            st.session_state.sub_tela_login = "entrar"
            st.rerun()

        if st.button("📋 CADASTRAR COMO ATLETA", key="btn_card_atleta"):
            st.session_state.sub_tela_login = "cad_atleta"
            st.rerun()

        if st.button("⚙️ ÁREA DO DESENVOLVEDOR", key="btn_card_dev"):
            st.session_state.sub_tela_login = "dev"
            st.rerun()

    elif st.session_state.sub_tela_login == "entrar":
        st.subheader("Entrar no Sistema")
        with st.form("form_login_geral"):
            l_user = st.text_input("Usuário / Login", key="log_user")
            l_pass = st.text_input("Senha", type="password", key="log_pass")
            if st.form_submit_button("ENTRAR"):
                admin_encontrado = next((adm for adm in st.session_state.administradores if adm.get("login") == l_user.strip() and adm.get("senha") == l_pass), None)
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

    elif st.session_state.sub_tela_login == "cad_atleta":
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
                        st.success("Cadastro realizado com sucesso! Aguardando aprovação de um Administrador.")
                        
                        st.markdown("---")
                        st.write("📱 **Aviso importante:** Para agilizar sua aprovação, clique abaixo para avisar um dos administradores via WhatsApp:")
                        for adm in st.session_state.administradores:
                            cel_adm = adm.get("celular", "").strip()
                            if cel_adm:
                                msg = f"Olá {adm['nome']}! Acabei de me cadastrar no Peladinha FC como {c_tipo} (Usuário: {c_user.strip()}). Pode aprovar meu cadastro por favor?"
                                link_zap = f"https://wa.me/{cel_adm}?text={quote(msg)}"
                                st.markdown(f"👉 [Avisar Admin {adm['nome']} no WhatsApp]({link_zap})", unsafe_allow_html=True)
                else:
                    st.error("Preencha todos os campos obrigatórios!")

    elif st.session_state.sub_tela_login == "dev":
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
    exibir_topo_logo()
    st.markdown(f"<p style='text-align: center; color: #9CA3AF; font-size: 0.9rem;'>Logado como: <b>{st.session_state.usuario_logado}</b> ({st.session_state.perfil_logado})</p>", unsafe_allow_html=True)
    st.markdown("---")

    if st.session_state.pagina_atual != "dashboard":
        if st.button("⬅️ Voltar ao Menu Principal"):
            st.session_state.pagina_atual = "dashboard"
            st.rerun()
        st.markdown("---")

    if st.session_state.pagina_atual == "dashboard":
        mes_atual = hoje_dt.month
        aniversariantes_mes = []
        for j in st.session_state.jogadoras:
            nasc_str = j.get("nascimento", "")
            if nasc_str and "/" in nasc_str:
                try:
                    partes = nasc_str.split("/")
                    mes_nasc = int(partes[1])
                    if mes_nasc == mes_atual:
                        aniversariantes_mes.append(j)
                except:
                    pass

        if aniversariantes_mes:
            nomes_aniv = [a["nome"] for a in aniversariantes_mes]
            usuario_atual = st.session_state.usuario_logado
            aniversariante_logada = next((a for a in aniversariantes_mes if a["nome"] == usuario_atual), None)
            
            if aniversariante_logada:
                st.markdown(f"""
                <div class='card-team' style='text-align: center;'>
                    <h3>🎉 PARABÉNS PELO SEU ANIVERSÁRIO! 🎂</h3>
                    <p>Desejamos a você um feliz aniversário, muita saúde, felicidades e muitos gols! 🥳⚽</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                lista_str = ", ".join(nomes_aniv)
                st.markdown(f"""
                <div class='card-team' style='text-align: center;'>
                    <h3>🎈 Aniversariantes do Mês 🎈</h3>
                    <p>Atletas comemorando nova idade este mês: <b>{lista_str}</b>. Não deixe de parabenizá-las! 🥳⚽</p>
                </div>
                """, unsafe_allow_html=True)

        cards = [
            ("📄 Regulamento", "regulamento"),
            ("📋 Lista de Presença", "lista"),
            ("🔀 Sorteio de Times", "sorteio"),
            ("📁 Elenco de Jogadoras", "elenco"),
            ("💳 Pagamento Pix", "pagamento"),
            ("🎂 Aniversariantes do Mês", "aniversariantes")
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
            st.session_state.sub_tela_login = "menu"
            st.session_state.pagina_atual = "login"
            st.rerun()

    elif st.session_state.pagina_atual == "regulamento":
        st.subheader("📄 Regulamento Interno & Boa Convivência")
        for reg in st.session_state.regulamento:
            st.markdown(f"<div class='card-team'><h4>{reg['topico']}</h4><p>{reg['regrinha']}</p></div>", unsafe_allow_html=True)

    elif st.session_state.pagina_atual == "aniversariantes":
        st.subheader("🎂 Painel de Aniversariantes do Mês")
        mes_atual = hoje_dt.month
        aniversariantes_mes = []
        for j in st.session_state.jogadoras:
            nasc_str = j.get("nascimento", "")
            if nasc_str and "/" in nasc_str:
                try:
                    partes = nasc_str.split("/")
                    mes_nasc = int(partes[1])
                    if mes_nasc == mes_atual:
                        aniversariantes_mes.append(j)
                except:
                    pass
        
        if not aniversariantes_mes:
            st.info("Nenhuma atleta faz aniversário neste mês.")
        else:
            for a in aniversariantes_mes:
                st.markdown(f"""
                <div class='card-team'>
                    <h3>🎉 {a['nome']}</h3>
                    <p>D
