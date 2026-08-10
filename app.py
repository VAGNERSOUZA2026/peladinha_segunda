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
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------------------------------------------------------
# ESTILIZAÇÃO CSS CUSTOMIZADA
# -----------------------------------------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] { 
        font-family: 'Montserrat', sans-serif; 
    }

    .stApp {
        background-color: #111827;
        color: #F3F4F6;
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
        color: #9CA3AF;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    .card-team {
        background: #1F2937;
        border: 1px solid #374151;
        border-top: 4px solid #0D9488;
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 15px;
    }

    div.stButton > button:first-child {
        background-color: #0D9488 !important;
        color: #FFFFFF !important;
        font-weight: 700 !important;
        border-radius: 10px !important;
        border: 1px solid #14B8A6 !important;
        padding: 10px 20px !important;
        box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.2);
    }
    div.stButton > button:first-child:hover {
        background-color: #0F766E !important;
        border-color: #2DD4BF !important;
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
# TRATAMENTO DE DADOS (ARQUIVOS JSON)
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
    st.session_state.financeiro = carregar_dados(FINANCE_FILE, [])
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

if "usuario_logado" not in st.session_state:
    st.session_state.usuario_logado = None
if "admin_logged" not in st.session_state:
    st.session_state.admin_logged = False
if "dev_logged" not in st.session_state:
    st.session_state.dev_logged = False
if "admin_nome" not in st.session_state:
    st.session_state.admin_nome = ""

# Senha mestre exclusiva do Desenvolvedor
SENHA_MESTRE_DEV = "dev@peladinha2026"

# -----------------------------------------------------------------------------
# BARRA LATERAL (AUTENTICAÇÃO E ACESSOS)
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### ⚙️ Acesso & Contas")
    
    if st.session_state.usuario_logado:
        st.success(f"Atleta: **{st.session_state.usuario_logado}**")
        if st.button("🚪 Sair da Conta", use_container_width=True):
            st.session_state.usuario_logado = None
            st.rerun()
    else:
        st.subheader("🔑 Entrar")
        with st.form("form_login_player"):
            l_user = st.text_input("Login")
            l_pass = st.text_input("Senha", type="password")
            if st.form_submit_button("Entrar", use_container_width=True):
                user_found = next((j for j in st.session_state.jogadoras if j.get("login") == l_user and j.get("senha") == l_pass), None)
                if user_found:
                    if user_found.get("status") == "Pendente":
                        st.warning("Seu cadastro aguarda aprovação de um Administrador.")
                    else:
                        st.session_state.usuario_logado = user_found["nome"]
                        st.rerun()
                else:
                    st.error("Login ou senha incorretos!")

        st.markdown("---")
        st.subheader("📝 Cadastrar Nova Atleta")
        with st.form("form_cad_player", clear_on_submit=True):
            c_nome = st.text_input("Seu Nome *")
            c_nasc = st.text_input("Nascimento (DD/MM) *", placeholder="Ex: 15/05")
            c_tipo = st.selectbox("Tipo:", ["Avulso", "Mensalista"])
            c_user = st.text_input("Login *")
            c_pass = st.text_input("Senha *", type="password")
            if st.form_submit_button("Cadastrar", use_container_width=True):
                if c_nome and c_user and c_pass:
                    if any(j.get("login") == c_user.strip() for j in st.session_state.jogadoras):
                        st.error("Login já em uso!")
                    else:
                        st.session_state.jogadoras.append({
                            "nome": c_nome.strip(), "nascimento": c_nasc.strip(),
                            "login": c_user.strip(), "senha": c_pass.strip(),
                            "tipo": c_tipo, "status": "Pendente", "quitado": "Não"
                        })
                        salvar_dados(DATA_FILE, st.session_state.jogadoras)
                        st.success("Cadastro realizado! Aguarde a aprovação do Administrador.")
                else:
                    st.error("Preencha todos os campos obrigatórios!")

    st.markdown("---")
    st.subheader("🔒 Área Administrativa")
    if not st.session_state.admin_logged:
        with st.form("form_login_admin"):
            adm_user = st.text_input("Login Admin")
            adm_pass = st.text_input("Senha Admin", type="password")
            if st.form_submit_button("Acessar Admin", use_container_width=True):
                admin_encontrado = next((adm for adm in st.session_state.administradores if adm.get("login") == adm_user and adm.get("senha") == adm_pass), None)
                if admin_encontrado:
                    st.session_state.admin_logged = True
                    st.session_state.admin_nome = admin_encontrado["nome"]
                    st.rerun()
                else:
                    st.error("Credenciais incorretas!")
    else:
        st.info(f"Admin: **{st.session_state.admin_nome}**")
        if st.button("Sair do Admin", use_container_width=True):
            st.session_state.admin_logged = False
            st.rerun()

    st.markdown("---")
    st.subheader("🛠️ Área do Desenvolvedor")
    if not st.session_state.dev_logged:
        with st.form("form_login_dev"):
            dev_pass = st.text_input("Senha Mestre", type="password")
            if st.form_submit_button("Acessar Dev", use_container_width=True):
                if dev_pass == SENHA_MESTRE_DEV:
                    st.session_state.dev_logged = True
                    st.rerun()
                else:
                    st.error("Senha mestre incorreta!")
    else:
        st.success("Modo Desenvolvedor Ativo")
        if st.button("Sair do Dev", use_container_width=True):
            st.session_state.dev_logged = False
            st.rerun()

# -----------------------------------------------------------------------------
# CABEÇALHO DO APLICATIVO
# -----------------------------------------------------------------------------
st.markdown("""
<div class='app-header'>
    <div class='app-subtitle'>peladinha fc</div>
    <div class='app-title'>Gestão Inteligente & Resenha</div>
</div>
""", unsafe_allow_html=True)

# Saudação personalizada se logada
if st.session_state.usuario_logado:
    st.markdown(f"### 👋 Olá, **{st.session_state.usuario_logado}**! Seja bem-vinda de volta.")

# -----------------------------------------------------------------------------
# PAINEL DO DESENVOLVEDOR (GERENCIAMENTO DE CREDENCIAIS DE ADMINS)
# -----------------------------------------------------------------------------
if st.session_state.dev_logged:
    st.markdown("---")
    st.markdown("## 🛠️ Painel Exclusivo do Desenvolvedor - Gerenciamento de Administradores")
    
    col_d1, col_d2 = st.columns(2)
    with col_d1:
        st.write("### ➕ Cadastrar Novo Administrador")
        with st.form("form_novo_admin", clear_on_submit=True):
            novo_adm_nome = st.text_input("Nome do Admin")
            novo_adm_login = st.text_input("Login do Admin")
            novo_adm_senha = st.text_input("Senha do Admin", type="password")
            if st.form_submit_button("Criar Administrador"):
                if novo_adm_nome and novo_adm_login and novo_adm_senha:
                    st.session_state.administradores.append({
                        "nome": novo_adm_nome, "login": novo_adm_login, "senha": novo_adm_senha
                    })
                    salvar_dados(ADMINS_FILE, st.session_state.administradores)
                    st.success("Administrador cadastrado com sucesso!")
                    st.rerun()
                else:
                    st.error("Preencha todos os campos!")

    with col_d2:
        st.write("### 📋 Administradores Cadastrados")
        for idx, adm in enumerate(st.session_state.administradores):
            st.markdown(f"<div class='card-team'><b>Nome:</b> {adm['nome']} | <b>Login:</b> <code>{adm['login']}</code></div>", unsafe_allow_html=True)
            if st.button(f"Excluir Admin {adm['nome']}", key=f"del_adm_{idx}"):
                if len(st.session_state.administradores) > 1:
                    st.session_state.administradores.pop(idx)
                    salvar_dados(ADMINS_FILE, st.session_state.administradores)
                    st.success("Administrador removido!")
                    st.rerun()
                else:
                    st.error("Você não pode excluir o último administrador ativo.")

st.markdown("---")

# -----------------------------------------------------------------------------
# PAINEL DO ADMINISTRADOR (APROVAÇÕES E GESTÃO DA LISTA)
# -----------------------------------------------------------------------------
if st.session_state.admin_logged:
    st.markdown("## 👑 Painel do Administrador")
    tab_adm1, tab_adm2, tab_adm3, tab_adm4 = st.tabs(["📝 Aprovar Cadastros", "👥 Gerenciar Presenças", "💸 Comprovantes Pix", "⚙️ Configurações"])
    
    with tab_adm1:
        st.subheader("Aprovação de Novas Jogadoras")
        pendentes = [j for j in st.session_state.jogadoras if j.get("status") == "Pendente"]
        if not pendentes:
            st.info("Nenhum cadastro pendente no momento.")
        for idx, j in enumerate(pendentes):
            col_p1, col_p2, col_p3 = st.columns([2, 1, 1])
            with col_p1:
                st.write(f"**{j['nome']}** (`{j.get('tipo', 'Avulso')}`) - Nasc: {j.get('nascimento')}")
            with col_p2:
                if st.button("✅ Aprovar", key=f"aprov_{idx}"):
                    j["status"] = "Ativo"
                    salvar_dados(DATA_FILE, st.session_state.jogadoras)
                    st.success(f"Atleta {j['nome']} aprovada!")
                    st.rerun()
            with col_p3:
                if st.button("❌ Recusar", key=f"rec_{idx}"):
                    st.session_state.jogadoras.remove(j)
                    salvar_dados(DATA_FILE, st.session_state.jogadoras)
                    st.warning("Cadastro removido.")
                    st.rerun()

    with tab_adm2:
        st.subheader("Inclusão/Exclusão Manual de Confirmadas")
        with st.form("form_add_manual"):
            ativas_nomes = [j["nome"] for j in st.session_state.jogadoras if j.get("status") == "Ativo"]
            atleta_escolhida = st.selectbox("Selecione a Atleta", atativas_nomes)
            if st.form_submit_button("Forçar Inclusão na Lista"):
                if atleta_escolhida and not any(obter_nome_p(p) == atleta_escolhida for p in st.session_state.presencas):
                    dados_j = next((j for j in st.session_state.jogadoras if j["nome"] == atleta_escolhida), None)
                    st.session_state.presencas.append({
                        "nome": atleta_escolhida,
                        "hora": hoje_dt.strftime("%H:%M"),
                        "tipo": dados_j.get("tipo", "Avulso") if dados_j else "Avulso",
                        "dt_confirmacao": hoje_dt.isoformat()
                    })
                    salvar_dados(PRESENCAS_FILE, st.session_state.presencas)
                    st.success("Atleta incluída manualmente!")
                    st.rerun()

        st.write("Remover Atleta da Lista:")
        for p in st.session_state.presencas:
            c_nome = obter_nome_p(p)
            if st.button(f"Remover {c_nome}", key=f"rem_l_{c_nome}"):
                st.session_state.presencas = [item for item in st.session_state.presencas if obter_nome_p(item) != c_nome]
                salvar_dados(PRESENCAS_FILE, st.session_state.presencas)
                st.rerun()

    with tab_adm3:
        st.subheader("Conferência de Comprovantes Pix")
        comprovantes = st.session_state.comprovantes
        if not comprovantes:
            st.info("Nenhum comprovante enviado.")
        for idx, comp in enumerate(comprovantes):
            if not comp.get("conferido", False):
                st.markdown(f"<div class='card-team'><b>Atleta:</b> {comp['nome']} | <b>Data:</b> {comp['data']}</div>", unsafe_allow_html=True)
                if os.path.exists(comp['arquivo']):
                    st.image(comp['arquivo'], width=300)
                if st.button(f"Validar Pagamento de {comp['nome']}", key=f"val_comp_{idx}"):
                    comp["conferido"] = True
                    # Atualizar status quitado da jogadora
                    for j in st.session_state.jogadoras:
                        if j["nome"] == comp["nome"]:
                            j["quitado"] = "Sim"
                    salvar_dados(DATA_FILE, st.session_state.jogadoras)
                    
                    # Alimentar fluxo de caixa
                    st.session_state.financeiro.append({
                        "nome": comp["nome"], "data": hoje_dt.strftime("%d/%m/%Y"), "status": "Quitado"
                    })
                    salvar_dados(FINANCE_FILE, st.session_state.financeiro)
                    salvar_dados(COMPROVANTES_FILE, comprovantes)
                    st.success("Pagamento validado e fluxo de caixa atualizado!")
                    st.rerun()

    with tab_adm4:
        with st.form("form_cfg_geral"):
            limite_v = st.number_input("Limite de Vagas", value=int(st.session_state.avisos.get("limite_vagas", 15)))
            pix_val = st.text_input("Chave Pix", value=st.session_state.avisos.get("pix", ""))
            if st.form_submit_button("Salvar Ajustes"):
                st.session_state.avisos["limite_vagas"] = limite_v
                st.session_state.avisos["pix"] = pix_val
                salvar_dados(AVISOS_FILE, st.session_state.avisos)
                st.success("Configurações salvas!")

    st.markdown("---")

# -----------------------------------------------------------------------------
# TELA ÚNICA PRINCIPAL (SEÇÕES EXIBIDAS DIRETAMENTE)
# -----------------------------------------------------------------------------
col_principal1, col_principal2 = st.columns([1, 1])

limite = st.session_state.avisos.get("limite_vagas", 15)
jogadoras_ativas = [j for j in st.session_state.jogadoras if j.get("status") == "Ativo"]
nomes_ativas = {j["nome"] for j in jogadoras_ativas}
presencas_ativas = [p for p in st.session_state.presencas if obter_nome_p(p) in nomes_ativas]

lista_atual = sorted(presencas_ativas, key=lambda x: x.get("dt_confirmacao", x.get("hora", "")))

# Regra de horário limite: Segunda-feira às 17:00
mensalistas = []
avulsas = []

for p in lista_atual:
    tipo = obter_tipo_p(p)
    dt_conf_str = p.get("dt_confirmacao", "")
    atrasada_mensalista = False
    if dt_conf_str:
        try:
            dt_obj = datetime.fromisoformat(dt_conf_str)
            # Se for segunda-feira (weekday == 0) e após 17:00
            if dt_obj.weekday() == 0 and (dt_obj.hour >= 17):
                atrasada_mensalista = True
        except:
            pass
            
    if tipo == "Mensalista" and not atrasada_mensalista:
        mensalistas.append(p)
    else:
        avulsas.append(p)

confirmadas = mensalistas[:limite]
espera = mensalistas[limite:] + avulsas

with col_principal1:
    st.markdown("### 📌 Presença no Jogo & Listas")
    st.write(f"**Vagas Principais:** {len(confirmadas)}/{limite}")
    
    if not confirmadas:
        st.info("Nenhuma atleta confirmada ainda.")
    for i, p in enumerate(confirmadas, 1):
        st.markdown(f"<div class='card-team'><b>{i}.</b> {obter_nome_p(p)} `[{obter_tipo_p(p)}]` — <i>{obter_hora_p(p)}</i></div>", unsafe_allow_html=True)

    st.markdown(f"### ⏳ Fila de Espera ({len(espera)})")
    if not espera:
        st.info("Fila de espera vazia.")
    for i, p in enumerate(espera, 1):
        st.markdown(f"<div class='card-team'><b>{i}º:</b> {obter_nome_p(p)} `[{obter_tipo_p(p)}]`</div>", unsafe_allow_html=True)

    # Ação de confirmar/cancelar para a jogadora logada
    st.markdown("---")
    st.subheader("✍️ Minha Confirmação")
    if not st.session_state.usuario_logado:
        st.warning("Faça login na barra lateral para confirmar sua presença.")
    else:
        j_nome = st.session_state.usuario_logado
        dados_j = next((j for j in st.session_state.jogadoras if j["nome"] == j_nome), None)
        tipo_j = dados_j.get("tipo", "Avulso") if dados_j else "Avulso"
        
        pos_conf = next((idx + 1 for idx, p in enumerate(confirmadas) if obter_nome_p(p) == j_nome), None)
        pos_esp = next((idx + 1 for idx, p in enumerate(espera) if obter_nome_p(p) == j_nome), None)
        
        if pos_conf:
            st.success(f"🎉 Você está na **Lista Principal** na posição **{pos_conf}**!")
        elif pos_esp:
            st.warning(f"⏳ Você está na **Fila de Espera** na posição **{pos_esp}º**.")
        else:
            st.info("ℹ️ Você não está confirmada no momento.")

        with st.form("form_pres_user"):
            c_ok = st.form_submit_button("👍 Confirmar Presença", use_container_width=True)
            c_canc = st.form_submit_button("❌ Cancelar Presença", use_container_width=True)

        ja_na_lista = (pos_conf is not None or pos_esp is not None)

        if c_ok:
            st.session_state.presencas = [p for p in st.session_state.presencas if obter_nome_p(p) != j_nome]
            st.session_state.presencas.append({
                "nome": j_nome, 
                "hora": hoje_dt.strftime("%H:%M"),
                "tipo": tipo_j,
                "dt_confirmacao": hoje_dt.isoformat()
            })
            salvar_dados(PRESENCAS_FILE, st.session_state.presencas)
            st.success("Presença confirmada com sucesso!")
            st.rerun()

        if c_canc:
            if ja_na_lista:
                st.session_state.presencas = [p for p in st.session_state.presencas if obter_nome_p(p) != j_nome]
                salvar_dados(PRESENCAS_FILE, st.session_state.presencas)
                st.info("Presença cancelada com sucesso!")
                st.rerun()
            else:
                st.error("Seu nome não está na lista.")

with col_principal2:
    st.markdown("### 🔀 Sorteio de Times Oficial & Paralelo")
    sorteio_salvo = st.session_state.sorteio_oficial
    
    if sorteio_salvo and "times" in sorteio_salvo:
        st.write("#### 🏆 Sorteio Oficial")
        for nome_time, membros in sorteio_salvo["times"].items():
            st.markdown(f"<div class='card-team'><h3>⚽ {nome_time}</h3>", unsafe_allow_html=True)
            for item in membros:
                st.markdown(f"• **{item}**")
            st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.info("Nenhum sorteio oficial gerado ainda (Automático às 18:30).")

    # Sorteio Paralelo (Baseado em quem está presente agora)
    st.markdown("#### ⚡ Sorteio Paralelo (Presença no Local)")
    if st.button("Gerar Sorteio Paralelo Agora", use_container_width=True):
        confirmadas_nomes = [obter_nome_p(p) for p in confirmadas]
        if len(confirmadas_nomes) >= 2:
            random.shuffle(confirmadas_nomes)
            res_paralelo = {"Time A": confirmadas_nomes[::2], "Time B": confirmadas_nomes[1::2]}
            st.success("Sorteio Paralelo Gerado!")
            for nome_t, membros_t in res_paralelo.items():
                st.markdown(f"<div class='card-team'><b>{nome_t}:</b> {', '.join(membros_t)}</div>", unsafe_allow_html=True)
        else:
            st.error("Atletas insuficientes na lista confirmada para gerar o sorteio.")

st.markdown("---")

# -----------------------------------------------------------------------------
# SEÇÕES INFERIORES: PAGAMENTO, REGULAMENTO E ELENCO
# -----------------------------------------------------------------------------
col_bot1, col_bot2, col_bot3 = st.columns(3)

with col_bot1:
    st.markdown("### 💸 Pagamento & Pix")
    st.markdown(f"""
    <div class='card-team'>
        📌 <b>Chave Pix:</b> <code>{st.session_state.avisos.get('pix', 'peladinhafc@email.com')}</code><br>
        Vencimento: <b>{st.session_state.avisos.get('vencimento', 'Todo dia 10')}</b>
    </div>
    """, unsafe_allow_html=True)
    
    if st.session_state.usuario_logado:
        st.write("Enviar Comprovante:")
        with st.form("form_comprovante", clear_on_submit=True):
            arquivo_submetido = st.file_uploader("Selecione a imagem", type=["png", "jpg", "jpeg"])
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
                    st.success("Comprovante enviado com sucesso para validação do Administrador!")
                else:
                    st.error("Selecione um arquivo de imagem.")

with col_bot2:
    st.markdown("### 📜 Regulamento Interno")
    for reg in st.session_state.regulamento:
        st.markdown(f"<div class='card-team'><h4 style='color: #0D9488;'>{reg['topico']}</h4><p>{reg['regrinha']}</p></div>", unsafe_allow_html=True)

with col_bot3:
    st.markdown("### 📋 Elenco de Atletas")
    for j in st.session_state.jogadoras:
        if j.get("status") == "Ativo":
            st.markdown(f"<div class='card-team'><b>⚽ {j['nome']}</b><br><small>Tipo: `{j.get('tipo', 'Avulso')}` | Quitado: `{j.get('quitado', 'Não')}`</small></div>", unsafe_allow_html=True)
