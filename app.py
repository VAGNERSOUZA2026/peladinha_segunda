import streamlit as st
import pandas as pd
import json
import os
import random
from datetime import datetime, timedelta, timezone
from urllib.parse import quote
from PIL import Image

# -----------------------------------------------------------------------------
# CONFIGURAÃ‡ÃƒO DE FUSO HORÃRIO E DATAS
# -----------------------------------------------------------------------------
fuso_br = timezone(timedelta(hours=-3))
hoje_dt = datetime.now(fuso_br)
data_hoje_id = hoje_dt.strftime("%Y-%m-%d")

# -----------------------------------------------------------------------------
# CONFIGURAÃ‡ÃƒO DA PÃGINA
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Peladinha FC | Mais que Futebol, Uma ConexÃ£o",
    page_icon="âš½",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# -----------------------------------------------------------------------------
# ESTILIZAÃ‡ÃƒO CSS CUSTOMIZADA
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

    /* CartÃµes de ConteÃºdo e Menu Mobile Style */
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

    /* BotÃµes Principais Rosa Pink */
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

    /* Inputs e FormulÃ¡rios */
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
# ARQUIVOS JSON E PERSISTÃŠNCIA
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
# INICIALIZAÃ‡ÃƒO DO SESSION STATE
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
        {"topico": "ðŸ“Œ 1. Prioridade de Mensalistas", "regrinha": "Mensalistas confirmando atÃ© as 17:00 de segunda-feira tÃªm prioridade nas 15 vagas."},
        {"topico": "â³ 2. Fila de Espera de Avulsas", "regrinha": "Avulsas entram na fila de espera. ApÃ³s as 17:00, se sobrarem vagas, sobem automaticamente."},
        {"topico": "â° 3. Fechamento da Lista", "regrinha": "A lista fecha rigidamente Ã s 18:00 de toda segunda-feira."},
        {"topico": "ðŸ¤ 4. Boa ConvivÃªncia", "regrinha": "Respeito mÃºtuo em campo e fora dele Ã© obrigatÃ³rio para todas as atletas."}
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

def obter_senha_dev():
    try:
        senha = st.secrets.get("DEV_PASSWORD")
        if senha:
            return str(senha)
    except Exception:
        pass
    # Fallback apenas para desenvolvimento local. Em produÃ§Ã£o, configure
    # [DEV_PASSWORD] no .streamlit/secrets.toml.
    return os.getenv("DEV_PASSWORD", "")

SENHA_MESTRE_DEV = obter_senha_dev()

