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
# CONFIGURAÇÃO DA PÁGINA
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Peladinha FC | Gestão Inteligente",
    page_icon="⚽",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# -----------------------------------------------------------------------------
# ESTILIZAÇÃO CSS CUSTOMIZADA (CARDS ROSAS E LETRAS PRETAS)
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

    /* CARDS EM ROSA COM LETRAS PRETAS */
    .card-team {
        background: #FFC0CB !important;
        border: 1px solid #FF69B4 !important;
        border-top: 4px solid #FF1493 !important;
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 15px;
        color: #000000 !important;
    }
    .card-team h3, .card-team h4, .card-team p, .card-team b, .card-team span, .card-team small, .card-team code {
        color: #000000 !important;
    }

    div.stButton > button:first-child {
        background-color: #FFC0CB !important;
        color: #000000 !important;
        font-weight: 700 !important;
        border-radius: 10px !important;
        border: 1px solid #FF69B4 !important;
        padding: 15px 20px !important;
        box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.2);
        width: 100%;
    }
    div.stButton > button:first-child:hover {
        background-color: #FF69B4 !important;
        border-color: #FF1493 !important;
        color: #000000 !important;
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

SENHA_MESTRE_DEV = "1980"

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
        st.subheader("Solicitar Conta Administradora")
        with st.form("form_cad_adm", clear_on_submit=True):
            a_nome = st.text_input("Nome do Administrador *")
            a_user = st.text_input("Login Admin *")
            a_pass = st.text_input("Senha Admin *", type="password")
            if st.form_submit_button("CADASTRAR ADMIN"):
                if a_nome and a_user and a_pass:
                    if any(adm.get("login") == a_user.strip() for adm in st.session_state.administradores):
                        st.error("Login de admin já existe!")
                    else:
                        st.session_state.administradores.append({
                            "nome": a_nome.strip(), "login": a_user.strip(), "senha": a_pass.strip()
                        })
                        salvar_dados(ADMINS_FILE, st.session_state.administradores)
                        st.success("Administrador cadastrado com sucesso!")
                else:
                    st.error("Preencha todos os campos!")

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
        # --- PAINEL DE ANIVERSARIANTES DO MÊS VIGENTE ---
        mes_atual = hoje_dt.month
        aniversariantes_mes = []
        for j in st.session_state.jogadoras:
            nasc_str = j.get("nascimento", "")
            if nasc_str and "/" in nasc_str:
                try:
                    partes = nasc_str.split("/")
                    mes_nasc = int(partes[1])
                    if mes_nasc == mes_atual:
                        aniversariantes_mes.append(j["nome"])
                except:
                    pass

        if aniversariantes_mes:
            nomes_aniv = ", ".join(aniversariantes_mes)
            st.markdown(f"""
            <div class='card-team' style='border-top-color: #FF1493; text-align: center;'>
                <h3>🎂🎂🎂 PARABÉNS ÀS ANIVERSARIANTES DO MÊS! 🎂🎂🎂</h3>
                <p>Desejamos um feliz aniversário, muita saúde, felicidades e muitos gols para: <b>{nomes_aniv}</b>! 🥳⚽</p>
            </div>
            """, unsafe_allow_html=True)

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
            st.markdown(f"<div class='card-team'><h4 style='color: #000000;'>{reg['topico']}</h4><p>{reg['regrinha']}</p></div>", unsafe_allow_html=True)

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
                st.write("### ✍️ Gerenciar Minha Presença")
                if st.session_state.perfil_logado == "Jogadora":
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
                        st.info("ℹ️ Você não está confirmada.")

                    with st.form("form_pres"):
                        c_ok = st.form_submit_button("👍 Confirmar Presença", use_container_width=True)
                        c_canc = st.form_submit_button("❌ Cancelar Presença", use_container_width=True)

                    ja_na_lista = (pos_conf is not None or pos_esp is not None)

                    if c_ok:
                        st.session_state.presencas = [p for p in st.session_state.presencas if obter_nome_p(p) != j_nome]
                        st.session_state.presencas.append({
                            "nome": j_nome, "hora": hoje_dt.strftime("%H:%M"),
                            "tipo": tipo_j, "dt_confirmacao": hoje_dt.isoformat()
                        })
                        salvar_dados(PRESENCAS_FILE, st.session_state.presencas)
                        st.success("Presença atualizada!")
                        st.rerun()

                    if c_canc:
                        if ja_na_lista:
                            st.session_state.presencas = [p for p in st.session_state.presencas if obter_nome_p(p) != j_nome]
                            salvar_dados(PRESENCAS_FILE, st.session_state.presencas)
                            st.info("Presença cancelada!")
                            st.rerun()
                        else:
                            st.error("Seu nome não está na lista.")

    elif st.session_state.pagina_atual == "sorteio":
        st.subheader("🔀 Sorteio de Times (Oficial & Paralelo)")
        sorteio_salvo = st.session_state.sorteio_oficial
        
        if sorteio_salvo and "times" in sorteio_salvo:
            st.write("#### 🏆 Sorteio Oficial")
            for nome_time, membros in sorteio_salvo["times"].items():
                st.markdown(f"<div class='card-team'><h3>⚽ {nome_time}</h3>", unsafe_allow_html=True)
                for item in membros:
                    st.markdown(f"• **{item}**")
                st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.info("Nenhum sorteio oficial gerado ainda.")

        st.markdown("#### ⚡ Sorteio Paralelo (Baseado em Presença no Local)")
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
        st.subheader("📋 Elenco de Atletas Cadastradas")
        for j in st.session_state.jogadoras:
            if j.get("status") == "Ativo":
                st.markdown(f"<div class='card-team'><b>⚽ {j['nome']}</b><br><small>Tipo: `{j.get('tipo', 'Avulso')}` | Quitado: `{j.get('quitado', 'Não')}` | Nasc: {j.get('nascimento')}</small></div>", unsafe_allow_html=True)

    elif st.session_state.pagina_atual == "pagamento":
        st.subheader("💸 Pagamentos e Chave Pix")
        st.markdown(f"""
        <div class='card-team'>
            📌 <b>Chave Pix Oficial:</b> <code>{st.session_state.avisos.get('pix', 'peladinhafc@email.com')}</code><br>
            Vencimento: <b>{st.session_state.avisos.get('vencimento', 'Todo dia 10')}</b>
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
                        st.success("Comprovante enviado com sucesso para validação do Administrador!")
                    else:
                        st.error("Selecione um arquivo de imagem.")

        if st.session_state.perfil_logado in ["Admin", "Dev"]:
            st.write("### 👑 Conferência de Comprovantes Pendentes")
            comprovantes = st.session_state.comprovantes
            pendentes_comp = [c for c in comprovantes if not c.get("conferido", False)]
            if not pendentes_comp:
                st.info("Nenhum comprovante pendente para conferência.")
            for idx, comp in enumerate(comprovantes):
                if not comp.get("conferido", False):
                    st.markdown(f"<div class='card-team'><b>Atleta:</b> {comp['nome']} | <b>Data:</b> {comp['data']}</div>", unsafe_allow_html=True)
                    if os.path.exists(comp['arquivo']):
                        st.image(comp['arquivo'], width=300)
                    if st.button(f"Validar Pagamento de {comp['nome']}", key=f"val_comp_{idx}"):
                        comp["conferido"] = True
                        for j in st.session_state.jogadoras:
                            if j["nome"] == comp["nome"]:
                                j["quitado"] = "Sim"
                        salvar_dados(DATA_FILE, st.session_state.jogadoras)
                        
                        st.session_state.financeiro.append({
                            "mes": hoje_dt.strftime("%B/%Y"), "tipo": "Receita", "descricao": f"Mensalidade - {comp['nome']}", "valor": 50.00
                        })
                        salvar_dados(FINANCE_FILE, st.session_state.financeiro)
                        salvar_dados(COMPROVANTES_FILE, comprovantes)
                        st.success("Pagamento validado e adicionado como receita no fluxo de caixa!")
                        st.rerun()

    elif st.session_state.pagina_atual == "caixa":
        st.subheader("📊 Fluxo de Caixa Completo")
        
        with st.form("form_lanca_caixa", clear_on_submit=True):
            st.write("<b>Lançar Nova Receita ou Despesa</b>", unsafe_allow_html=True)
            c_mes = st.text_input("Mês / Ano (Ex: Janeiro/2026)", value=hoje_dt.strftime("%B/%Y"))
            c_tipo_fin = st.selectbox("Tipo", ["Receita", "Despesa"])
            c_desc = st.text_input("Descrição (Ex: Compra de Coletes, Aluguel)")
            c_valor = st.number_input("Valor (R$)", min_value=0.0, step=10.0)
            if st.form_submit_button("Adicionar Lançamento"):
                if c_desc.strip() and c_valor > 0:
                    st.session_state.financeiro.append({
                        "mes": c_mes.strip(), "tipo": c_tipo_fin, "descricao": c_desc.strip(), "valor": float(c_valor)
                    })
                    salvar_dados(FINANCE_FILE, st.session_state.financeiro)
                    st.success("Lançamento adicionado com sucesso!")
                    st.rerun()
                else:
                    st.error("Preencha a descrição e informe um valor válido.")

        st.markdown("---")
        
        registros_caixa = st.session_state.financeiro
        if not registros_caixa:
            st.info("Nenhum registro financeiro encontrado.")
        else:
            total_geral_rec = sum(item["valor"] for item in registros_caixa if item["tipo"] == "Receita")
            total_geral_desp = sum(item["valor"] for item in registros_caixa if item["tipo"] == "Despesa")
            saldo_total = total_geral_rec - total_geral_desp

            st.markdown(f"""
            <div class='card-team' style='border-top-color: #10B981;'>
                <h3>💰 Saldo Total em Caixa: R$ {saldo_total:.2f}</h3>
                <p>🟢 Total de Receitas: R$ {total_geral_rec:.2f} | 🔴 Total de Despesas: R$ {total_geral_desp:.2f}</p>
            </div>
            """, unsafe_allow_html=True)

            st.write("### Histórico de Movimentações")
            for idx, item in enumerate(registros_caixa):
                cor_borda = "#10B981" if item["tipo"] == "Receita" else "#EF4444"
                st.markdown(f"""
                <div class='card-team' style='border-top-color: {cor_borda};'>
                    <b>Mês:</b> {item.get('mes', 'Geral')} | <b>Tipo:</b> <code>{item['tipo']}</code> | <b>Descrição:</b> {item['descricao']} | <b>Valor:</b> R$ {item['valor']:.2f}
                </div>
                """, unsafe_allow_html=True)

    elif st.session_state.pagina_atual == "gerenciamento":
        st.subheader("🛠️ Painel de Gerenciamento Geral & Aprovações")
        
        tab_ger1, tab_ger2, tab_ger3 = st.tabs(["📝 Aprovar Cadastros", "⚙️ Configurações Gerais", "🔒 Gestão de Contas (Dev)"])

        with tab_ger1:
            st.write("### Aprovação de Novas Atletas")
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
                        st.success(f"✔️ Confirmação: A atleta {j['nome']} foi aprovada e ativada com sucesso!")
                        st.rerun()
                with col_p3:
                    if st.button("❌ Recusar", key=f"rec_{idx}"):
                        st.session_state.jogadoras.remove(j)
                        salvar_dados(DATA_FILE, st.session_state.jogadoras)
                        st.warning(f"⚠️ O cadastro de {j['nome']} foi recusado/removido.")
                        st.rerun()

        with tab_ger2:
            with st.form("form_cfg_geral_painel"):
                limite_v = st.number_input("Limite de Vagas", value=int(st.session_state.avisos.get("limite_vagas", 15)))
                pix_val = st.text_input("Chave Pix", value=st.session_state.avisos.get("pix", ""))
                if st.form_submit_button("Salvar Ajustes"):
                    st.session_state.avisos["limite_vagas"] = limite_v
                    st.session_state.avisos["pix"] = pix_val
                    salvar_dados(AVISOS_FILE, st.session_state.avisos)
                    st.success("Configurações atualizadas!")

        with tab_ger3:
            if st.session_state.perfil_logado == "Dev":
                st.write("### Gerenciamento de Credenciais de Administradores (Restrito ao Desenvolvedor)")
                for idx, adm in enumerate(st.session_state.administradores):
                    st.markdown(f"<div class='card-team'><b>Admin:</b> {adm['nome']} | <b>Login:</b> <code>{adm['login']}</code></div>", unsafe_allow_html=True)
                    if st.button(f"Excluir Admin {adm['nome']}", key=f"del_adm_{idx}"):
                        if len(st.session_state.administradores) > 1:
                            st.session_state.administradores.pop(idx)
                            salvar_dados(ADMINS_FILE, st.session_state.administradores)
                            st.success("Administrador removido!")
                            st.rerun()
                        else:
                            st.error("Você não pode excluir o único administrador do sistema.")
            else:
                st.warning("⚠️ Esta área é restrita apenas ao perfil de Desenvolvedor.")
