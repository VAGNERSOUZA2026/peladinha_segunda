import streamlit as st
import pandas as pd
import json
import os
import random
from datetime import datetime, timedelta, timezone
import urllib.parse

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
# ESTILIZAÇÃO CSS CUSTOMIZADA (VISUAL NEON ROSA / DARK COM ALTO CONTRASTE)
# -----------------------------------------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] { 
        font-family: 'Montserrat', sans-serif; 
        color: #FFFFFF !important; 
    }
    
    .stApp { 
        background-color: #080C14;
        background-image: radial-gradient(#EC4899 0.75px, transparent 0.75px), radial-gradient(#EC4899 0.75px, #080C14 0.75px);
        background-size: 30px 30px;
        background-position: 0 0, 15px 15px;
    }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    h1, h2, h3, h4, h5, h6, label, p, span, div {
        color: #FFFFFF !important;
        text-shadow: 0px 1px 3px rgba(0,0,0,0.8);
    }

    .streamlit-expanderHeader, div[data-testid="stExpander"], div[data-baseweb="accordion"] {
        background-color: #161E2E !important;
        border: 1px solid #EC4899 !important;
        border-radius: 12px !important;
        color: #FFFFFF !important;
    }
    
    div[data-testid="stFileUploader"] {
        background-color: #161E2E !important;
        border: 1px solid #EC4899 !important;
        border-radius: 12px !important;
        padding: 15px !important;
    }
    
    div[data-testid="stFileUploader"] section {
        background-color: #0B0F19 !important;
        border: 1px dashed #EC4899 !important;
    }

    div.stTabs [data-baseweb="tab-list"] {
        background-color: #0B0F19 !important;
    }
    div.stTabs [data-baseweb="tab"] {
        color: #FFFFFF !important;
    }

    .card-team {
        background: rgba(22, 30, 46, 0.95);
        border: 1px solid #EC4899;
        border-radius: 14px;
        padding: 16px;
        margin-bottom: 14px;
        color: #FFFFFF;
        box-shadow: 0px 4px 15px rgba(236, 72, 153, 0.2);
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

    div.stButton > button:first-child {
        background: linear-gradient(135deg, rgba(22, 30, 46, 0.95) 0%, rgba(15, 23, 42, 0.95) 100%);
        color: #FFFFFF !important;
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

    .stTextInput input, .stSelectbox select, .stNumberInput input, .stTextArea textarea {
        background-color: #1F2937 !important;
        color: #FFFFFF !important;
        border: 1px solid #EC4899 !important;
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
    st.session_state.jogadoras = carregar_dados(DATA_FILE, [
        {"nome": "Camila Admin", "nascimento": "18/08", "login": "camila", "senha": "123", "tipo": "Mensalista", "status": "Ativo", "quitado": "Sim"},
        {"nome": "Juliana Atleta", "nascimento": "12/03", "login": "juliana", "senha": "123", "tipo": "Mensalista", "status": "Ativo", "quitado": "Não"},
        {"nome": "Mariana Avulsa", "nascimento": "25/07", "login": "mariana", "senha": "123", "tipo": "Avulso", "status": "Ativo", "quitado": "Sim"}
    ])
if "presencas" not in st.session_state:
    st.session_state.presencas = carregar_dados(PRESENCAS_FILE, [])
if "financeiro" not in st.session_state:
    st.session_state.financeiro = carregar_dados(FINANCE_FILE, [
        {"data": "2026-08-01", "tipo": "Receita", "descricao": "Mensalidade - Camila Admin", "valor": 50.00, "status": "Pago"}
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
        "banco": "Banco Inter",
        "beneficiario": "Peladinha FC Ltda",
        "limite_vagas": 15,
        "valor_mensalidade": 50.00,
        "valor_avulso": 15.00,
        "senha_autorizacao_admin": "1980",
        "whatsapp_admin": "5531999999999"
    })
if "regulamento" not in st.session_state:
    st.session_state.regulamento = carregar_dados(REGULAMENTO_FILE, [
        {"topico": "📌 1. Prioridade de Mensalistas", "regrinha": "Mensalistas confirmando até as 17:00 de segunda-feira têm prioridade nas 15 vagas."},
        {"topico": "⏳ 2. Fila de Espera de Avulsas", "regrinha": "Avulsas entram na fila de espera. Após as 17:00, se sobrarem vagas, sobem automaticamente."},
        {"topico": "⏰ 3. Fechamento e Sorteio Automático", "regrinha": "A lista fecha às 18:00 e o sorteio automático dos grupos é realizado rigidamente às 18:30."},
        {"topico": "🚫 4. Conduta e Fair Play na Quadra", "regrinha": "Entradas violentas, jogo desleal e agressões verbais são estritamente proibidos, sujeitos a suspensão imediata."}
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

# -----------------------------------------------------------------------------
# FUNÇÃO PARA EXIBIR A LOGO NO TOPO
# -----------------------------------------------------------------------------
def exibir_topo_logo():
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
                    st.success("Logo atualizada com sucesso!")
                    st.rerun()

# -----------------------------------------------------------------------------
# TELA DE LOGIN / CARDS ESTILO APP MOBILE
# -----------------------------------------------------------------------------
if st.session_state.pagina_atual == "login":
    exibir_topo_logo()
    st.markdown('<p style="text-align: center; color: #F3F4F6; font-weight: 600; margin-bottom: 25px;">Mais que Futebol, Uma Conexão!</p>', unsafe_allow_html=True)

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
                        
                        # Disparo automático de WhatsApp para o Admin
                        celular_adm = st.session_state.avisos.get("whatsapp_admin", "5531999999999")
                        msg_wpp = f"Olá Admin! Uma nova atleta se cadastrou e aguarda aprovação: *{c_nome.strip()}* ({c_tipo}). Acesse o app para liberar o acesso!"
                        link_wpp = f"https://api.whatsapp.com/send?phone={celular_adm}&text={urllib.parse.quote(msg_wpp)}"
                        st.markdown(f'<a href="{link_wpp}" target="_blank"><button style="background-color: #25D366; color: white; border: none; padding: 10px 20px; border-radius: 8px; font-weight: bold; cursor: pointer; width: 100%; margin-top: 10px;">📲 Enviar Aviso WhatsApp para o Admin</button></a>', unsafe_allow_html=True)
                else:
                    st.error("Preencha todos os campos obrigatórios!")

    elif st.session_state.sub_tela_login == "cad_admin":
        st.subheader("Cadastro de Novo Administrador")
        a_nome = st.text_input("Nome do Administrador *", key="cad_adm_nome")
        a_cel = st.text_input("Celular (WhatsApp) *", placeholder="Ex: 5531999999999", key="cad_adm_cel")
        a_user = st.text_input("Login de Admin *", key="cad_adm_user")
        a_pass = st.text_input("Senha de Acesso *", type="password", key="cad_adm_pass")
        
        senha_autorizacao_atual = st.session_state.avisos.get("senha_autorizacao_admin", "1980")
        a_aut = st.text_input("Senha de Autorização *", type="password", key="cad_adm_aut")
        
        if st.button("CADASTRAR ADMINISTRADOR", key="btn_sub_adm_custom"):
            if a_aut.strip() == senha_autorizacao_atual:
                if a_nome and a_user and a_pass:
                    if any(adm.get("login") == a_user.strip() for adm in st.session_state.administradores):
                        st.error("Este login de administrador já existe!")
                    else:
                        st.session_state.administradores.append({
                            "nome": a_nome.strip(), "login": a_user.strip(),
                            "senha": a_pass.strip(), "celular": a_cel.strip()
                        })
                        salvar_dados(ADMINS_FILE, st.session_state.administradores)
                        st.success("Administrador cadastrado com sucesso! Agora você já pode fazer o login.")
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
    
    hora_atual = hoje_dt.hour
    if 5 <= hora_atual < 12:
        saudacao_tempo = "Bom dia"
    elif 12 <= hora_atual < 18:
        saudacao_tempo = "Boa tarde"
    else:
        saudacao_tempo = "Boa noite"

    eh_aniversario_hoje = False
    if st.session_state.perfil_logado == "Jogadora":
        atleta_obj = next((j for j in st.session_state.jogadoras if j.get("nome") == st.session_state.usuario_logado), None)
        if atleta_obj and atleta_obj.get("nascimento"):
            try:
                partes_nasc = atleta_obj.get("nascimento").split("/")
                dia_nasc = int(partes_nasc[0])
                mes_nasc = int(partes_nasc[1])
                if dia_nasc == hoje_dt.day and mes_nasc == hoje_dt.month:
                    eh_aniversario_hoje = True
            except:
                pass

    if eh_aniversario_hoje:
        st.markdown(
            f'<div class="card-team" style="border-color: #EC4899; text-align: center; box-shadow: 0 0 20px rgba(236,72,153,0.5);">'
            f'<h3>🥳 {saudacao_tempo}, {st.session_state.usuario_logado}! 🎂</h3>'
            f'<p><b>Parabéns pelo seu aniversário! Muita saúde, alegria e gols hoje e sempre! 💖⚽</b></p>'
            f'</div>',
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            f'<div style="text-align: center; margin-bottom: 15px;">'
            f'<span style="background-color: rgba(236, 72, 153, 0.25); color: #FFFFFF; padding: 6px 16px; border-radius: 20px; font-size: 0.95rem; font-weight: 700; border: 1px solid #EC4899;">'
            f'✨ {saudacao_tempo}, <b>{st.session_state.usuario_logado}</b>! ({st.session_state.perfil_logado})'
            f'</span></div>',
            unsafe_allow_html=True
        )
    
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
        cards = [
            ("📄 **Regulamento**\n\nConsulte o regulamento do time", "regulamento"),
            ("👥 **Lista de Presenças**\n\nVeja e gerencie as presenças", "lista"),
            ("🏆 **Sorteio de Times & Grupos**\n\nSorteio automático e paralelo", "sorteio"),
            ("👕 **Elenco de Jogadoras**\n\nConfira o status do elenco", "elenco"),
            ("💠 **Pagamento Pix**\n\nValores e envio de comprovantes", "pagamento"),
            ("🎂 **Aniversariantes do Mês**\n\nParabéns e felicitações", "aniversariantes"),
            ("💡 **Sugestões de Melhorias**\n\nDicas e inovações para o app", "melhorias")
        ]

        if st.session_state.perfil_logado in ["Admin", "Dev"]:
            cards.append(("📸 **Fluxo de Caixa**\n\nReceitas, despesas e pagamentos", "caixa"))
            cards.append(("⚙️ **Gerenciamento Geral**\n\nAprovações e configurações", "gerenciamento"))
            
        if st.session_state.perfil_logado == "Dev":
            cards.append(("🔑 **Credenciais (DEV)**\n\nVisualização e edição de senhas", "credenciais"))

        cols = st.columns(2)
        for i, (texto_botao, rota) in enumerate(cards):
            with cols[i % 2]:
                if st.button(texto_botao, use_container_width=True, key=f"card_menu_{rota}_{i}"):
                    st.session_state.pagina_atual = rota
                    st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.button("🚪 **Sair da Conta**", use_container_width=True, key="btn_sair_conta_full"):
            st.session_state.usuario_logado = None
            st.session_state.perfil_logado = None
            st.session_state.sub_tela_login = "menu"
            st.session_state.pagina_atual = "login"
            st.rerun()

        st.markdown(
            '<div style="text-align: center; color: #FFFFFF; font-weight: 600; font-size: 0.85rem; margin-top: 40px; margin-bottom: 20px;">'
            '© 2026 Peladinha FC | Mais que Futebol, Uma Conexão! ♥'
            '</div>', 
            unsafe_allow_html=True
        )

    elif st.session_state.pagina_atual == "regulamento":
        st.subheader("📄 Regulamento Interno & Boa Convivência")
        
        if st.session_state.perfil_logado in ["Admin", "Dev"]:
            with st.expander("🛠️ Adicionar / Editar Regra"):
                with st.form("form_add_regra"):
                    nova_top = st.text_input("Título do Tópico", placeholder="Ex: 5. Novo Tópico")
                    nova_reg = st.text_area("Descrição da Regra")
                    if st.form_submit_button("Salvar Nova Regra"):
                        if nova_top and nova_reg:
                            st.session_state.regulamento.append({"topico": nova_top, "regrinha": nova_reg})
                            salvar_dados(REGULAMENTO_FILE, st.session_state.regulamento)
                            st.success("Regra adicionada!")
                            st.rerun()

        for idx, reg in enumerate(st.session_state.regulamento):
            st.markdown(f'<div class="card-team"><h4>{reg["topico"]}</h4><p>{reg["regrinha"]}</p></div>', unsafe_allow_html=True)
            if st.session_state.perfil_logado in ["Admin", "Dev"]:
                if st.button(f"🗑️ Excluir Regra {idx+1}", key=f"del_reg_{idx}"):
                    st.session_state.regulamento.pop(idx)
                    salvar_dados(REGULAMENTO_FILE, st.session_state.regulamento)
                    st.rerun()

    elif st.session_state.pagina_atual == "aniversariantes":
        st.subheader("🎂 Painel de Aniversariantes do Mês")
        mes_atual = hoje_dt.month
        dia_atual = hoje_dt.day
        
        aniversariantes_mes = [j for j in st.session_state.jogadoras if j.get("nascimento") and int(j.get("nascimento").split("/")[1]) == mes_atual]
        
        if not aniversariantes_mes:
            st.info("Nenhuma atleta faz aniversário neste mês.")
        else:
            for a in aniversariantes_mes:
                nasc_str = a.get("nascimento")
                dia_nasc = int(nasc_str.split("/")[0]) if "/" in nasc_str else 0
                
                if dia_nasc == dia_atual:
                    st.markdown(f'<div class="card-team" style="border-color: #EC4899; box-shadow: 0 0 15px rgba(236,72,153,0.5);"><h3>🥳 HOJE É ANIVERSÁRIO DE: {a["nome"]}! 🎂</h3><p>Mensagem automática: <b>"Feliz Aniversário, {a["nome"]}! Muita saúde, alegria e gols!"</b> 💖</p></div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="card-team"><h3>🎉 {a["nome"]}</h3><p>Data: <b>{nasc_str}</b></p></div>', unsafe_allow_html=True)
            
            st.markdown("---")
            st.info("💌 Mensagem disparada para o grupo lembrando todas das aniversariantes do dia!")

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
            for i, p in enumerate(confirmadas, 1):
                nome_p = obter_nome_p(p)
                tipo_p = obter_tipo_p(p)
                hora_p = p.get("hora", "--:--") if isinstance(p, dict) else "--:--"
                st.markdown(f'<div class="card-team"><b>{i}.</b> {nome_p} <code>[{tipo_p}]</code> <br><small>🕒 Confirmado às: {hora_p}</small></div>', unsafe_allow_html=True)

            st.write(f"### ⏳ Fila de Espera ({len(espera)})")
            for i, p in enumerate(espera, 1):
                nome_p = obter_nome_p(p)
                tipo_p = obter_tipo_p(p)
                hora_p = p.get("hora", "--:--") if isinstance(p, dict) else "--:--"
                st.markdown(f'<div class="card-team"><b>{i}º:</b> {nome_p} <code>[{tipo_p}]</code> <br><small>🕒 Confirmado às: {hora_p}</small></div>', unsafe_allow_html=True)

        with col_l2:
            if st.session_state.perfil_logado in ["Admin", "Dev"]:
                st.write("### 👑 Inclusão pelo Admin")
                
                with st.form("form_add_manual_cadastrada"):
                    atativas_nomes = [j["nome"] for j in st.session_state.jogadoras if j.get("status") == "Ativo"]
                    atleta_escolhida = st.selectbox("Adicionar Jogadora Cadastrada", atativas_nomes if atativas_nomes else ["Nenhuma"])
                    if st.form_submit_button("Incluir Cadastrada"):
                        if atativas_nomes and not any(obter_nome_p(p) == atleta_escolhida for p in st.session_state.presencas):
                            tipo_atl = next((j.get("tipo", "Avulso") for j in st.session_state.jogadoras if j["nome"] == atleta_escolhida), "Avulso")
                            st.session_state.presencas.append({"nome": atleta_escolhida, "hora": hoje_dt.strftime("%H:%M"), "tipo": tipo_atl, "dt_confirmacao": hoje_dt.isoformat()})
                            salvar_dados(PRESENCAS_FILE, st.session_state.presencas)
                            st.success(f"{atleta_escolhida} incluída!")
                            st.rerun()

                with st.form("form_add_manual_convidada"):
                    nome_convidada = st.text_input("Adicionar Convidada Avulsa (Nome)")
                    if st.form_submit_button("Incluir Convidada"):
                        if nome_convidada.strip():
                            if not any(obter_nome_p(p).lower() == nome_convidada.strip().lower() for p in st.session_state.presencas):
                                st.session_state.presencas.append({"nome": nome_convidada.strip(), "hora": hoje_dt.strftime("%H:%M"), "tipo": "Convidada", "dt_confirmacao": hoje_dt.isoformat()})
                                salvar_dados(PRESENCAS_FILE, st.session_state.presencas)
                                st.success(f"Convidada {nome_convidada.strip()} incluída!")
                                st.rerun()
                            else:
                                st.warning("Essa pessoa já está na lista!")
                        else:
                            st.error("Digite o nome da convidada.")
                
                st.write("#### Remover da Lista")
                for p in st.session_state.presencas:
                    c_nome = obter_nome_p(p)
                    if st.button(f"Remover {c_nome}", key=f"rem_l_{c_nome}"):
                        st.session_state.presencas = [item for item in st.session_state.presencas if obter_nome_p(item) != c_nome]
                        salvar_dados(PRESENCAS_FILE, st.session_state.presencas)
                        st.rerun()
            else:
                st.write("### ✍️ Minha Presença")
                j_name = st.session_state.usuario_logado
                ja_esta = any(obter_nome_p(p) == j_name for p in st.session_state.presencas)
                tipo_usuario_atual = next((j.get("tipo", "Avulso") for j in st.session_state.jogadoras if j["nome"] == j_name), "Avulso")
                
                with st.form("form_pres"):
                    c_ok = st.form_submit_button("👍 Confirmar Presença")
                    c_canc = st.form_submit_button("❌ Cancelar Presença")
                
                if c_ok:
                    if ja_esta:
                        st.info("Você já confirmou sua presença! Seu horário e posição foram mantidos.")
                    else:
                        st.session_state.presencas.append({
                            "nome": j_name, 
                            "hora": hoje_dt.strftime("%H:%M"), 
                            "tipo": tipo_usuario_atual, 
                            "dt_confirmacao": hoje_dt.isoformat()
                        })
                        salvar_dados(PRESENCAS_FILE, st.session_state.presencas)
                        st.success("Presença confirmada com sucesso!")
                        st.rerun()

                if c_canc:
                    if ja_esta:
                        st.session_state.presencas = [p for p in st.session_state.presencas if obter_nome_p(p) != j_name]
                        salvar_dados(PRESENCAS_FILE, st.session_state.presencas)
                        st.success("Sua presença foi cancelada.")
                        st.rerun()
                    else:
                        st.warning("Você não está na lista de presença.")

    elif st.session_state.pagina_atual == "sorteio":
        st.subheader("🏆 Sorteio de Times & Grupos (Às 18:30)")
        
        st.markdown("### 🤖 Sorteio Oficial Automático (Grupos)")
        nomes_oficiais = [obter_nome_p(p) for p in st.session_state.presencas][:15]
        
        if st.session_state.perfil_logado in ["Admin", "Dev"]:
            with st.expander("🛠️ Editar Participantes do Sorteio Oficial"):
                nomes_editados = st.multiselect(
                    "Selecione as atletas presentes para o sorteio:", 
                    [j["nome"] for j in st.session_state.jogadoras if j.get("status") == "Ativo"], 
                    default=nomes_oficiais if nomes_oficiais else None
                )
                if st.button("Atualizar Lista Oficial do Sorteio"):
                    st.session_state.presencas = [{"nome": n, "tipo": "Atleta"} for n in nomes_editados]
                    salvar_dados(PRESENCAS_FILE, st.session_state.presencas)
                    st.success("Lista oficial atualizada com sucesso!")
                    st.rerun()

        if len(nomes_oficiais) >= 2:
            random.shuffle(nomes_oficiais)
            metade = len(nomes_oficiais) // 2
            grupo_a = nomes_oficiais[:metade]
            grupo_b = nomes_oficiais[metade:]
            
            col_g1, col_g2 = st.columns(2)
            with col_g1:
                st.markdown(f'<div class="card-team"><h4>⭐ Grupo A</h4>' + "".join([f"<p>• {n}</p>" for n in grupo_a]) + '</div>', unsafe_allow_html=True)
            with col_g2:
                st.markdown(f'<div class="card-team"><h4>⭐ Grupo B</h4>' + "".join([f"<p>• {n}</p>" for n in grupo_b]) + '</div>', unsafe_allow_html=True)
        else:
            st.info("Aguardando confirmações suficientes para o sorteio automático das 18:30.")

        st.markdown("---")
        st.markdown("### ⚡ Sorteio Paralelo (Na Quadra - Sem interferir no oficial)")
        presenca_quadra = st.text_area("Digite os nomes presentes na quadra (separados por vírgula):", placeholder="Ex: Camila, Juliana, Mariana, Beatriz")
        if st.button("Realizar Sorteio Paralelo na Quadra"):
            if presenca_quadra:
                lista_paralela = [n.strip() for n in presenca_quadra.split(",") if n.strip()]
                if len(lista_paralela) >= 2:
                    random.shuffle(lista_paralela)
                    metade_p = len(lista_paralela) // 2
                    time_1 = lista_paralela[:metade_p]
                    time_2 = lista_paralela[metade_p:]
                    
                    col_p1, col_p2 = st.columns(2)
                    with col_p1:
                        st.markdown(f'<div class="card-team"><h4>⚽ Time 1 (Paralelo)</h4>' + "".join([f"<p>• {n}</p>" for n in time_1]) + '</div>', unsafe_allow_html=True)
                    with col_p2:
                        st.markdown(f'<div class="card-team"><h4>⚽ Time 2 (Paralelo)</h4>' + "".join([f"<p>• {n}</p>" for n in time_2]) + '</div>', unsafe_allow_html=True)
                else:
                    st.warning("Insira pelo menos 2 nomes para realizar o sorteio paralelo.")
            else:
                st.error("Digite os nomes das atletas presentes na quadra.")

    elif st.session_state.pagina_atual == "elenco":
        st.subheader("👕 Elenco de Jogadoras Cadastradas")
        for idx, j in enumerate(st.session_state.jogadoras):
            st.markdown(
                f'<div class="card-team">'
                f'<h4>{j.get("nome")}</h4>'
                f'<p>Tipo: <code>{j.get("tipo")}</code> | Status: <code>{j.get("status")}</code> | Mensalidade Quitada: <code>{j.get("quitado", "Não")}</code></p>'
                f'<small>Nascimento: {j.get("nascimento", "--/--")}</small>'
                f'</div>',
                unsafe_allow_html=True
            )
            if st.session_state.perfil_logado in ["Admin", "Dev"]:
                col_el1, col_el2 = st.columns(2)
                with col_el1:
                    novo_quit = "Sim" if j.get("quitado") != "Sim" else "Não"
                    if st.button(f"Alternar Quitação ({novo_quit})", key=f"quit_{idx}"):
                        st.session_state.jogadoras[idx]["quitado"] = novo_quit
                        salvar_dados(DATA_FILE, st.session_state.jogadoras)
                        st.rerun()
                with col_el2:
                    if st.button(f"Excluir Jogadora", key=f"del_jog_{idx}"):
                        st.session_state.jogadoras.pop(idx)
                        salvar_dados(DATA_FILE, st.session_state.jogadoras)
                        st.rerun()

    elif st.session_state.pagina_atual == "pagamento":
        st.subheader("💠 Pagamento via Pix & Envio de Comprovantes")
        pix_chave = st.session_state.avisos.get("pix", "peladinhafc@email.com")
        banco_nome = st.session_state.avisos.get("banco", "Banco Inter")
        beneficiario_nome = st.session_state.avisos.get("beneficiario", "Peladinha FC Ltda")
        v_mensal = st.session_state.avisos.get("valor_mensalidade", 50.00)
        v_avulso = st.session_state.avisos.get("valor_avulso", 15.00)
        
        st.markdown(
            f'<div class="card-team">'
            f'<h4>📌 Dados para Pagamento Pix</h4>'
            f'<p><b>Chave Pix:</b> <code>{pix_chave}</code></p>'
            f'<p><b>Instituição/Banco:</b> {banco_nome}</p>'
            f'<p><b>Beneficiário:</b> {beneficiario_nome}</p>'
            f'<hr style="border-color: #EC4899;">'
            f'<p><b>Valores:</b> Mensalidade: R$ {v_mensal:.2f} | Avulso: R$ {v_avulso:.2f}</p>'
            f'</div>',
            unsafe_allow_html=True
        )
        
        st.markdown("### 📤 Enviar Comprovante de Pagamento")
        with st.form("form_envio_comprovante", clear_on_submit=True):
            nome_pagante = st.text_input("Nome da Atleta / Pagante", value=st.session_state.usuario_logado if st.session_state.usuario_logado else "")
            desc_pagamento = st.text_input("Descrição (Ex: Mensalidade de Agosto / Jogo Avulso)")
            arquivo_comp = st.file_uploader("Anexar Imagem do Comprovante (.png, .jpg)", type=["png", "jpg", "jpeg"])
            
            if st.form_submit_button("Enviar Comprovante"):
                if nome_pagante and arquivo_comp:
                    nome_arquivo = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{arquivo_comp.name}"
                    caminho_completo = os.path.join(UPLOAD_DIR, nome_arquivo)
                    with open(caminho_completo, "wb") as f:
                        f.write(arquivo_comp.getbuffer())
                    
                    st.session_state.comprovantes.append({
                        "nome": nome_pagante,
                        "descricao": desc_pagamento,
                        "arquivo": caminho_completo,
                        "data": hoje_dt.strftime("%d/%m/%Y %H:%M"),
                        "status": "Pendente"
                    })
                    salvar_dados(COMPROVANTES_FILE, st.session_state.comprovantes)
                    st.success("Comprovante enviado com sucesso para análise do Administrador!")
                else:
                    st.error("Preencha o nome e selecione a imagem do comprovante.")

    elif st.session_state.pagina_atual == "caixa":
        st.subheader("📸 Fluxo de Caixa Detalhado e Status de Pagamento")
        
        total_rec = sum(item["valor"] for item in st.session_state.financeiro if item.get("tipo") == "Receita" and item.get("status") == "Pago")
        total_desp = sum(item["valor"] for item in st.session_state.financeiro if item.get("tipo") == "Despesa" and item.get("status") == "Pago")
        saldo_caixa = total_rec - total_desp
        
        col_c1, col_c2, col_c3 = st.columns(3)
        with col_c1:
            st.metric("Receitas", f"R$ {total_rec:.2f}")
        with col_c2:
            st.metric("Despesas", f"R$ {total_desp:.2f}")
        with col_c3:
            st.metric("Saldo Atual", f"R$ {saldo_caixa:.2f}")
            
        st.markdown("---")
        st.markdown("### 📊 Status de Pagamento das Atletas (Mensalistas e Avulsas)")
        st.info("Aqui você acompanha e atualiza manualmente (Dinheiro, Pix direto ou isenção) o status financeiro de cada atleta.")
        
        for idx_j, j in enumerate(st.session_state.jogadoras):
            if j.get("status") == "Ativo":
                quit_atual = j.get("quitado", "Não")
                cor_tag = "#10B981" if quit_atual == "Sim" else "#EF4444"
                
                col_j1, col_j2, col_j3 = st.columns([2, 1, 1])
                with col_j1:
                    st.markdown(f"<b>{j.get('nome')}</b> <code>[{j.get('tipo')}]</code>", unsafe_allow_html=True)
                with col_j2:
                    st.markdown(f'<span style="color: {cor_tag}; font-weight: bold;">Pago: {quit_atual}</span>', unsafe_allow_html=True)
                with col_j3:
                    novo_status_q = "Não" if quit_atual == "Sim" else "Sim"
                    if st.button(f"Mudar p/ {novo_status_q}", key=f"tog_pag_{idx_j}"):
                        val_ref = st.session_state.avisos.get("valor_mensalidade", 50.0) if j.get("tipo") == "Mensalista" else st.session_state.avisos.get("valor_avulso", 15.0)
                        st.session_state.jogadoras[idx_j]["quitado"] = novo_status_q
                        salvar_dados(DATA_FILE, st.session_state.jogadoras)
                        
                        # Se mudou para Sim, registra no fluxo de caixa automaticamente
                        if novo_status_q == "Sim":
                            st.session_state.financeiro.append({
                                "data": hoje_dt.strftime("%Y-%m-%d"),
                                "tipo": "Receita",
                                "descricao": f"Pagamento ({j.get('tipo')}) - {j.get('nome')}",
                                "valor": val_ref,
                                "status": "Pago"
                            })
                            salvar_dados(FINANCE_FILE, st.session_state.financeiro)
                        st.rerun()

        st.markdown("---")
        st.markdown("### 📥 Comprovantes Enviados para Aprovação")
        if not st.session_state.comprovantes:
            st.info("Nenhum comprovante enviado no momento.")
        else:
            for idx, comp in enumerate(st.session_state.comprovantes):
                st.markdown(
                    f'<div class="card-team">'
                    f'<h4>Enviado por: {comp.get("nome")}</h4>'
                    f'<p>Descrição: {comp.get("descricao")}</p>'
                    f'<p>Data: {comp.get("data")} | Status: <code>{comp.get("status")}</code></p>'
                    f'</div>',
                    unsafe_allow_html=True
                )
                if os.path.exists(comp.get("arquivo", "")):
                    st.image(comp["arquivo"], caption=f"Comprovante de {comp.get('nome')}", width=300)
                
                if comp.get("status") == "Pendente":
                    if st.button("Aprovar Comprovante e Lançar no Caixa", key=f"apr_comp_{idx}"):
                        st.session_state.comprovantes[idx]["status"] = "Aprovado"
                        salvar_dados(COMPROVANTES_FILE, st.session_state.comprovantes)
                        
                        # Adiciona no caixa automaticamente
                        val_padrao = st.session_state.avisos.get("valor_mensalidade", 50.0)
                        st.session_state.financeiro.append({
                            "data": hoje_dt.strftime("%Y-%m-%d"),
                            "tipo": "Receita",
                            "descricao": f"Comprovante Pix - {comp.get('nome')} ({comp.get('descricao')})",
                            "valor": val_padrao,
                            "status": "Pago"
                        })
                        salvar_dados(FINANCE_FILE, st.session_state.financeiro)
                        st.success("Comprovante aprovado e receita lançada no caixa!")
                        st.rerun()

        st.markdown("---")
        st.markdown("### ➕ Adicionar Despesa / Receita Manual")
        with st.form("form_novo_fluxo", clear_on_submit=True):
            f_tipo = st.selectbox("Tipo", ["Receita", "Despesa"])
            f_desc = st.text_input("Descrição (Ex: Aluguel da Quadra / Coletes Novos)")
            f_valor = st.number_input("Valor (R$)", min_value=0.0, step=5.0)
            f_status = st.selectbox("Status", ["Pago", "Pendente"])
            if st.form_submit_button("Salvar Lançamento"):
                if f_desc and f_valor > 0:
                    st.session_state.financeiro.append({
                        "data": hoje_dt.strftime("%Y-%m-%d"),
                        "tipo": f_tipo,
                        "descricao": f_desc,
                        "valor": f_valor,
                        "status": f_status
                    })
                    salvar_dados(FINANCE_FILE, st.session_state.financeiro)
                    st.success("Movimentação salva!")
                    st.rerun()
                else:
                    st.error("Preencha a descrição e um valor válido.")

    elif st.session_state.pagina_atual == "credenciais" and st.session_state.perfil_logado == "Dev":
        st.subheader("🔑 [DEV] Gerenciamento de Credenciais e Senhas")
        st.info("Painel exclusivo para o Desenvolvedor visualizar, auditar e redefinir logins e senhas de todas as usuárias e administradoras.")
        
        st.markdown("### 👑 Administradores Cadastrados")
        for i, adm in enumerate(st.session_state.administradores):
            with st.expander(f"Admin: {adm.get('nome')} ({adm.get('login')})"):
                with st.form(f"form_edt_adm_{i}"):
                    e_nome = st.text_input("Nome", value=adm.get("nome"), key=f"eadm_n_{i}")
                    e_log = st.text_input("Login", value=adm.get("login"), key=f"eadm_l_{i}")
                    e_pass = st.text_input("Senha", value=adm.get("senha"), key=f"eadm_p_{i}")
                    e_cel = st.text_input("Celular", value=adm.get("celular", ""), key=f"eadm_c_{i}")
                    if st.form_submit_button("Salvar Alterações do Admin"):
                        st.session_state.administradores[i]["nome"] = e_nome
                        st.session_state.administradores[i]["login"] = e_log
                        st.session_state.administradores[i]["senha"] = e_pass
                        st.session_state.administradores[i]["celular"] = e_cel
                        salvar_dados(ADMINS_FILE, st.session_state.administradores)
                        st.success("Credenciais do Admin atualizadas!")
                        st.rerun()

        st.markdown("---")
        st.markdown("### ⚽ Atletas Cadastradas")
        for i, jog in enumerate(st.session_state.jogadoras):
            with st.expander(f"Atleta: {jog.get('nome')} [{jog.get('tipo')}]"):
                with st.form(f"form_edt_jog_{i}"):
                    ej_nome = st.text_input("Nome", value=jog.get("nome"), key=f"ejog_n_{i}")
                    ej_log = st.text_input("Login", value=jog.get("login"), key=f"ejog_l_{i}")
                    ej_pass = st.text_input("Senha", value=jog.get("senha"), key=f"ejog_p_{i}")
                    ej_tipo = st.selectbox("Tipo", ["Avulso", "Mensalista"], index=0 if jog.get("tipo") == "Avulso" else 1, key=f"ejog_t_{i}")
                    ej_stat = st.selectbox("Status", ["Ativo", "Pendente"], index=0 if jog.get("status") == "Ativo" else 1, key=f"ejog_s_{i}")
                    if st.form_submit_button("Salvar Alterações da Atleta"):
                        st.session_state.jogadoras[i]["nome"] = ej_nome
                        st.session_state.jogadoras[i]["login"] = ej_log
                        st.session_state.jogadoras[i]["senha"] = ej_pass
                        st.session_state.jogadoras[i]["tipo"] = ej_tipo
                        st.session_state.jogadoras[i]["status"] = ej_stat
                        salvar_dados(DATA_FILE, st.session_state.jogadoras)
                        st.success("Credenciais da atleta atualizadas!")
                        st.rerun()

    elif st.session_state.pagina_atual == "gerenciamento":
        st.subheader("⚙️ Gerenciamento Geral & Aprovações")
        
        st.markdown("### ⏳ Cadastros de Atletas Pendentes")
        pendentes = [j for j in st.session_state.jogadoras if j.get("status"] == "Pendente"]
        if not pendentes:
            st.info("Nenhum cadastro pendente de aprovação.")
        else:
            for j in st.session_state.jogadoras:
                if j.get("status"] == "Pendente":
                    st.markdown(
                        f'<div class="card-team">'
                        f'<h4>{j.get("nome")} ({j.get("tipo")})</h4>'
                        f'<p>Login: <code>{j.get("login")}</code> | Nascimento: {j.get("nascimento")}</p>'
                        f'</div>',
                        unsafe_allow_html=True
                    )
                    idx_real = st.session_state.jogadoras.index(j)
                    col_ap1, col_ap2 = st.columns(2)
                    with col_ap1:
                        if st.button(f"Aprovar {j.get('nome')}", key=f"aprov_{idx_real}"):
                            st.session_state.jogadoras[idx_real]["status"] = "Ativo"
                            salvar_dados(DATA_FILE, st.session_state.jogadoras)
                            st.success("Atleta aprovada com sucesso!")
                            st.rerun()
                    with col_ap2:
                        if st.button(f"Rejeitar {j.get('nome')}", key=f"rej_{idx_real}"):
                            st.session_state.jogadoras.pop(idx_real)
                            salvar_dados(DATA_FILE, st.session_state.jogadoras)
                            st.rerun()

        st.markdown("---")
        st.markdown("### ⚙️ Configurações Gerais do Sistema")
        with st.form("form_config_geral"):
            cfg_vagas = st.number_input("Limite de Vagas Oficiais", min_value=2, max_value=50, value=int(st.session_state.avisos.get("limite_vagas", 15)))
            cfg_pix = st.text_input("Chave Pix Oficial", value=st.session_state.avisos.get("pix", ""))
            cfg_banco = st.text_input("Nome do Banco", value=st.session_state.avisos.get("banco", ""))
            cfg_benef = st.text_input("Nome do Beneficiário", value=st.session_state.avisos.get("beneficiario", ""))
            cfg_v_mensal = st.number_input("Valor da Mensalidade (R$)", value=float(st.session_state.avisos.get("valor_mensalidade", 50.0)))
            cfg_v_avulso = st.number_input("Valor Avulso (R$)", value=float(st.session_state.avisos.get("valor_avulso", 15.0)))
            cfg_wpp_adm = st.text_input("Celular WhatsApp do Admin (para avisos)", value=st.session_state.avisos.get("whatsapp_admin", "5531999999999"))
            cfg_senha_adm = st.text_input("Senha de Autorização para Novos Admins", value=st.session_state.avisos.get("senha_autorizacao_admin", "1980"), type="password")
            
            if st.form_submit_button("Salvar Configurações"):
                st.session_state.avisos["limite_vagas"] = int(cfg_vagas)
                st.session_state.avisos["pix"] = cfg_pix
                st.session_state.avisos["banco"] = cfg_banco
                st.session_state.avisos["beneficiario"] = cfg_benef
                st.session_state.avisos["valor_mensalidade"] = float(cfg_v_mensal)
                st.session_state.avisos["valor_avulso"] = float(cfg_v_avulso)
                st.session_state.avisos["whatsapp_admin"] = cfg_wpp_adm
                st.session_state.avisos["senha_autorizacao_admin"] = cfg_senha_adm
                salvar_dados(AVISOS_FILE, st.session_state.avisos)
                st.success("Configurações atualizadas com sucesso!")
                st.rerun()

    elif st.session_state.pagina_atual == "melhorias":
        st.subheader("💡 Sugestões de Melhorias e Inovações para o App")
        st.markdown("""
        <div class="card-team">
            <h4>🚀 Ideias para Evoluir o Peladinha FC</h4>
            <ul>
                <li><b>Notificações Push / Lembrete Automático:</b> Integrar robôs de disparo (ex: Evolution API ou Z-API) para lembrar automaticamente as mensalistas na segunda-feira às 12:00 sobre a confirmação da vaga.</li>
                <li><b>Estatísticas de Partida (Artilharia & Craque da Rodada):</b> Criar uma aba de súmula onde a organizadora possa pontuar gols, assistências e votar na craque do jogo após o apito final.</li>
                <li><b>Gamificação e Ranking:</b> Exibir um ranking mensal com as atletas mais assíduas, fair play e artilheiras para engajar ainda mais o grupo.</li>
                <li><b>Controle de Coletes e Material:</b> Adicionar um campo para sortear qual atleta será responsável por levar os coletes ou a bola na semana.</li>
                <li><b>Backup em Nuvem Automático (Banco de Dados SQL):</b> Migrar os arquivos `.json` locais para um banco de dados relacional gratuito (como Supabase ou PostgreSQL) para garantir multi-acesso simultâneo sem perda de dados.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