# -----------------------------------------------------------------------------
# FUNÃ‡ÃƒO PARA EXIBIR A LOGO NO TOPO (COM EFEITO TRANSLÃšCIDO)
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
        
        # OpÃ§Ã£o de alterar/enviar logo visÃ­vel EXCLUSIVAMENTE para o Desenvolvedor
        if st.session_state.perfil_logado == "Dev":
            with st.expander("âš™ï¸ [DEV] Alterar/Enviar Logo"):
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
    st.markdown("<p style='text-align: center; color: #9CA3AF; margin-bottom: 25px;'>Mais que Futebol, Uma ConexÃ£o!</p>", unsafe_allow_html=True)

    if st.session_state.sub_tela_login != "menu":
        if st.button("â¬…ï¸ Voltar ao Menu Inicial"):
            st.session_state.sub_tela_login = "menu"
            st.rerun()
        st.markdown("---")

    if st.session_state.sub_tela_login == "menu":
        # Apenas os botÃµes-card diretos, sem texto redundante separado
        if st.button("ðŸ”‘ ENTRAR NO SISTEMA", key="btn_card_entrar"):
            st.session_state.sub_tela_login = "entrar"
            st.rerun()

        if st.button("ðŸ“ CADASTRAR COMO ATLETA", key="btn_card_atleta"):
            st.session_state.sub_tela_login = "cad_atleta"
            st.rerun()

        if st.button("âš™ï¸ ÃREA DO DESENVOLVEDOR", key="btn_card_dev"):
            st.session_state.sub_tela_login = "dev"
            st.rerun()

    elif st.session_state.sub_tela_login == "entrar":
        st.subheader("Entrar no Sistema")
        with st.form("form_login_geral"):
            l_user = st.text_input("UsuÃ¡rio / Login", key="log_user")
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
                            st.warning("Seu cadastro ainda aguarda aprovaÃ§Ã£o de um Administrador.")
                        else:
                            st.session_state.usuario_logado = user_found["nome"]
                            st.session_state.perfil_logado = "Jogadora"
                            st.session_state.pagina_atual = "dashboard"
                            st.rerun()
                    else:
                        st.error("UsuÃ¡rio ou senha incorretos!")

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
                        st.error("Este login jÃ¡ estÃ¡ em uso!")
                    else:
                        st.session_state.jogadoras.append({
                            "nome": c_nome.strip(), "nascimento": c_nasc.strip(),
                            "login": c_user.strip(), "senha": c_pass.strip(),
                            "tipo": c_tipo, "status": "Pendente", "quitado": "NÃ£o"
                        })
                        salvar_dados(DATA_FILE, st.session_state.jogadoras)
                        st.success("Cadastro realizado com sucesso! Aguardando aprovaÃ§Ã£o de um Administrador.")
                        
                        st.markdown("---")
                        st.write("ðŸ“± **Aviso importante:** Para agilizar sua aprovaÃ§Ã£o, clique abaixo para avisar um dos administradores via WhatsApp:")
                        for adm in st.session_state.administradores:
                            cel_adm = adm.get("celular", "").strip()
                            if cel_adm:
                                msg = f"OlÃ¡ {adm['nome']}! Acabei de me cadastrar no Peladinha FC como {c_tipo} (UsuÃ¡rio: {c_user.strip()}). Pode aprovar meu cadastro por favor?"
                                link_zap = f"https://wa.me/{cel_adm}?text={quote(msg)}"
                                st.markdown(f"ðŸ‘‰ [Avisar Admin {adm['nome']} no WhatsApp]({link_zap})", unsafe_allow_html=True)
                else:
                    st.error("Preencha todos os campos obrigatÃ³rios!")

    elif st.session_state.sub_tela_login == "cad_admin":
        st.subheader("ðŸ“ Solicitar Acesso de Administrador")
        st.info(
            "O cadastro nÃ£o cria uma conta administrativa imediatamente. "
            "Sua solicitaÃ§Ã£o serÃ¡ enviada para anÃ¡lise do Desenvolvedor."
        )
        with st.form("form_solicitacao_admin", clear_on_submit=True):
            a_nome = st.text_input("Nome do solicitante *")
            a_cel = st.text_input("Celular / WhatsApp *", placeholder="Ex: 5531999999999")
            a_user = st.text_input("Login desejado *")
            a_pass = st.text_input("Senha desejada *", type="password")
            if st.form_submit_button("ENVIAR SOLICITAÃ‡ÃƒO"):
                nome = a_nome.strip()
                celular = a_cel.strip()
                login = a_user.strip()
                senha = a_pass.strip()

                if not all([nome, celular, login, senha]):
                    st.error("Preencha todos os campos obrigatÃ³rios!")
                elif len(senha) < 8:
                    st.error("A senha deve ter pelo menos 8 caracteres.")
                elif any(adm.get("login", "").lower() == login.lower()
                         for adm in st.session_state.administradores):
                    st.error("Este login jÃ¡ pertence a um administrador.")
                elif any(req.get("login", "").lower() == login.lower()
                         and req.get("status") == "Pendente"
                         for req in st.session_state.solicitacoes_admin):
                    st.error("JÃ¡ existe uma solicitaÃ§Ã£o pendente para este login.")
                else:
                    st.session_state.solicitacoes_admin.append({
                        "nome": nome,
                        "login": login,
                        "senha": senha,
                        "celular": celular,
                        "data_solicitacao": hoje_dt.isoformat(),
                        "status": "Pendente"
                    })
                    salvar_dados(ADMIN_REQUESTS_FILE, st.session_state.solicitacoes_admin)
                    st.success(
                        "SolicitaÃ§Ã£o enviada com sucesso! "
                        "A conta somente serÃ¡ criada apÃ³s aprovaÃ§Ã£o do Desenvolvedor."
                    )

    elif st.session_state.sub_tela_login == "dev":
        st.subheader("Acesso Restrito ao Desenvolvedor")
        if not SENHA_MESTRE_DEV:
            st.error(
                "A senha do Desenvolvedor nÃ£o estÃ¡ configurada. "
                "Configure DEV_PASSWORD no Streamlit Secrets antes de entrar."
            )
        with st.form("form_dev_login"):
            d_pass = st.text_input("Senha Mestre do Desenvolvedor", type="password")
            if st.form_submit_button("ENTRAR COMO DEV"):
                if SENHA_MESTRE_DEV and d_pass == SENHA_MESTRE_DEV:
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
        if st.button("â¬…ï¸ Voltar ao Menu Principal"):
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
                    <h3>ðŸŽ‰ PARABÃ‰NS PELO SEU ANIVERSÃRIO! ðŸŽ‚</h3>
                    <p>Desejamos a vocÃª um feliz aniversÃ¡rio, muita saÃºde, felicidades e muitos gols! ðŸ¥³âš½</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                lista_str = ", ".join(nomes_aniv)
                st.markdown(f"""
                <div class='card-team' style='text-align: center;'>
                    <h3>ðŸŽˆ Aniversariantes do MÃªs ðŸŽˆ</h3>
                    <p>Atletas comemorando nova idade este mÃªs: <b>{lista_str}</b>. NÃ£o deixe de parabenizÃ¡-las! ðŸ¥³âš½</p>
                </div>
                """, unsafe_allow_html=True)

        cards = [
            ("ðŸ“œ Regulamento", "regulamento"),
            ("ðŸ“Œ Lista de PresenÃ§a", "lista"),
            ("ðŸ”€ Sorteio de Times", "sorteio"),
            ("ðŸ“‹ Elenco de Jogadoras", "elenco"),
            ("ðŸ’¸ Pagamento Pix", "pagamento"),
            ("ðŸŽ‚ Aniversariantes do MÃªs", "aniversariantes")
        ]

        if st.session_state.perfil_logado in ["Admin", "Dev"]:
            cards.append(("ðŸ“Š Fluxo de Caixa", "caixa"))
            cards.append(("ðŸ› ï¸ Gerenciamento Geral", "gerenciamento"))

        cols = st.columns(2)
        for i, (titulo, rota) in enumerate(cards):
            with cols[i % 2]:
                if st.button(titulo, use_container_width=True):
                    st.session_state.pagina_atual = rota
                    st.rerun()

        st.markdown("---")
        if st.button("ðŸšª Sair da Conta", use_container_width=True):
            st.session_state.usuario_logado = None
            st.session_state.perfil_logado = None
            st.session_state.sub_tela_login = "menu"
            st.session_state.pagina_atual = "login"
            st.rerun()

    elif st.session_state.pagina_atual == "regulamento":
        st.subheader("ðŸ“œ Regulamento Interno & Boa ConvivÃªncia")
        for reg in st.session_state.regulamento:
            st.markdown(f"<div class='card-team'><h4>{reg['topico']}</h4><p>{reg['regrinha']}</p></div>", unsafe_allow_html=True)

    elif st.session_state.pagina_atual == "aniversariantes":
        st.subheader("ðŸŽ‚ Painel de Aniversariantes do MÃªs")
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
            st.info("Nenhuma atleta faz aniversÃ¡rio neste mÃªs.")
        else:
            for a in aniversariantes_mes:
                st.markdown(f"""
                <div class='card-team'>
                    <h3>ðŸŽ‰ {a['nome']}</h3>
                    <p>Data de AniversÃ¡rio: <b>{a.get('nascimento')}</b> | Tipo: <code>{a.get('tipo', 'Avulso')}</code></p>
                </div>
                """, unsafe_allow_html=True)

    elif st.session_state.pagina_atual == "lista":
        st.subheader("ðŸ“Œ Lista de PresenÃ§a e ConfirmaÃ§Ãµes")
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
            st.write(f"### ðŸŸ¢ Confirmadas ({len(confirmadas)}/{limite})")
            if not confirmadas:
                st.info("Nenhuma atleta confirmada.")
            for i, p in enumerate(confirmadas, 1):
                st.markdown(f"<div class='card-team'><b>{i}.</b> {obter_nome_p(p)} `[{obter_tipo_p(p)}]` â€” <i>{obter_hora_p(p)}</i></div>", unsafe_allow_html=True)

            st.write(f"### â³ Fila de Espera ({len(espera)})")
            if not espera:
                st.info("Fila de espera vazia.")
            for i, p in enumerate(espera, 1):
                st.markdown(f"<div class='card-team'><b>{i}Âº:</b> {obter_nome_p(p)} `[{obter_tipo_p(p)}]`</div>", unsafe_allow_html=True)

        with col_l2:
            if st.session_state.perfil_logado in ["Admin", "Dev"]:
                st.write("### ðŸ‘‘ AÃ§Ãµes do Administrador")
                
                with st.form("form_add_manual"):
                    st.write("<b>Adicionar Atleta do Elenco</b>", unsafe_allow_html=True)
                    atativas_nomes = [j["nome"] for j in st.session_state.jogadoras if j.get("status") == "Ativo"]
                    atleta_escolhida = st.selectbox("Selecione a Atleta", atativas_nomes if atativas_nomes else ["Nenhuma cadastradas"])
                    if st.form_submit_button("Incluir do Elenco"):
                        if atativas_nomes and not any(obter_nome_p(p) == atleta_escolhida for p in st.session_state.presencas):
                            dados_j = next((j for j in st.session_state.jogadoras if j["nome"] == atleta_escolhida), None)
                            st.session_state.presencas.append({
                                "nome": atleta_escolhida, "hora": hoje_dt.strftime("%H:%M"),
                                "tipo": dados_j.get("tipo", "Avulso") if dados_j else "Avulso",
                                "dt_confirmacao": hoje_dt.isoformat()
                            })
                            salvar_dados(PRESENCAS_FILE, st.session_state.presencas)
                            st.success(f"{atleta_escolhida} incluÃ­da com sucesso!")
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
                                st.success(f"Convidada {nome_externa.strip()} incluÃ­da!")
                                st.rerun()
                            else:
                                st.error("Esta atleta jÃ¡ estÃ¡ na lista.")
                        else:
                            st.error("Informe o nome da convidada.")

                st.write("### Remover da Lista:")
                for p in st.session_state.presencas:
                    c_nome = obter_nome_p(p)
                    if st.button(f"Remover {c_nome}", key=f"rem_l_{c_nome}"):
                        st.session_state.presencas = [item for item in st.session_state.presencas if obter_nome_p(item) != c_nome]
                        salvar_dados(PRESENCAS_FILE, st.session_state.presencas)
                        st.rerun()
            else:
                st.write("### âœï¸ Gerenciar Minha PresenÃ§a")
                if st.session_state.perfil_logado == "Jogadora":
                    j_nome = st.session_state.usuario_logado
                    dados_j = next((j for j in st.session_state.jogadoras if j["nome"] == j_nome), None)
                    tipo_j = dados_j.get("tipo", "Avulso") if dados_j else "Avulso"
                    
                    pos_conf = next((idx + 1 for idx, p in enumerate(confirmadas) if obter_nome_p(p) == j_nome), None)
                    pos_esp = next((idx + 1 for idx, p in enumerate(espera) if obter_nome_p(p) == j_nome), None)
                    
                    if pos_conf:
                        st.success(f"ðŸŽ‰ VocÃª estÃ¡ na **Lista Principal** na posiÃ§Ã£o **{pos_conf}**!")
                    elif pos_esp:
                        st.warning(f"â³ VocÃª estÃ¡ na **Fila de Espera** na posiÃ§Ã£o **{pos_esp}Âº**.")
                    else:
                        st.info("â„¹ï¸ VocÃª nÃ£o estÃ¡ confirmada.")

                    with st.form("form_pres"):
                        c_ok = st.form_submit_button("ðŸ‘ Confirmar PresenÃ§a", use_container_width=True)
                        c_canc = st.form_submit_button("âŒ Cancelar PresenÃ§a", use_container_width=True)

                    ja_na_lista = (pos_conf is not None or pos_esp is not None)

                    if c_ok:
                        if ja_na_lista:
                            st.warning("âš ï¸ VocÃª jÃ¡ estÃ¡ confirmada na lista! Sua posiÃ§Ã£o e horÃ¡rio foram preservados.")
                        else:
                            st.session_state.presencas.append({
                                "nome": j_nome, "hora": hoje_dt.strftime("%H:%M"),
                                "tipo": tipo_j, "dt_confirmacao": hoje_dt.isoformat()
                            })
                            salvar_dados(PRESENCAS_FILE, st.session_state.presencas)
                            st.success("PresenÃ§a confirmada com sucesso!")
                            st.rerun()

                    if c_canc:
                        if ja_na_lista:
                            st.session_state.presencas = [item for item in st.session_state.presencas if obter_nome_p(item) != j_nome]
                            salvar_dados(PRESENCAS_FILE, st.session_state.presencas)
                            st.info("PresenÃ§a cancelada com sucesso!")
                            st.rerun()
                        else:
                            st.error("Seu nome nÃ£o estÃ¡ na lista.")

    elif st.session_state.pagina_atual == "sorteio":
        st.subheader("ðŸ”€ Sorteio de Times (Oficial & Paralelo)")
        sorteio_salvo = st.session_state.sorteio_oficial
        
        if sorteio_salvo and "times" in sorteio_salvo:
            st.write("#### ðŸ† Sorteio Oficial")
            for nome_time, membros in sorteio_salvo["times"].items():
                st.markdown(f"<div class='card-team'><h3>âš½ {nome_time}</h3>", unsafe_allow_html=True)
                for item in membros:
                    st.markdown(f"â€¢ **{item}**")
                st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.info("Nenhum sorteio oficial gerado ainda.")

        st.markdown("#### âš¡ Sorteio Paralelo (Baseado em PresenÃ§a no Local)")
        if st.button("Gerar Sorteio Paralelo Agora", use_container_width=True):
            confirmadas_nomes = [obter_nome_p(p) for p in st.session_state.presencas]
            if len(confirmadas_nomes) >= 2:
                random.shuffle(confirmadas_nomes)
                res_paralelo = {"Time A": confirmadas_nomes[::2], "Time B": confirmadas_nomes[1::2]}
                st.success("Sorteio Paralelo Gerado com Sucesso!")
                for nome_t, membros_t in res_paralelo.items():
                    st.markdown(f"<div class='card-team'><b>{nome_t}:</b> {', '.join(membros_t)}</div>", unsafe_allow_html=True)
            else:
                st.error("Atletas insuficientes para gerar o sorteio paralelo.")

    elif st.session_state.pagina_atual == "elenco":
        st.subheader("ðŸ“‹ Elenco de Atletas Cadastradas")
        for j in st.session_state.jogadoras:
            if j.get("status") == "Ativo":
                st.markdown(f"<div class='card-team'><b>âš½ {j['nome']}</b><br><small>Tipo: `{j.get('tipo', 'Avulso')}` | Quitado: `{j.get('quitado', 'NÃ£o')}` | Nasc: {j.get('nascimento')}</small></div>", unsafe_allow_html=True)

    elif st.session_state.pagina_atual == "pagamento":
        st.subheader("ðŸ’¸ Pagamentos e Chave Pix")
        v_mensal = st.session_state.avisos.get('valor_mensalidade', 50.00)
        v_avulso = st.session_state.avisos.get('valor_avulso', 15.00)
        
        st.markdown(f"""
        <div class='card-team'>
            ðŸ“Œ <b>Chave Pix Oficial:</b> <code>{st.session_state.avisos.get('pix', 'peladinhafc@email.com')}</code><br><br>
            ðŸ“… Vencimento: <b>{st.session_state.avisos.get('vencimento', 'Todo dia 10')}</b><br>
            ðŸ’µ <b>Valores:</b> Mensalidade: <b>R$ {v_mensal:.2f}</b> | Avulsa: <b>R$ {v_avulso:.2f}</b>
        </div>
        """, unsafe_allow_html=True)
        
        if st.session_state.perfil_logado == "Jogadora":
            st.write("### Enviar Comprovante de Pagamento")
            with st.form("form_comprovante_envio", clear_on_submit=True):
                arquivo_submetido = st.file_uploader("Selecione a imagem do comprovante", type=["png", "jpg", "jpeg"])
                if st.form_submit_button("Enviar Comprovante"):
                    if arquivo_submetido:
                        caminho_arquivo = os.path.join(UPLOAD_DIR, f"{st.session_state.usuario_logado}_{int(datetime.now().timestamp())}.png")
                        with open(caminho_arquivo, "wb") as f:
                            f.write(arquivo_submetido.getbuffer())
                        
                        st.session_state.comprovantes.append({
                            "nome": st.session_state.usuario_logado,
                            "arquivo": caminho_arquivo,
                            "data": hoje_dt.strftime("%d/%m/%Y"),
                            "conferido": False
                        })
                        salvar_dados(COMPROVANTES_FILE, st.session_state.comprovantes)
                        st.success("Comprovante enviado com sucesso para validaÃ§Ã£o do Administrador!")
                    else:
                        st.error("Selecione um arquivo de imagem.")

        if st.session_state.perfil_logado in ["Admin", "Dev"]:
            st.write("### ðŸ‘‘ ConferÃªncia de Comprovantes Pendentes")
            comprovantes = st.session_state.comprovantes
            pendentes_comp = [c for c in comprovantes if not c.get("conferido", False)]
            if not pendentes_comp:
                st.info("Nenhum comprovante pendente para conferÃªncia.")
            for idx, comp in enumerate(comprovantes):
                if not comp.get("conferido", False):
                    st.markdown(f"<div class='card-team'><b>Atleta:</b> {comp['nome']} | <b>Data:</b> {comp['data']}</div>", unsafe_allow_html=True)
                    if os.path.exists(comp['arquivo']):
                        st.image(comp['arquivo'], width=300)
                    if st.button(f"Validar Pagamento de {comp['nome']}", key=f"val_comp_{idx}"):
                        comp["conferido"] = True
                        
                        j_cad = next((j for j in st.session_state.jogadoras if j["nome"] == comp["nome"]), None)
                        tipo_j_cad = j_cad.get("tipo", "Avulso") if j_cad else "Avulso"
                        
                        v_recebido = st.session_state.avisos.get('valor_mensalidade', 50.00) if tipo_j_cad == "Mensalista" else st.session_state.avisos.get('valor_avulso', 15.00)
                        
                        for j in st.session_state.jogadoras:
                            if j["nome"] == comp["nome"]:
                                j["quitado"] = "Sim"
                        salvar_dados(DATA_FILE, st.session_state.jogadoras)
                        
                        st.session_state.financeiro.append({
                            "mes": hoje_dt.strftime("%B/%Y"), "tipo": "Receita", "descricao": f"Pagamento ({tipo_j_cad}) - {comp['nome']}", "valor": float(v_recebido)
                        })
                        salvar_dados(FINANCE_FILE, st.session_state.financeiro)
                        salvar_dados(COMPROVANTES_FILE, comprovantes)
                        st.success("Pagamento validado e adicionado automaticamente como receita no fluxo de caixa!")
                        st.rerun()

    elif st.session_state.pagina_atual == "caixa":
        st.subheader("ðŸ“Š Fluxo de Caixa Completo")
        
        with st.form("form_lanca_caixa", clear_on_submit=True):
            st.write("<b>LanÃ§ar Nova Receita ou Despesa Manualmente</b>", unsafe_allow_html=True)
            c_mes = st.text_input("MÃªs / Ano (Ex: Janeiro/2026)", value=hoje_dt.strftime("%B/%Y"))
            c_tipo_fin = st.selectbox("Tipo", ["Receita", "Despesa"])
            c_desc = st.text_input("DescriÃ§Ã£o (Ex: Compra de Coletes, Aluguel)")
            c_valor = st.number_input("Valor (R$)", min_value=0.0, step=10.0)
            if st.form_submit_button("Adicionar LanÃ§amento"):
                if c_desc.strip() and c_valor > 0:
                    st.session_state.financeiro.append({
                        "mes": c_mes.strip(), "tipo": c_tipo_fin, "descricao": c_desc.strip(), "valor": float(c_valor)
                    })
                    salvar_dados(FINANCE_FILE, st.session_state.financeiro)
                    st.success("LanÃ§amento adicionado com sucesso!")
                    st.rerun()
                else:
                    st.error("Preencha a descriÃ§Ã£o e informe um valor vÃ¡lido.")

        st.markdown("---")
        
        registros_caixa = st.session_state.financeiro
        if not registros_caixa:
            st.info("Nenhum registro financeiro encontrado.")
        else:
            total_geral_rec = sum(item["valor"] for item in registros_caixa if item["tipo"] == "Receita")
            total_geral_desp = sum(item["valor"] for item in registros_caixa if item["tipo"] == "Despesa")
            saldo_total = total_geral_rec - total_geral_desp

            st.markdown(f"""
            <div class='card-team'>
                <h3>ðŸ’° Saldo Total em Caixa: R$ {saldo_total:.2f}</h3>
                <p>ðŸŸ¢ Total de Receitas: R$ {total_geral_rec:.2f} | ðŸ”´ Total de Despesas: R$ {total_geral_desp:.2f}</p>
            </div>
            """, unsafe_allow_html=True)

            st.write("### HistÃ³rico de MovimentaÃ§Ãµes & ExclusÃ£o")
            for idx, item in enumerate(registros_caixa):
                col_c1, col_c2 = st.columns([4, 1])
                with col_c1:
                    st.markdown(f"""
                    <div class='card-team' style='margin-bottom: 5px;'>
                        <b>MÃªs:</b> {item.get('mes', 'Geral')} | <b>Tipo:</b> <code>{item['tipo']}</code> | <b>DescriÃ§Ã£o:</b> {item['descricao']} | <b>Valor:</b> R$ {item['valor']:.2f}
                    </div>
                    """, unsafe_allow_html=True)
                with col_c2:
                    if st.button("ðŸ—‘ï¸ Excluir", key=f"del_fin_{idx}"):
                        st.session_state.financeiro.pop(idx)
                        salvar_dados(FINANCE_FILE, st.session_state.financeiro)
                        st.success("LanÃ§amento excluÃ­do com sucesso!")
                        st.rerun()

    elif st.session_state.pagina_atual == "gerenciamento":
        st.subheader("ðŸ› ï¸ Painel de Gerenciamento Geral & AprovaÃ§Ãµes")
        
        tab_ger1, tab_ger2, tab_ger3 = st.tabs(["ðŸ“ Aprovar Cadastros", "âš™ï¸ ConfiguraÃ§Ãµes Gerais", "ðŸ”’ GestÃ£o de Contas (Dev)"])

        with tab_ger1:
            st.write("### AprovaÃ§Ã£o de Novas Atletas")
            pendentes = [j for j in st.session_state.jogadoras if j.get("status") == "Pendente"]
            if not pendentes:
                st.info("Nenhum cadastro pendente no momento.")
            for idx, j in enumerate(pendentes):
                col_p1, col_p2, col_p3 = st.columns([2, 1, 1])
                with col_p1:
                    st.write(f"**{j['nome']}** (`{j.get('tipo', 'Avulso')}`) - Nasc: {j.get('nascimento')}")
                with col_p2:
                    if st.button("âœ… Aprovar", key=f"aprov_{idx}"):
                        j["status"] = "Ativo"
                        salvar_dados(DATA_FILE, st.session_state.jogadoras)
                        st.success(f"âœ”ï¸ ConfirmaÃ§Ã£o: A atleta {j['nome']} foi aprovada e ativada com sucesso!")
                        st.rerun()
                with col_p3:
                    if st.button("âŒ Recusar", key=f"rec_{idx}"):
                        st.session_state.jogadoras.remove(j)
                        salvar_dados(DATA_FILE, st.session_state.jogadoras)
                        st.warning(f"âš ï¸ O cadastro de {j['nome']} foi recusado/removido.")
                        st.rerun()

        with tab_ger2:
            with st.form("form_cfg_geral_painel"):
                st.write("<b>ConfiguraÃ§Ãµes Gerais e Valores</b>", unsafe_allow_html=True)
                limite_v = st.number_input("Limite de Vagas", value=int(st.session_state.avisos.get("limite_vagas", 15)))
                pix_val = st.text_input("Chave Pix", value=st.session_state.avisos.get("pix", ""))
                venc_val = st.text_input("Dia/Regra de Vencimento", value=st.session_state.avisos.get("vencimento", "Todo dia 10"))
                val_mensal = st.number_input("Valor da Mensalidade (R$)", min_value=0.0, step=5.0, value=float(st.session_state.avisos.get("valor_mensalidade", 50.00)))
                val_avulso = st.number_input("Valor da DiÃ¡ria Avulsa (R$)", min_value=0.0, step=5.0, value=float(st.session_state.avisos.get("valor_avulso", 15.00)))
                
                if st.form_submit_button("Salvar Ajustes"):
                    st.session_state.avisos["limite_vagas"] = limite_v
                    st.session_state.avisos["pix"] = pix_val
                    st.session_state.avisos["vencimento"] = venc_val
                    st.session_state.avisos["valor_mensalidade"] = val_mensal
                    st.session_state.avisos["valor_avulso"] = val_avulso
                    salvar_dados(AVISOS_FILE, st.session_state.avisos)
                    st.success("ConfiguraÃ§Ãµes e valores atualizados com sucesso!")

        with tab_ger3:
            if st.session_state.perfil_logado == "Dev":
                st.write("### ðŸ”’ GestÃ£o Completa de Contas e Credenciais (Dev)")
                st.info("Somente o Desenvolvedor pode criar, aprovar, recusar ou excluir contas administrativas.")

                sub_tab_adm, sub_tab_jog, sub_tab_req = st.tabs(
                    ["ðŸ‘‘ Administradores", "âš½ Atletas / Jogadoras", "ðŸ“¨ SolicitaÃ§Ãµes de Admin"]
                )

                with sub_tab_adm:
                    st.write("#### Gerenciar Contas de Administradores & Celular WhatsApp")
                    for idx, adm in enumerate(st.session_state.administradores):
                        st.markdown(f"""
                        <div class='card-team'>
                            <b>Nome:</b> {adm['nome']} | <b>Login:</b> <code>{adm['login']}</code> | <b>Celular:</b> <code>{adm.get('celular', 'NÃ£o cadastrado')}</code>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        with st.form(f"form_alt_adm_{idx}"):
                            nova_cel_adm = st.text_input("Atualizar nÃºmero do Celular/WhatsApp (Ex: 5531999999999)", value=adm.get("celular", ""), key=f"cel_adm_{idx}")
                            nova_s_adm = st.text_input("Redefinir nova senha (opcional)", type="password", key=f"nova_s_adm_{idx}")
                            if st.form_submit_button("Salvar Dados do Admin"):
                                adm["celular"] = nova_cel_adm.strip()
                                if nova_s_adm.strip():
                                    adm["senha"] = nova_s_adm.strip()
                                salvar_dados(ADMINS_FILE, st.session_state.administradores)
                                st.success(f"Dados do admin {adm['nome']} atualizados com sucesso!")
                                st.rerun()

                        if st.button(f"Excluir Admin {adm['nome']}", key=f"del_adm_{idx}"):
                            if len(st.session_state.administradores) > 1:
                                st.session_state.administradores.pop(idx)
                                salvar_dados(ADMINS_FILE, st.session_state.administradores)
                                st.success("Administrador removido!")
                                st.rerun()
                            else:
                                st.error("VocÃª nÃ£o pode excluir o Ãºnico administrador do sistema.")

                with sub_tab_req:
                    st.write("#### ðŸ“¨ SolicitaÃ§Ãµes Pendentes de Administrador")
                    pendentes_admin = [
                        r for r in st.session_state.solicitacoes_admin
                        if r.get("status") == "Pendente"
                    ]

                    if not pendentes_admin:
                        st.info("Nenhuma solicitaÃ§Ã£o de administrador pendente.")
                    else:
                        for idx_req, req in enumerate(pendentes_admin):
                            st.markdown(
                                f"""
                                <div class='card-team'>
                                    <b>Nome:</b> {req.get('nome', '')}<br>
                                    <b>Login:</b> <code>{req.get('login', '')}</code><br>
                                    <b>Celular:</b> <code>{req.get('celular', '')}</code><br>
                                    <b>Solicitado em:</b> {req.get('data_solicitacao', '')}
                                </div>
                                """,
                                unsafe_allow_html=True
                            )

                            col_req1, col_req2 = st.columns(2)
                            with col_req1:
                                if st.button(
                                    "âœ… Aprovar",
                                    key=f"aprovar_req_admin_{idx_req}",
                                    use_container_width=True
                                ):
                                    login_req = req.get("login", "").strip()

                                    # RevalidaÃ§Ã£o antes da criaÃ§Ã£o da conta.
                                    if any(
                                        adm.get("login", "").lower() == login_req.lower()
                                        for adm in st.session_state.administradores
                                    ):
                                        st.error("O login jÃ¡ foi utilizado por outro administrador.")
                                    else:
                                        st.session_state.administradores.append({
                                            "nome": req.get("nome", "").strip(),
                                            "login": login_req,
                                            "senha": req.get("senha", ""),
                                            "celular": req.get("celular", "").strip()
                                        })
                                        req["status"] = "Aprovado"
                                        req["aprovado_em"] = hoje_dt.isoformat()
                                        salvar_dados(ADMINS_FILE, st.session_state.administradores)
                                        salvar_dados(
                                            ADMIN_REQUESTS_FILE,
                                            st.session_state.solicitacoes_admin
                                        )
                                        st.success(
                                            f"Administrador {req.get('nome')} aprovado com sucesso!"
                                        )
                                        st.rerun()

                            with col_req2:
                                if st.button(
                                    "âŒ Recusar",
                                    key=f"recusar_req_admin_{idx_req}",
                                    use_container_width=True
                                ):
                                    req["status"] = "Recusado"
                                    req["recusado_em"] = hoje_dt.isoformat()
                                    salvar_dados(
                                        ADMIN_REQUESTS_FILE,
                                        st.session_state.solicitacoes_admin
                                    )
                                    st.warning(
                                        f"SolicitaÃ§Ã£o de {req.get('nome')} recusada."
                                    )
                                    st.rerun()

                    st.markdown("---")
                    st.write("#### HistÃ³rico de SolicitaÃ§Ãµes")
                    historico_req = [
                        r for r in st.session_state.solicitacoes_admin
                        if r.get("status") != "Pendente"
                    ]
                    if historico_req:
                        for req in reversed(historico_req[-20:]):
                            st.markdown(
                                f"<div class='card-team'>"
                                f"<b>{req.get('nome', '')}</b> â€” "
                                f"<code>{req.get('login', '')}</code> â€” "
                                f"<b>Status:</b> {req.get('status', '')}"
                                f"</div>",
                                unsafe_allow_html=True
                            )
                    else:
                        st.info("Nenhuma solicitaÃ§Ã£o finalizada.")

                with sub_tab_jog:
                    st.write("#### Gerenciar Contas de Atletas / Jogadoras")
                    if not st.session_state.jogadoras:
                        st.info("Nenhuma atleta cadastrada.")
                    for idx_j, jog in enumerate(st.session_state.jogadoras):
                        st.markdown(f"""
                        <div class='card-team'>
                            <b>Atleta:</b> {jog['nome']} | <b>Login:</b> <code>{jog.get('login', 'N/D')}</code><br>
                            <small>Status: `{jog.get('status')}` | Tipo: `{jog.get('tipo')}`</small>
                        </div>
                        """, unsafe_allow_html=True)

                        with st.form(f"form_alt_senha_jog_{idx_j}"):
                            nova_s_jog = st.text_input("Redefinir nova senha para esta atleta", type="password", key=f"nova_s_jog_{idx_j}")
                            if st.form_submit_button("Atualizar Senha da Atleta"):
                                if nova_s_jog.strip():
                                    jog["senha"] = nova_s_jog.strip()
                                    salvar_dados(DATA_FILE, st.session_state.jogadoras)
                                    st.success(f"Senha da atleta {jog['nome']} alterada com sucesso!")
                                    st.rerun()
                                else:
                                    st.error("Digite uma nova senha vÃ¡lida.")

                        if st.button(f"Excluir Conta de {jog['nome']}", key=f"del_jog_{idx_j}"):
                            st.session_state.jogadoras.pop(idx_j)
                            salvar_dados(DATA_FILE, st.session_state.jogadoras)
                            st.warning(f"A atleta {jog['nome']} foi removida do sistema.")
                            st.rerun()
            else:
                st.warning("âš ï¸ Esta Ã¡rea Ã© restrita apenas ao perfil de Desenvolvedor.")
