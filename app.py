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

    /* Forçar alta visibilidade em títulos, textos e labels */
    h1, h2, h3, h4, h5, h6, label, p, span, div {
        color: #FFFFFF !important;
        text-shadow: 0px 1px 3px rgba(0,0,0,0.8);
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
        {"data": "2026-08-01", "tipo": "Receita", "descricao": "Mensalidade - Camila Admin", "valor": 50.00, "status": "Pago"},
        {"data": "2026-08-05", "tipo": "Despesa", "descricao": "Aluguel da Quadra", "valor": 200.00, "status": "Pago"}
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
        "valor_avulso": 15.00
    })
if "regulamento" not in st.session_state:
    st.session_state.regulamento = carregar_dados(REGULAMENTO_FILE, [
        {"topico": "📌 1. Prioridade de Mensalistas", "regrinha": "Mensalistas confirmando até as 17:00 de segunda-feira têm prioridade nas 15 vagas."},
        {"topico": "⏳ 2. Fila de Espera de Avulsas", "regrinha": "Avulsas entram na fila de espera. Após las 17:00, se sobrarem vagas, sobem automaticamente."},
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
SENHA_AUTORIZACAO_ADMIN = "1980"

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
                        st.success("Cadastro realizado com sucesso! Aguardando aprovação do Administrador.")
                else:
                    st.error("Preencha todos os campos obrigatórios!")

    elif st.session_state.sub_tela_login == "cad_admin":
        st.subheader("Cadastro de Novo Administrador")
        # Sem clear_on_submit para os dados não sumirem caso digite senha errada
        a_nome = st.text_input("Nome do Administrador *", key="cad_adm_nome")
        a_cel = st.text_input("Celular (WhatsApp) *", placeholder="Ex: 5531999999999", key="cad_adm_cel")
        a_user = st.text_input("Login de Admin *", key="cad_adm_user")
        a_pass = st.text_input("Senha de Acesso *", type="password", key="cad_adm_pass")
        a_aut = st.text_input("Senha de Autorização *", type="password", help="Senha padrão: 1980", key="cad_adm_aut")
        
        if st.button("CADASTRAR ADMINISTRADOR", key="btn_sub_adm_custom"):
            if a_aut.strip() == SENHA_AUTORIZACAO_ADMIN:
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
    
    st.markdown(
        f'<div style="text-align: center; margin-bottom: 20px;">'
        f'<span style="background-color: rgba(236, 72, 153, 0.25); color: #FFFFFF; padding: 6px 16px; border-radius: 20px; font-size: 0.95rem; font-weight: 700; border: 1px solid #EC4899;">'
        f'👤 Logado como: <b>{st.session_state.usuario_logado}</b> ({st.session_state.perfil_logado})'
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
            ("🎂 **Aniversariantes do Mês**\n\nParabéns e felicitações", "aniversariantes")
        ]

        if st.session_state.perfil_logado in ["Admin", "Dev"]:
            cards.append(("📸 **Fluxo de Caixa**\n\nReceitas, despesas e mensalistas", "caixa"))
            cards.append(("⚙️ **Gerenciamento Geral**\n\nAprovações e credenciais", "gerenciamento"))

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
                    st.markdown(f'<div class="card-team" style="border-color: #EC4899; box-shadow: 0 0 15px rgba(236,72,153,0.5);"><h3>🥳 HOJE É ANIVERSÁRIO DE: {a["nome"]}! 🎂</h3><p>Mensagem automática enviada: <b>"Feliz Aniversário, {a["nome"]}! Muita saúde, alegria e gols!"</b> 💖</p></div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="card-team"><h3>🎉 {a["nome"]}</h3><p>Data: <b>{nasc_str}</b></p></div>', unsafe_allow_html=True)
            
            st.markdown("---")
            st.info("💌 Mensagem disparada para o grupo lembrando todas as atletas de parabenizarem as aniversariantes do dia!")

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
                st.markdown(f'<div class="card-team"><b>{i}.</b> {obter_nome_p(p)} <code>[{obter_tipo_p(p)}]</code></div>', unsafe_allow_html=True)

            st.write(f"### ⏳ Fila de Espera ({len(espera)})")
            for i, p in enumerate(espera, 1):
                st.markdown(f'<div class="card-team"><b>{i}º:</b> {obter_nome_p(p)} <code>[{obter_tipo_p(p)}]</code></div>', unsafe_allow_html=True)

        with col_l2:
            if st.session_state.perfil_logado in ["Admin", "Dev"]:
                st.write("### 👑 Inclusão pelo Admin")
                
                # Opção 1: Incluir Jogadora Cadastrada
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

                # Opção 2: Incluir Convidada Avulsa
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
                if c_ok and not ja_esta:
                    st.session_state.presencas.append({"nome": j_name, "hora": hoje_dt.strftime("%H:%M"), "tipo": tipo_usuario_atual, "dt_confirmacao": hoje_dt.isoformat()})
                    salvar_dados(PRESENCAS_FILE, st.session_state.presencas)
                    st.rerun()
                if c_canc and ja_esta:
                    st.session_state.presencas = [p for p in st.session_state.presencas if obter_nome_p(p) != j_name]
                    salvar_dados(PRESENCAS_FILE, st.session_state.presencas)
                    st.rerun()

    elif st.session_state.pagina_atual == "sorteio":
        st.subheader("🏆 Sorteio de Times & Grupos (Às 18:30)")
        
        st.markdown("### 🤖 Sorteio Oficial Automático (Grupos)")
        nomes_oficiais = [obter_nome_p(p) for p in st.session_state.presencas][:15]
        
        if st.session_state.perfil_logado in ["Admin", "Dev"]:
            with st.expander("🛠️ Editar Participantes do Sorteio Oficial"):
                nomes_editados = st.multiselect("Selecione as atletas presentes para o sorteio:", [j["nome"] for j in st.session_state.jogadoras if j.get("status"] == "Ativo"], default=nomes_oficiais if nomes_oficiais else None)
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
                random.shuffle(lista_paralela)
                met = len(lista_paralela) // 2
                t1 = lista_paralela[:met]
                t2 = lista_paralela[met:]
                st.markdown(f'<div class="card-team"><h4>⚽ Time Paralelo 1</h4>' + "".join([f"<p>• {n}</p>" for n in t1]) + '</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="card-team"><h4>⚽ Time Paralelo 2</h4>' + "".join([f"<p>• {n}</p>" for n in t2]) + '</div>', unsafe_allow_html=True)
            else:
                st.error("Digite os nomes para o sorteio paralelo.")

    elif st.session_state.pagina_atual == "elenco":
        st.subheader("👕 Elenco de Jogadoras")
        for j in st.session_state.jogadoras:
            status_cor = "🟢 Ativa" if j.get("status") == "Ativo" else "🔴 Inativa"
            pag_cor = "✅ Em Dia" if j.get("quitado") == "Sim" else "❌ Pendente"
            st.markdown(f'<div class="card-team"><b>{j["nome"]}</b> | Tipo: <code>{j.get("tipo")}</code> | Status: <b>{status_cor}</b> | Pagamento: <b>{pag_cor}</b></div>', unsafe_allow_html=True)

    elif st.session_state.pagina_atual == "pagamento":
        st.subheader("💳 Chave Pix e Dados para Pagamento")
        
        # Opção do Admin para editar os dados do Pix
        if st.session_state.perfil_logado in ["Admin", "Dev"]:
            with st.expander("🛠️ Editar Dados de Pagamento / Chave Pix"):
                with st.form("form_edit_pix"):
                    novo_pix = st.text_input("Chave Pix", value=st.session_state.avisos.get("pix", ""))
                    novo_banco = st.text_input("Banco", value=st.session_state.avisos.get("banco", ""))
                    novo_beneficiario = st.text_input("Beneficiário", value=st.session_state.avisos.get("beneficiario", ""))
                    v_mensal_novo = st.number_input("Valor Mensalidade (R$)", value=float(st.session_state.avisos.get("valor_mensalidade", 50.0)))
                    v_avulso_novo = st.number_input("Valor Avulso (R$)", value=float(st.session_state.avisos.get("valor_avulso", 15.0)))
                    
                    if st.form_submit_button("Salvar Alterações de Pagamento"):
                        st.session_state.avisos["pix"] = novo_pix
                        st.session_state.avisos["banco"] = novo_banco
                        st.session_state.avisos["beneficiario"] = novo_beneficiario
                        st.session_state.avisos["valor_mensalidade"] = v_mensal_novo
                        st.session_state.avisos["valor_avulso"] = v_avulso_novo
                        salvar_dados(AVISOS_FILE, st.session_state.avisos)
                        st.success("Dados de pagamento atualizados com sucesso!")
                        st.rerun()

        tipo_atual = "Avulso"
        nome_logado = st.session_state.usuario_logado
        for j in st.session_state.jogadoras:
            if j.get("nome") == nome_logado:
                tipo_atual = j.get("tipo", "Avulso")
        
        v_mensal = st.session_state.avisos.get("valor_mensalidade", 50.00)
        v_avulso = st.session_state.avisos.get("valor_avulso", 15.00)
        valor_devido = v_mensal if tipo_atual == "Mensalista" else v_avulso

        st.markdown(f"""
        <div class="card-team">
            <h4>🏷️ Informações de Pagamento ({tipo_atual})</h4>
            <p>Valor correspondente à sua categoria: <b>R$ {valor_devido:.2f}</b></p>
            <hr style="border-color: #374151;">
            <p><b>Chave Pix:</b> <code>{st.session_state.avisos.get("pix")}</code></p>
            <p><b>Banco:</b> {st.session_state.avisos.get("banco", "Banco Inter")}</p>
            <p><b>Beneficiário:</b> {st.session_state.avisos.get("beneficiario", "Peladinha FC")}</p>
        </div>
        """, unsafe_allow_html=True)

        # Habilitar envio de comprovante para Jogadoras e Admin se testando
        if st.session_state.perfil_logado in ["Jogadora", "Admin", "Dev"]:
            with st.form("form_comp"):
                # Se for admin, pode escolher qual jogadora está enviando o comprovante
                if st.session_state.perfil_logado in ["Admin", "Dev"]:
                    nomes_joga_pag = [j["nome"] for j in st.session_state.jogadoras]
                    atleta_selecionada_comp = st.selectbox("Enviar em nome de:", nomes_joga_pag if nomes_joga_pag else [st.session_state.usuario_logado])
                else:
                    atleta_selecionada_comp = st.session_state.usuario_logado

                up = st.file_uploader("Enviar Comprovante de Pagamento", type=["png", "jpg", "jpeg"])
                if st.form_submit_button("Enviar Comprovante para o Admin"):
                    if up:
                        path = os.path.join(UPLOAD_DIR, f"{atleta_selecionada_comp}.png")
                        with open(path, "wb") as f: f.write(up.getbuffer())
                        st.session_state.comprovantes.append({"nome": atleta_selecionada_comp, "arquivo": path, "valor": valor_devido, "tipo": tipo_atual, "conferido": False})
                        salvar_dados(COMPROVANTES_FILE, st.session_state.comprovantes)
                        st.success("Comprovante enviado com sucesso para validação do Administrador!")

    elif st.session_state.pagina_atual == "caixa":
        st.subheader("📸 Fluxo de Caixa e Acompanhamento de Mensalistas")
        
        if st.session_state.comprovantes:
            st.write("### 📥 Comprovantes Pendentes de Aprovação")
            for idx, comp in enumerate(st.session_state.comprovantes):
                if not comp.get("conferido"):
                    st.markdown(f'<div class="card-team">Atleta: <b>{comp["nome"]}</b> | Valor: R$ {comp.get("valor", 0):.2f}</div>', unsafe_allow_html=True)
                    if st.button(f"Aprovar e Lançar no Caixa ({comp['nome']})", key=f"apr_comp_{idx}"):
                        comp["conferido"] = True
                        st.session_state.financeiro.append({
                            "data": hoje_dt.strftime("%Y-%m-%d"),
                            "tipo": "Receita",
                            "descricao": f"Pagamento - {comp['nome']}",
                            "valor": comp.get("valor", 0),
                            "status": "Pago"
                        })
                        for j in st.session_state.jogadoras:
                            if j["nome"] == comp["nome"]:
                                j["quitado"] = "Sim"
                        salvar_dados(FINANCE_FILE, st.session_state.financeiro)
                        salvar_dados(COMPROVANTES_FILE, st.session_state.comprovantes)
                        salvar_dados(DATA_FILE, st.session_state.jogadoras)
                        st.success("Pagamento aprovado e lançado no caixa com sucesso!")
                        st.rerun()

        with st.expander("➕ Lançar Nova Receita / Despesa"):
            with st.form("form_novo_fluxo"):
                f_tipo = st.selectbox("Tipo", ["Receita", "Despesa"])
                f_desc = st.text_input("Descrição (Ex: Aluguel da Quadra / Compra de Coletes)")
                f_val = st.number_input("Valor (R$)", min_value=0.0, value=50.0)
                f_status = st.selectbox("Status", ["Pago", "Pendente"])
                if st.form_submit_button("Salvar Lançamento"):
                    if f_desc:
                        st.session_state.financeiro.append({
                            "data": hoje_dt.strftime("%Y-%m-%d"),
                            "tipo": f_tipo, "descricao": f_desc, "valor": f_val, "status": f_status
                        })
                        salvar_dados(FINANCE_FILE, st.session_state.financeiro)
                        st.success("Lançamento adicionado!")
                        st.rerun()

        total_rec = sum(i["valor"] for i in st.session_state.financeiro if i["tipo"] == "Receita" and i["status"] == "Pago")
        total_desp = sum(i["valor"] for i in st.session_state.financeiro if i["tipo"] == "Despesa" and i["status"] == "Pago")
        saldo_geral = total_rec - total_desp

        col_c1, col_c2, col_c3 = st.columns(3)
        with col_c1:
            st.metric("Receitas Pagas", f"R$ {total_rec:.2f}")
        with col_c2:
            st.metric("Despesas Pagas", f"R$ {total_desp:.2f}")
        with col_c3:
            st.metric("Saldo em Caixa", f"R$ {saldo_geral:.2f}")

        st.write("### 📋 Lançamentos Registrados (Mensal / Semanal)")
        for lanc in st.session_state.financeiro:
            cor_st = "🟢 Pago" if lanc.get("status") == "Pago" else "🟠 Pendente"
            st.markdown(f'<div class="card-team"><b>[{lanc["tipo"]}]</b> {lanc["descricao"]} — <b>R$ {lanc["valor"]:.2f}</b> | Status: <b>{cor_st}</b> ({lanc.get("data")})</div>', unsafe_allow_html=True)

        st.write("### 👥 Acompanhamento de Pagamento das Mensalistas")
        for j in st.session_state.jogadoras:
            if j.get("tipo") == "Mensalista":
                st.markdown(f'<div class="card-team">Mensalista: <b>{j["nome"]}</b> — Situação: <b>{"✅ Em Dia" if j.get("quitado")=="Sim" else "❌ Pendente"}</b></div>', unsafe_allow_html=True)

    elif st.session_state.pagina_atual == "gerenciamento":
        st.subheader("🛠️ Gerenciamento Geral & Credenciais")
        
        if st.session_state.perfil_logado == "Dev":
            st.write("### 🔐 [DEV] Credenciais de Acesso de Todas as Contas")
            for adm in st.session_state.administradores:
                st.markdown(f'<div class="card-team">Admin: <b>{adm["nome"]}</b> | Login: <code>{adm["login"]}</code> | Senha: <code>{adm["senha"]}</code></div>', unsafe_allow_html=True)
            for j in st.session_state.jogadoras:
                st.markdown(f'<div class="card-team">Atleta: <b>{j["nome"]}</b> | Login: <code>{j.get("login")}</code> | Senha: <code>{j.get("senha")}</code></div>', unsafe_allow_html=True)
            st.markdown("---")

        st.write("### 👑 Aprovação de Cadastros Pendentes")
        pendentes_j = [item for item in st.session_state.jogadoras if item.get("status") == "Pendente"]
        if not pendentes_j:
            st.info("Nenhum cadastro de atleta pendente no momento.")
        else:
            for j in pendentes_j:
                st.markdown(f'<div class="card-team">Atleta Pendente: <b>{j["nome"]}</b> ({j.get("tipo")})</div>', unsafe_allow_html=True)
                if st.button(f"Aprovar Atleta {j['nome']}", key=f"ap_{j['nome']}"):
                    j["status"] = "Ativo"
                    salvar_dados(DATA_FILE, st.session_state.jogadoras)
                    st.success("Atleta aprovada com sucesso!")
                    st.rerun()

        st.markdown("---")
        st.write("### ✏️ Gerenciar / Editar / Excluir Cadastros")

        tab_g1, tab_g2 = st.tabs(["Jogadoras", "Administradores"])

        with tab_g1:
            for idx, j in enumerate(st.session_state.jogadoras):
                with st.expander(f"Jogadora: {j['nome']} ({j.get('tipo', 'Avulso')})"):
                    with st.form(f"form_edit_jog_{idx}"):
                        novo_nome_j = st.text_input("Nome", value=j["nome"])
                        novo_tipo_j = st.selectbox("Tipo", ["Avulso", "Mensalista"], index=0 if j.get("tipo") == "Avulso" else 1)
                        novo_status_j = st.selectbox("Status", ["Ativo", "Pendente", "Inativo"], index=0 if j.get("status") == "Ativo" else (1 if j.get("status") == "Pendente" else 2))
                        novo_quitado_j = st.selectbox("Quitado", ["Sim", "Não"], index=0 if j.get("quitado") == "Sim" else 1)
                        novo_login_j = st.text_input("Login", value=j.get("login", ""))
                        novo_senha_j = st.text_input("Senha", value=j.get("senha", ""))

                        btn_salvar_j = st.form_submit_button("Salvar Alterações da Atleta")
                        if btn_salvar_j:
                            j["nome"] = novo_nome_j
                            j["tipo"] = novo_tipo_j
                            j["status"] = novo_status_j
                            j["quitado"] = novo_quitado_j
                            j["login"] = novo_login_j
                            j["senha"] = novo_senha_j
                            salvar_dados(DATA_FILE, st.session_state.jogadoras)
                            st.success("Atleta atualizada com sucesso!")
                            st.rerun()

                    if st.button(f"🗑️ Excluir Atleta {j['nome']}", key=f"del_jog_{idx}"):
                        st.session_state.jogadoras.pop(idx)
                        salvar_dados(DATA_FILE, st.session_state.jogadoras)
                        st.success("Atleta excluída com sucesso!")
                        st.rerun()

        with tab_g2:
            for idx, adm in enumerate(st.session_state.administradores):
                # Proteger o Admin Principal / Desenvolvedor se necessário, permitindo exclusão dos demais
                is_admin_principal = adm.get("login") == "admin"
                with st.expander(f"Administrador: {adm['nome']} ({adm.get('login')})"):
                    with st.form(f"form_edit_adm_{idx}"):
                        novo_nome_a = st.text_input("Nome", value=adm["nome"])
                        novo_cel_a = st.text_input("Celular", value=adm.get("celular", ""))
                        novo_login_a = st.text_input("Login", value=adm.get("login", ""))
                        novo_senha_a = st.text_input("Senha", value=adm.get("senha", ""))

                        btn_salvar_a = st.form_submit_button("Salvar Alterações do Admin")
                        if btn_salvar_a:
                            adm["nome"] = novo_nome_a
                            adm["celular"] = novo_cel_a
                            adm["login"] = novo_login_a
                            adm["senha"] = novo_senha_a
                            salvar_dados(ADMINS_FILE, st.session_state.administradores)
                            st.success("Administrador atualizado com sucesso!")
                            st.rerun()

                    if not is_admin_principal:
                        if st.button(f"🗑️ Excluir Administrador {adm['nome']}", key=f"del_adm_{idx}"):
                            st.session_state.administradores.pop(idx)
                            salvar_dados(ADMINS_FILE, st.session_state.administradores)
                            st.success("Administrador excluído com sucesso!")
                            st.rerun()
                    else:
                        st.info("O Administrador Principal padrão não pode ser excluído.")
