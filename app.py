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

    /* BOTÕES GERAIS E DE FORMULÁRIOS COM TEXTO VISÍVEL E BRANCO */
    div.stButton > button:first-child, div.stFormSubmitButton > button {
        background: linear-gradient(135deg, rgba(22, 30, 46, 0.95) 0%, rgba(15, 23, 42, 0.95) 100%) !important;
        color: #FFFFFF !important;
        font-weight: 700 !important;
        border-radius: 16px !important;
        border: 1px solid #EC4899 !important;
        padding: 14px 20px !important;
        box-shadow: 0 0 12px rgba(236, 72, 153, 0.25) !important;
        transition: all 0.3s ease !important;
    }
    
    div.stButton > button:first-child:hover, div.stFormSubmitButton > button:hover {
        border-color: #F472B6 !important;
        box-shadow: 0 0 20px rgba(236, 72, 153, 0.5) !important;
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.95) 0%, rgba(22, 30, 46, 0.95) 100%) !important;
        color: #FFFFFF !important;
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
            st.info("São necessárias pelo menos 2 atletas confirmadas para realizar o sorteio automático.")

    elif st.session_state.pagina_atual == "elenco":
        st.subheader("👕 Elenco de Jogadoras Cadastradas")
        for j in st.session_state.jogadoras:
            st.markdown(f'<div class="card-team"><h3>{j["nome"]}</h3><p>Tipo: <b>{j.get("tipo")}</b> | Status: <b>{j.get("status")}</b> | Quitado: <b>{j.get("quitado")}</b></p></div>', unsafe_allow_html=True)

    elif st.session_state.pagina_atual == "pagamento":
        st.subheader("💠 Informações de Pagamento e Pix")
        av = st.session_state.avisos
        st.markdown(f'''
        <div class="card-team">
            <h3>💳 Dados para Transferência / PIX</h3>
            <p><b>Chave PIX:</b> <code>{av.get("pix")}</code></p>
            <p><b>Banco:</b> {av.get("banco")}</p>
            <p><b>Beneficiário:</b> {av.get("beneficiario")}</p>
            <p><b>Valor Mensalidade:</b> R$ {av.get("valor_mensalidade"):.2f} ({av.get("vencimento")})</p>
            <p><b>Valor Avulso:</b> R$ {av.get("valor_avulso"):.2f}</p>
        </div>
        ''', unsafe_allow_html=True)

        st.write("### 📤 Enviar Comprovante de Pagamento")
        with st.form("form_comprovante", clear_on_submit=True):
            arq_comp = st.file_uploader("Selecione a imagem do comprovante", type=["png", "jpg", "jpeg"])
            desc_comp = st.text_input("Descrição / Referência", placeholder="Ex: Mensalidade Agosto - Nome")
            if st.form_submit_button("Enviar Comprovante"):
                if arq_comp:
                    file_path = os.path.join(UPLOAD_DIR, f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{arq_comp.name}")
                    with open(file_path, "wb") as f:
                        f.write(arq_comp.getbuffer())
                    
                    st.session_state.comprovantes.append({
                        "atleta": st.session_state.usuario_logado or "Anônimo",
                        "descricao": desc_comp,
                        "arquivo": file_path,
                        "data": hoje_dt.strftime("%d/%m/%Y %H:%M"),
                        "status": "Pendente"
                    })
                    salvar_dados(COMPROVANTES_FILE, st.session_state.comprovantes)
                    st.success("Comprovante enviado com sucesso para análise do Administrador!")
                else:
                    st.error("Envie um arquivo de imagem.")

    elif st.session_state.pagina_atual == "melhorias":
        st.subheader("💡 Sugestões de Melhorias")
        with st.form("form_sugestoes", clear_on_submit=True):
            sugestao = st.text_area("Deixe sua ideia ou sugestão para o app:")
            if st.form_submit_button("Enviar Sugestão"):
                if sugestao.strip():
                    st.success("Sugestão enviada com sucesso! Obrigado pela colaboração.")
                else:
                    st.error("Escreva alguma sugestão.")

    elif st.session_state.pagina_atual == "caixa":
        st.subheader("📸 Fluxo de Caixa & Finanças")
        total_rec = sum(f["valor"] for f in st.session_state.financeiro if f["tipo"] == "Receita" and f["status"] == "Pago")
        total_desp = sum(f["valor"] for f in st.session_state.financeiro if f["tipo"] == "Despesa" and f["status"] == "Pago")
        
        col_c1, col_c2, col_c3 = st.columns(3)
        col_c1.metric("Receitas", f"R$ {total_rec:.2f}")
        col_c2.metric("Despesas", f"R$ {total_desp:.2f}")
        col_c3.metric("Saldo Atual", f"R$ {total_rec - total_desp:.2f}")

        st.write("### 📋 Lançamentos Financeiros")
        for f in st.session_state.financeiro:
            st.markdown(f'<div class="card-team"><b>{f["data"]}</b> | {f["tipo"]}: {f["descricao"]} — <b>R$ {f["valor"]:.2f}</b> [{f["status"]}]</div>', unsafe_allow_html=True)

        if st.session_state.comprovantes:
            st.write("### 🔍 Comprovantes Enviados para Análise")
            for idx, comp in enumerate(st.session_state.comprovantes):
                nome_atleta_comp = comp.get("atleta") or comp.get("nome") or "Desconhecido"
                desc_comp = comp.get("descricao") or "Sem descrição"
                data_comp = comp.get("data") or "Data não informada"
                status_comp = comp.get("status") or "Pendente"
                
                st.markdown(f'<div class="card-team"><b>Atleta:</b> {nome_atleta_comp} <br><b>Descrição:</b> {desc_comp} <br><b>Data:</b> {data_comp} <br><b>Status:</b> {status_comp}</div>', unsafe_allow_html=True)
                
                arq_path = comp.get("arquivo")
                if arq_path and os.path.exists(arq_path):
                    st.image(arq_path, width=250)
                
                if status_comp == "Pendente":
                    if st.button(f"Aprovar Comprovante {idx}", key=f"apr_comp_{idx}"):
                        st.session_state.comprovantes[idx]["status"] = "Aprovado"
                        salvar_dados(COMPROVANTES_FILE, st.session_state.comprovantes)
                        st.success("Comprovante aprovado!")
                        st.rerun()

    elif st.session_state.pagina_atual == "gerenciamento":
        st.subheader("⚙️ Gerenciamento Geral e Aprovações")
        
        pendentes = [j for j in st.session_state.jogadoras if j.get("status") == "Pendente"]
        if not pendentes:
            st.info("Nenhum cadastro pendente no momento.")
        else:
            st.write("### 👥 Cadastros Pendentes de Aprovação")
            for j in pendentes:
                st.markdown(f'<div class="card-team"><b>{j["nome"]}</b> ({j.get("tipo")}) — Login: <code>{j.get("login")}</code></div>', unsafe_allow_html=True)
                col_a, col_b = st.columns(2)
                with col_a:
                    if st.button(f"Aprovar {j['nome']}", key=f"aprov_{j['login']}"):
                        j["status"] = "Ativo"
                        salvar_dados(DATA_FILE, st.session_state.jogadoras)
                        st.success(f"{j['nome']} aprovada com sucesso!")
                        st.rerun()
                with col_b:
                    if st.button(f"Recusar {j['nome']}", key=f"rec_{j['login']}"):
                        st.session_state.jogadoras = [item for item in st.session_state.jogadoras if item.get("login") != j.get("login")]
                        salvar_dados(DATA_FILE, st.session_state.jogadoras)
                        st.success(f"Cadastro de {j['nome']} removido.")
                        st.rerun()

        st.write("### 🛠️ Configurações Gerais do Aplicativo")
        with st.form("form_config_geral"):
            novo_limite = st.number_input("Limite de Vagas Oficiais", value=int(st.session_state.avisos.get("limite_vagas", 15)), step=1)
            novo_val_mensal = st.number_input("Valor da Mensalidade (R$)", value=float(st.session_state.avisos.get("valor_mensalidade", 50.0)), step=5.0)
            novo_val_avulso = st.number_input("Valor Avulso (R$)", value=float(st.session_state.avisos.get("valor_avulso", 15.0)), step=5.0)
            nova_chave_pix = st.text_input("Chave Pix", value=st.session_state.avisos.get("pix", ""))
            
            if st.form_submit_button("Salvar Configurações"):
                st.session_state.avisos["limite_vagas"] = int(novo_limite)
                st.session_state.avisos["valor_mensalidade"] = float(novo_val_mensal)
                st.session_state.avisos["valor_avulso"] = float(novo_val_avulso)
                st.session_state.avisos["pix"] = nova_chave_pix
                salvar_dados(AVISOS_FILE, st.session_state.avisos)
                st.success("Configurações atualizadas com sucesso!")
                st.rerun()

    elif st.session_state.pagina_atual == "credenciais":
        st.subheader("🔑 Credenciais e Controles de Acesso (DEV)")
        st.write("### Administradores Cadastrados")
        for adm in st.session_state.administradores:
            st.markdown(f'<div class="card-team"><b>Nome:</b> {adm["nome"]} <br><b>Login:</b> <code>{adm["login"]}</code> <br><b>Senha:</b> <code>{adm["senha"]}</code></div>', unsafe_allow_html=True)
        
        st.write("### Atletas Cadastradas")
        for j in st.session_state.jogadoras:
            st.markdown(f'<div class="card-team"><b>Nome:</b> {j["nome"]} <br><b>Login:</b> <code>{j.get("login")}</code> <br><b>Senha:</b> <code>{j.get("senha")}</code></div>', unsafe_allow_html=True)
