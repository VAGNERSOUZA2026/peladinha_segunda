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

# -----------------------------------------------------------------------------
# CONFIGURAÇÃO DA PÁGINA
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Peladinha FC",
    page_icon="⚽",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# -----------------------------------------------------------------------------
# ESTILIZAÇÃO CSS CUSTOMIZADA (VISUAL NEON ROSA / DARK)
# -----------------------------------------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] { 
        font-family: 'Montserrat', sans-serif; 
        color: #F3F4F6; 
    }
    
    .stApp { 
        background-color: #080C14;
        background-image: radial-gradient(#EC4899 0.75px, transparent 0.75px), radial-gradient(#EC4899 0.75px, #080C14 0.75px);
        background-size: 30px 30px;
        background-position: 0 0, 15px 15px;
        background-opacity: 0.05;
    }

    /* Ocultar elementos nativos desnecessários */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Estilização Geral de Cartões */
    .card-team {
        background: rgba(22, 30, 46, 0.85);
        border: 1px solid #374151;
        border-radius: 14px;
        padding: 16px;
        margin-bottom: 14px;
        color: #FFFFFF;
        box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.4);
    }
    .card-team h3, .card-team h4, .card-team p, .card-team b, .card-team span { 
        color: #FFFFFF !important; 
    }
    .card-team code { 
        background-color: #0B0F19; 
        color: #F472B6; 
        padding: 4px 8px; 
        border-radius: 6px; 
        font-weight: 700; 
    }

    /* Estilização Customizada dos Botões de Menu (Estilo Card Neon) */
    div.stButton > button:first-child {
        background: linear-gradient(135deg, rgba(22, 30, 46, 0.95) 0%, rgba(15, 23, 42, 0.95) 100%);
        color: #FFFFFF;
        font-weight: 600;
        border-radius: 16px;
        border: 1px solid #EC4899;
        padding: 18px 20px;
        width: 100%;
        box-shadow: 0 0 12px rgba(236, 72, 153, 0.25);
        transition: all 0.3s ease;
        text-align: left !important;
    }
    
    div.stButton > button:first-child:hover {
        border-color: #F472B6;
        box-shadow: 0 0 20px rgba(236, 72, 153, 0.5);
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.95) 0%, rgba(22, 30, 46, 0.95) 100%);
    }

    /* Inputs e Caixas de Texto */
    .stTextInput input, .stSelectbox select, .stNumberInput input {
        background-color: #1F2937;
        color: #FFFFFF;
        border: 1px solid #4B5563;
        border-radius: 10px;
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

def obter_tipo_p(p):
    return p.get("tipo", "Avulso") if isinstance(p, dict) else "Avulso"

def file_to_base64(file_path):
    import base64
    with open(file_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

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

if "pagina_atual" not in st.session_state:
    st.session_state.pagina_atual = "login"
if "sub_tela_login" not in st.session_state:
    st.session_state.sub_tela_login = "menu"
if "usuario_logado" not in st.session_state:
    st.session_state.usuario_logado = None
if "perfil_logado" not in st.session_state:
    st.session_state.perfil_logado = None

SENHA_MESTRE_DEV = "1980"
SENHA_AUTORIZACAO_ADMIN = "1980"

# -----------------------------------------------------------------------------
# FUNÇÃO PARA EXIBIR A LOGO NO TOPO COM CUSTOMIZAÇÕES
# -----------------------------------------------------------------------------
def exibir_topo_logo():
    col_top1, col_top2, col_top3 = st.columns([6, 1, 1])
    with col_top3:
        if st.button("🔄 Atualizar", key="btn_reload_top"):
            st.rerun()

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if os.path.exists(LOGO_FILE):
            try:
                b64_img = file_to_base64(LOGO_FILE)
                st.markdown(
                    f'<div style="text-align: center; margin-bottom: 5px;"><img src="data:image/png;base64,{b64_img}" style="width: 100%; max-width: 190px; display: block; margin: 0 auto;" /></div>',
                    unsafe_allow_html=True
                )
            except:
                st.markdown('<h2 style="text-align: center; color: #EC4899;">PELADINHA FC</h2>', unsafe_allow_html=True)
        else:
            st.markdown('<h2 style="text-align: center; color: #EC4899;">PELADINHA FC</h2>', unsafe_allow_html=True)
        
        if st.session_state.perfil_logado == "Dev":
            with st.expander("⚙️ [DEV] Alterar/Enviar Logo"):
                upl_logo = st.file_uploader("Envie a nova imagem da Logo (.png ou .jpg)", type=["png", "jpg", "jpeg"], key="up_logo_topo")
                if upl_logo:
                    with open(LOGO_FILE, "wb") as f:
                        f.write(upl_logo.getbuffer())
                    st.success("Logo atualizada com sucesso! Recarregando...")
                    st.rerun()

# -----------------------------------------------------------------------------
# TELA DE LOGIN / CARDS ESTILO APP MOBILE
# -----------------------------------------------------------------------------
if st.session_state.pagina_atual == "login":
    exibir_topo_logo()
    st.markdown('<p style="text-align: center; color: #9CA3AF; margin-bottom: 25px;">Mais que Futebol, Uma Conexão!</p>', unsafe_allow_html=True)

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

        if st.button("👑 CADASTRAR COMO ADMINISTRADOR", key="btn_card_admin"):
            st.session_state.sub_tela_login = "cad_admin"
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
                        st.success("Cadastro realizado com sucesso! Aguardando aprovação.")
                else:
                    st.error("Preencha todos os campos obrigatórios!")

    elif st.session_state.sub_tela_login == "cad_admin":
        st.subheader("Cadastro de Novo Administrador")
        with st.form("form_cad_admin_novo", clear_on_submit=True):
            a_nome = st.text_input("Nome do Administrador *")
            a_cel = st.text_input("Celular (WhatsApp) *", placeholder="Ex: 5531999999999")
            a_user = st.text_input("Login de Admin *")
            a_pass = st.text_input("Senha de Acesso *", type="password")
            a_aut = st.text_input("Senha de Autorização *", type="password", help="Senha padrão: 1980")
            
            if st.form_submit_button("CADASTRAR ADMINISTRADOR"):
                if a_aut == SENHA_AUTORIZACAO_ADMIN:
                    if a_nome and a_user and a_pass:
                        if any(adm.get("login") == a_user.strip() for adm in st.session_state.administradores):
                            st.error("Este login de administrador já existe!")
                        else:
                            st.session_state.administradores.append({
                                "nome": a_nome.strip(), "login": a_user.strip(),
                                "senha": a_pass.strip(), "celular": a_cel.strip()
                            })
                            salvar_dados(ADMINS_FILE, st.session_state.administradores)
                            st.success("Administrador cadastrado com sucesso!")
                    else:
                        st.error("Preencha todos os campos obrigatórios!")
                else:
                    st.error("Senha de autorização incorreta!")

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
# PAINEL PRINCIPAL (DASHBOARD COM CARDS EM DUAS COLUNAS)
# -----------------------------------------------------------------------------
else:
    exibir_topo_logo()
    
    # Identificação do usuário logado com ícone igual à imagem
    st.markdown(
        f'<div style="text-align: center; margin-bottom: 20px;">'
        f'<span style="background-color: rgba(236, 72, 153, 0.15); color: #F472B6; padding: 6px 16px; border-radius: 20px; font-size: 0.9rem; font-weight: 500; border: 1px solid rgba(236, 72, 153, 0.3);">'
        f'👤 Logado como: <b>{st.session_state.usuario_logado}</b> ({st.session_state.perfil_logado})'
        f'</span></div>',
        unsafe_allow_html=True
    )
    
    # Pequeno divisor com coração centralizado igualzinho à referência
    st.markdown(
        '<div style="text-align: center; color: #EC4899; margin-bottom: 25px; font-size: 0.9rem;">— ♥ —</div>', 
        unsafe_allow_html=True
    )

    if st.session_state.pagina_atual != "dashboard":
        if st.button("⬅️ Voltar ao Menu Principal"):
            st.session_state.pagina_atual = "dashboard"
            st.rerun()
        st.markdown("---")

    if st.session_state.pagina_atual == "dashboard":
        # Lista estruturada com os cards idênticos aos da imagem de referência
        cards = [
            ("📄 **Regulamento**\n\nConsulte o regulamento do time", "regulamento"),
            ("👥 **Lista de Presenças**\n\nVeja e gerencie as presenças", "lista"),
            ("🏆 **Sorteio de Times**\n\nRealize o sorteio de times", "sorteio"),
            ("👕 **Elenco de Jogadoras**\n\nConfira o elenco do time", "elenco"),
            ("💠 **Pagamento Pix**\n\nInformações para pagamento", "pagamento"),
            ("🎂 **Aniversariantes do Mês**\n\nConfira quem faz aniversário", "aniversariantes")
        ]

        if st.session_state.perfil_logado in ["Admin", "Dev"]:
            cards.append(("📸 **Fluxo de Caixa**\n\nAcompanhe entradas e saídas", "caixa"))
            cards.append(("⚙️ **Gerenciamento Geral**\n\nConfigurações e gerenciamento", "gerenciamento"))

        # Renderização em 2 colunas perfeitas
        cols = st.columns(2)
        for i, (texto_botao, rota) in enumerate(cards):
            with cols[i % 2]:
                if st.button(texto_botao, use_container_width=True, key=f"card_menu_{rota}_{i}"):
                    st.session_state.pagina_atual = rota
                    st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)
        
        # Botão Inferior de Sair da Conta em largura total
        if st.button("🚪 **Sair da Conta**", use_container_width=True, key="btn_sair_conta_full"):
            st.session_state.usuario_logado = None
            st.session_state.perfil_logado = None
            st.session_state.sub_tela_login = "menu"
            st.session_state.pagina_atual = "login"
            st.rerun()

        # Rodapé idêntico ao modelo da imagem
        st.markdown(
            '<div style="text-align: center; color: #9CA3AF; font-size: 0.8rem; margin-top: 40px; margin-bottom: 20px;">'
            '© 2026 Peladinha FC | Mais que Futebol, Uma Conexão! ♥'
            '</div>', 
            unsafe_allow_html=True
        )

    elif st.session_state.pagina_atual == "regulamento":
        st.subheader("📄 Regulamento Interno & Boa Convivência")
        for reg in st.session_state.regulamento:
            st.markdown(f'<div class="card-team"><h4>{reg["topico"]}</h4><p>{reg["regrinha"]}</p></div>', unsafe_allow_html=True)

    elif st.session_state.pagina_atual == "aniversariantes":
        st.subheader("🎂 Painel de Aniversariantes do Mês")
        mes_atual = hoje_dt.month
        aniversariantes_mes = [j for j in st.session_state.jogadoras if j.get("nascimento") and int(j.get("nascimento").split("/")[1]) == mes_atual]
        if not aniversariantes_mes:
            st.info("Nenhuma atleta faz aniversário neste mês.")
        else:
            for a in aniversariantes_mes:
                st.markdown(f'<div class="card-team"><h3>🎉 {a["nome"]}</h3><p>Data: <b>{a.get("nascimento")}</b></p></div>', unsafe_allow_html=True)

    elif st.session_state.pagina_atual == "lista":
        st.subheader("📋 Lista de Presença e Confirmações")
        limite = st.session_state.avisos.get("limite_vagas", 15)
        lista_atual = sorted(st.session_state.presencas, key=lambda x: x.get("dt_confirmacao", x.get("hora", "")))
        
        mensalistas = [p for p in lista_atual if obter_tipo_p(p) == "Mensalista"]
        avulsas = [p for p in lista_atual if obter_tipo_p(p) != "Mensalista"]
        
        confirmadas = mensalistas[:limite]
        espera = mensalistas[limite:] + avulsas

        col_l1, col_l2 = st.columns(2)
        with col_l1:
            st.write(f"### 🟢 Confirmadas ({len(confirmadas)}/{limite})")
  
