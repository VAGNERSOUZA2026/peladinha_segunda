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
hoje_str = hoje_dt.strftime("%d/%m")
mes_vigente_str = hoje_dt.strftime("%m/%Y")
data_hoje_id = hoje_dt.strftime("%Y-%m-%d")

# -----------------------------------------------------------------------------
# CONFIGURAÇÃO DA PÁGINA
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Peladinha FC | Gestão Inteligente",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------------------------------------------------------
# ESTILIZAÇÃO CSS CUSTOMIZADA (ESTÉTICA MODERNA / CARDS VISÍVEIS)
# -----------------------------------------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] { 
        font-family: 'Montserrat', sans-serif; 
    }

    .stApp {
        background-color: #F8FAFC;
    }

    .hero-banner {
        background: linear-gradient(135deg, #4C1D95 0%, #831843 50%, #9D174D 100%);
        border-radius: 20px;
        padding: 35px 20px;
        text-align: center;
        color: #FFFFFF;
        box-shadow: 0px 10px 25px rgba(131, 24, 67, 0.25);
        margin-bottom: 25px;
    }
    .hero-title { 
        font-size: 2.2rem; 
        font-weight: 800; 
        letter-spacing: -0.5px;
        margin-bottom: 8px; 
        color: #FFFFFF; 
    }
    .hero-subtitle { 
        font-size: 0.95rem; 
        font-weight: 300; 
        color: #FCE7F3; 
        letter-spacing: 0.5px;
    }

    /* Cards Interativos Visíveis */
    .card-interactive {
        background: #FFFFFF !important;
        border: 1px solid #CBD5E1 !important;
        border-radius: 14px;
        padding: 20px;
        margin-bottom: 15px;
        box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.05);
        color: #1E293B !important;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .card-interactive:hover {
        transform: translateY(-2px);
        box-shadow: 0px 6px 16px rgba(131, 24, 67, 0.1);
        border-color: #DB2777 !important;
    }

    .card-notice {
        background: #FDF2F8;
        border-left: 6px solid #DB2777;
        padding: 18px;
        border-radius: 12px;
        margin-bottom: 20px;
        color: #831843;
        box-shadow: 0px 4px 12px rgba(219, 39, 119, 0.05);
    }

    .card-bday {
        background: linear-gradient(135deg, #FCE7F3 0%, #F3E8FF 100%);
        border-left: 6px solid #9333EA;
        padding: 20px;
        border-radius: 14px;
        margin-bottom: 20px;
        color: #581C87;
        text-align: center;
        font-size: 1.1rem;
        font-weight: 500;
        box-shadow: 0px 6px 15px rgba(147, 51, 234, 0.08);
    }

    .card-team {
        background: #FFFFFF;
        border: 1px solid #CBD5E1;
        border-top: 5px solid #DB2777;
        border-radius: 14px;
        padding: 18px;
        margin-bottom: 15px;
        box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.05);
    }
    .card-team h3 {
        color: #831843;
        font-size: 1.1rem;
        font-weight: 700;
        margin-bottom: 10px;
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

if "jogadoras" not in st.session_state:
    st.session_state.jogadoras = carregar_dados(DATA_FILE, [])
if "presencas" not in st.session_state:
    st.session_state.presencas = carregar_dados(PRESENCAS_FILE, [])
if "financeiro" not in st.session_state:
    st.session_state.financeiro = carregar_dados(FINANCE_FILE, [])
if "comprovantes" not in st.session_state:
    st.session_state.comprovantes = carregar_dados(COMPROVANTES_FILE, [])
if "administradores" not in st.session_state:
    def_admins = [{"nome": "Administrador Principal", "login": "admin", "senha": "1980", "principal": True}]
    st.session_state.administradores = carregar_dados(ADMINS_FILE, def_admins)
if "avisos" not in st.session_state:
    st.session_state.avisos = carregar_dados(AVISOS_FILE, {
        "vencimento": "Todo dia 10 de cada mês",
        "recado": "Favor chegarem 10 minutos antes para organizar o jogo!",
        "pix": "peladinhafc@email.com",
        "limite_vagas": 15
    })
if "regulamento" not in st.session_state:
    st.session_state.regulamento = carregar_dados(REGULAMENTO_FILE, [
        {"topico": "📌 1. Prioridade nas Vagas", "regrinha": "Mensalistas confirmando até as 17:00 de segunda têm prioridade na lista principal. Avulsas vão para a fila de espera e sobem após esse horário se houver vagas."},
        {"topico": "⏳ 2. Fila de Espera", "regrinha": "Jogadoras avulsas entram na fila de espera por ordem de chegada."},
        {"topico": "❌ 3. Desistências", "regrinha": "Ao cancelar, a primeira da fila é incluída no jogo."},
        {"topico": "💸 4. Mensalidades", "regrinha": "Pagas via Pix até a data estipulada."}
    ])
if "sorteio_oficial" not in st.session_state:
    st.session_state.sorteio_oficial = carregar_dados(SORTEIO_FILE, {})
if "usuario_logado" not in st.session_state:
    st.session_state.usuario_logado = None
if "admin_logged" not in st.session_state:
    st.session_state.admin_logged = False
if "admin_nome" not in st.session_state:
    st.session_state.admin_nome = ""
if "admin_principal" not in st.session_state:
    st.session_state.admin_principal = False
if "msg_cadastro_sucesso" not in st.session_state:
    st.session_state.msg_cadastro_sucesso = False

# -----------------------------------------------------------------------------
# BANNER DA APLICAÇÃO
# -----------------------------------------------------------------------------
st.markdown("""
<div class='hero-banner'>
    <div class='hero-title'>⚽ PELADINHA FC</div>
    <div class='hero-subtitle'>Gestão Inteligente & Sorteio de Futebol Feminino</div>
</div>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# SAUDAÇÃO DINÂMICA E BOAS-VINDAS ÚNICA
# -----------------------------------------------------------------------------
if st.session_state.usuario_logado:
    hora_atual = hoje_dt.hour
    if 5 <= hora_atual < 12:
        saudacao = "Bom dia"
    elif 12 <= hora_atual < 18:
        saudacao = "Boa tarde"
    else:
        saudacao = "Boa noite"

    dados_usuario_atual = next((j for j in st.session_state.jogadoras if j["nome"] == st.session_state.usuario_logado), None)
    
    if dados_usuario_atual:
        if not dados_usuario_atual.get("boas_vindas_vista", False):
            st.markdown(f"""
            <div class='card-notice' style='background: #ECFDF5; border-left: 6px solid #10B981; color: #065F46;'>
                🎉 <b>Olá {st.session_state.usuario_logado}, {saudacao}! Seja muito bem-vinda ao Peladinha FC!</b><br>
                Ficamos muito felizes com a sua chegada ao nosso time. Para garantir sua vaga nos jogos, acesse a aba <b>📌 Presença no Jogo</b>. Bom jogo e muitos gols! ⚽✨
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("👍 Entendido, vamos lá!"):
                dados_usuario_atual["boas_vindas_vista"] = True
                salvar_dados(DATA_FILE, st.session_state.jogadoras)
                st.rerun()
        else:
            st.markdown(f"""
            <div class='card-notice' style='background: #EFF6FF; border-left: 6px solid #3B82F6; color: #1E40AF;'>
                👋 <b>{saudacao}, {st.session_state.usuario_logado}!</b> Que bom ter você de volta por hoje. ⚽✨
            </div>
            """, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# ANIVERSARIANTES DO DIA
# -----------------------------------------------------------------------------
aniversariantes_hoje = [j["nome"] for j in st.session_state.jogadoras if j.get("nascimento", "").strip() == hoje_str]
if aniversariantes_hoje:
    nomes_aniver = " e ".join(aniversariantes_hoje)
    st.balloons()
    st.markdown(f"""
    <div class='card-bday'>
        🎂 🎉 <b>PARABÉNS, {nomes_aniver.upper()}!</b> 🎉 🎂<br>
        O Peladinha FC deseja a você um FELIZ ANIVERSÁRIO! Muita saúde e gols! ⚽🎈
    </div>
    """, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# MENU LATERAL (SIDEBAR) COM CADASTRO LOGO ABAIXO DO LOGIN
# -----------------------------------------------------------------------------
st.sidebar.title("📌 Navegação")
lista_menu = ["📌 Presença no Jogo", "🔀 Sorteio de Times", "💸 Pagamento & Pix", "📜 Regulamento", "📋 Elenco de Jogadoras"]

if st.session_state.admin_logged:
    lista_menu.insert(2, "📊 Fluxo de Caixa (Admin)")
    lista_menu.append("⚙️ Painel Admin")

menu = st.sidebar.radio("Ir para:", lista_menu)

st.sidebar.markdown("---")
st.sidebar.title("👤 Área da Jogadora")

if st.session_state.usuario_logado:
    st.sidebar.success(f"Logada: **{st.session_state.usuario_logado}**")
    if st.sidebar.button("🚪 Sair da Conta"):
        st.session_state.usuario_logado = None
        st.rerun()
else:
    # 1. Seção de Entrar
    st.sidebar.subheader("🔑 Entrar na Conta")
    if st.session_state.msg_cadastro_sucesso:
        st.sidebar.success("🎉 Cadastro realizado com sucesso! Faça login abaixo.")
        st.session_state.msg_cadastro_sucesso = False
        
    with st.sidebar.form("form_login_player"):
        l_user = st.text_input("Login")
        l_pass = st.text_input("Senha", type="password")
        if st.form_submit_button("Entrar", use_container_width=True):
            user_found = next((j for j in st.session_state.jogadoras if j.get("login") == l_user and j.get("senha") == l_pass), None)
            if user_found:
                st.session_state.usuario_logado = user_found["nome"]
                st.rerun()
            else:
                st.error("Login ou senha incorretos!")

    st.sidebar.markdown("---")
    
    # 2. Seção de Cadastro (Colocada logo abaixo da opção de entrar)
    st.sidebar.subheader("📝 Cadastrar Nova Jogadora")
    with st.sidebar.form("form_cad_player", clear_on_submit=True):
        c_nome = st.text_input("Seu Nome *")
        c_nasc = st.text_input("Nascimento (DD/MM) *", placeholder="Ex: 15/05")
        c_tipo = st.selectbox("Deseja se cadastrar como:", ["Avulso", "Mensalista"])
        c_user = st.text_input("Escolha um Login *")
        c_pass = st.text_input("Escolha uma Senha *", type="password")
        if st.form_submit_button("Criar Conta", use_container_width=True):
            if c_nome and c_user and c_pass:
                if any(j.get("login") == c_user.strip() for j in st.session_state.jogadoras):
                    st.error("Este Login já está em uso. Escolha outro!")
                else:
                    st.session_state.jogadoras.append({
                        "nome": c_nome.strip(), "nascimento": c_nasc.strip(),
                        "login": c_user.strip(), "senha": c_pass.strip(),
                        "tipo": c_tipo, "mes_vigente": mes_vigente_str,
                        "contato": "", "status": "Ativo",
                        "boas_vindas_vista": False
                    })
                    salvar_dados(DATA_FILE, st.session_state.jogadoras)
                    st.session_state.msg_cadastro_sucesso = True
                    st.rerun()
            else:
                st.error("Preencha Nome, Login e Senha!")

st.sidebar.markdown("---")
st.sidebar.subheader("🔒 Área do Administrador")

if not st.session_state.admin_logged:
    with st.sidebar.form("form_login_admin"):
        adm_user = st.text_input("Login Admin")
        adm_pass = st.text_input("Senha Admin", type="password")
        if st.form_submit_button("Acessar Como Admin", use_container_width=True):
            admin_encontrado = next((adm for adm in st.session_state.administradores if adm.get("login") == adm_user and adm.get("senha") == adm_pass), None)
            if admin_encontrado:
                st.session_state.admin_logged = True
                st.session_state.admin_nome = admin_encontrado["nome"]
                st.session_state.admin_principal = admin_encontrado.get("principal", False)
                st.rerun()
            else:
                st.error("Credenciais de Administrador incorretas!")
else:
    cargo_str = "Admin Principal" if st.session_state.admin_principal else "Admin Secundário"
    st.sidebar.info(f"🔑 Admin: **{st.session_state.admin_nome}**\n\n*{cargo_str}*")
    if st.sidebar.button("Sair do Admin"):
        st.session_state.admin_logged = False
        st.session_state.admin_nome = ""
        st.session_state.admin_principal = False
        st.rerun()

# -----------------------------------------------------------------------------
# LÓGICA DE ORDENAÇÃO DE PRESENÇA
# -----------------------------------------------------------------------------
jogadoras_ativas = [j for j in st.session_state.jogadoras if j.get("status") != "Inativo"]
nomes_ativas = {j["nome"] for j in jogadoras_ativas}

presencas_ativas = [p for p in st.session_state.presencas if obter_nome_p(p) in nomes_ativas]

lista_atual = sorted(presencas_ativas, key=lambda x: x.get("dt_confirmacao", x.get("hora", "")))
mensalistas = [p for p in lista_atual if p.get("tipo") == "Mensalista"]
avulsas = [p for p in lista_atual if p.get("tipo") == "Avulso"]
limite = st.session_state.avisos.get("limite_vagas", 15)

confirmadas = mensalistas[:limite]
espera = mensalistas[limite:] + avulsas

passou_prazo = hoje_dt.weekday() == 0 and hoje_dt.hour >= 17

if passou_prazo and len(confirmadas) < limite:
    vagas_sobrando = limite - len(confirmadas)
    promovidas = espera[:vagas_sobrando]
    confirmadas.extend(promovidas)
    espera = espera[vagas_sobrando:]

# -----------------------------------------------------------------------------
# SORTEIO AUTOMÁTICO
# -----------------------------------------------------------------------------
if hoje_dt.weekday() == 0 and (hoje_dt.hour > 18 or (hoje_dt.hour == 18 and hoje_dt.minute >= 30)):
    sorteio_salvo = st.session_state.sorteio_oficial
    if sorteio_salvo.get("data") != data_hoje_id:
        nomes_confirmadas = [obter_nome_p(p) for p in confirmadas]
        if len(nomes_confirmadas) >= 2:
            random.shuffle(nomes_confirmadas)
            qtd_t = 2
            res_times = {f"Time {i+1}": [] for i in range(qtd_t)}
            for idx, p in enumerate(nomes_confirmadas):
                res_times[f"Time {idx % qtd_t + 1}"].append(p)
            
            st.session_state.sorteio_oficial = {
                "data": data_hoje_id,
                "hora": f"{hoje_dt.strftime('%H:%M')} (Automático)",
                "times": res_times
            }
            salvar_dados(SORTEIO_FILE, st.session_state.sorteio_oficial)

# -----------------------------------------------------------------------------
# PÁGINAS DO SISTEMA
# -----------------------------------------------------------------------------
if menu == "📌 Presença no Jogo":
    st.markdown(f"""
    <div class='card-notice'>
        📢 <b>AVISOS:</b> Limitado a <b>{limite} vagas</b>. <br>
        ⭐ <b>Mensalistas têm prioridade até SEGUNDA-FEIRA às 17:00!</b> Avulsas ficam na fila de espera e sobem após esse horário caso haja vagas.<br>
        💡 <i>{st.session_state.avisos.get('recado')}</i><br>
        ⏰ <i>Sorteio oficial automático: <b>Segunda-feira às 18:30</b>.</i>
    </div>
    """, unsafe_allow_html=True)

    col_lista, col_acoes = st.columns([1, 1])

    with col_lista:
        st.subheader("📋 Lista de Presença")
        st.markdown(f"### 🟢 Confirmadas no Jogo ({len(confirmadas)}/{limite})")
        if not confirmadas:
            st.info("Nenhuma jogadora confirmada ainda.")
        else:
            for i, p in enumerate(confirmadas, 1):
                nome_p, hora_p, tipo_p = obter_nome_p(p), obter_hora_p(p), obter_tipo_p(p)
                st.markdown(f"<div class='card-interactive' style='padding: 10px 15px; margin-bottom: 8px;'><b>{i}.</b> {nome_p} `[{tipo_p}]` — <i>às {hora_p}</i></div>", unsafe_allow_html=True)

        st.markdown("---")
        st.markdown(f"### ⏳ Fila de Espera ({len(espera)})")
        if not espera:
            st.caption("Nenhuma jogadora na fila de espera.")
        else:
            for i, p in enumerate(espera, 1):
                nome_p, hora_p, tipo_p = obter_nome_p(p), obter_hora_p(p), obter_tipo_p(p)
                badge = "🏃 Avulsa" if tipo_p == "Avulso" else "⭐ Mensalista"
                st.markdown(f"<div class='card-interactive' style='padding: 10px 15px; margin-bottom: 8px;'><b>{i}º na espera:</b> {nome_p} `[{badge}]` — <i>às {hora_p}</i></div>", unsafe_allow_html=True)

    with col_acoes:
        st.subheader("✍️ Marcar Minha Presença")
        if not (st.session_state.usuario_logado or st.session_state.admin_logged):
            st.warning("⚠️ **Faça Login no menu lateral para confirmar presença!**")
        else:
            with st.form("form_presenca_express"):
                if st.session_state.admin_logged and not st.session_state.usuario_logado:
                    nomes_cad = [j["nome"] for j in jogadoras_ativas]
                    jogadora_sel = st.selectbox("Selecione a jogadora para alterar:", nomes_cad) if nomes_cad else None
                else:
                    jogadora_sel = st.session_state.usuario_logado
                    st.write(f"Conectada como: **{jogadora_sel}**")

                c1, c2 = st.columns(2)
                btn_confirmar = c1.form_submit_button("👍 Confirmar Presença", use_container_width=True)
                btn_cancelar = c2.form_submit_button("❌ Cancelar Presença", use_container_width=True)

            if jogadora_sel:
                dados_j = next((j for j in st.session_state.jogadoras if j["nome"] == jogadora_sel), None)
                tipo_j = dados_j.get("tipo", "Avulso") if dados_j else "Avulso"

                pos_confirmada = next((idx + 1 for idx, p in enumerate(confirmadas) if obter_nome_p(p) == jogadora_sel), None)
                pos_espera = next((idx + 1 for idx, p in enumerate(espera) if obter_nome_p(p) == jogadora_sel), None)

                if pos_confirmada:
                    st.success(f"🎉 **VOCÊ ESTÁ NO JOGO!** Posição **{pos_confirmada}**.")
                elif pos_espera:
                    st.warning(f"⏳ **VOCÊ ESTÁ NA FILA DE ESPERA!** Posição **{pos_espera}º**.")

                ja_na_lista = pos_confirmada is not None or pos_espera is not None

                if btn_confirmar:
                    if ja_na_lista:
                        st.error("⚠️ Seu nome já está registrado na lista de presença para esta rodada! Não é permitido confirmar mais de uma vez.")
                    else:
                        st.session_state.presencas.append({
                            "nome": jogadora_sel, 
                            "hora": hoje_dt.strftime("%H:%M"),
                            "tipo": tipo_j,
                            "dt_confirmacao": hoje_dt.isoformat()
                        })
                        salvar_dados(PRESENCAS_FILE, st.session_state.presencas)
                        st.success("Presença confirmada com sucesso!")
                        st.rerun()

                if btn_cancelar:
                    if ja_na_lista:
                        st.session_state.presencas = [p for p in st.session_state.presencas if obter_nome_p(p) != jogadora_sel]
                        salvar_dados(PRESENCAS_FILE, st.session_state.presencas)
                        st.info("Presença cancelada com sucesso!")
                        st.rerun()
                    else:
                        st.error("Seu nome não está na lista.")

        if st.session_state.admin_logged:
            st.markdown("---")
            st.subheader("🚨 Ações de Admin")
            if st.button("🧹 Zerar Toda a Lista Manualmente", use_container_width=True):
                st.session_state.presencas = []
                salvar_dados(PRESENCAS_FILE, [])
                st.session_state.sorteio_oficial = {}
                salvar_dados(SORTEIO_FILE, {})
                st.warning("Lista e sorteios zerados com sucesso!")
                st.rerun()

elif menu == "🔀 Sorteio de Times":
    st.subheader("🔀 Sorteio de Times")
    tab_oficial, tab_quadra = st.tabs(["🏆 Sorteio Oficial (Pré-Jogo)", "⚡ Ajuste Rápido de Quadra"])

    with tab_oficial:
        sorteio_salvo = st.session_state.sorteio_oficial
        if sorteio_salvo and "times" in sorteio_salvo:
            st.success(f"✅ **Sorteio Oficial Realizado ({sorteio_salvo.get('hora', '')})**")
            cols = st.columns(len(sorteio_salvo["times"]))
            for idx, (nome_time, membros) in enumerate(sorteio_salvo["times"].items()):
                with cols[idx]:
                    st.markdown(f"<div class='card-team'><h3>⚽ {nome_time}</h3>", unsafe_allow_html=True)
                    for item in membros:
                        st.markdown(f"<div style='background: #F8FAFC; padding: 6px 10px; border-radius: 6px; margin-bottom: 5px; color: #1E293B;'>• **{item}**</div>", unsafe_allow_html=True)
                    st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.info("⏰ O Sorteio Oficial é realizado automaticamente às **Segundas-feiras, às 18:30**.")

        if st.session_state.admin_logged:
            st.markdown("---")
            st.write("#### 🛠️ Forçar Novo Sorteio (Admin)")
            confirmadas_nomes = [obter_nome_p(p) for p in confirmadas]
            qtd_t = st.slider("Dividir em quantos times?", 2, 4, 2, key="slider_oficial")
            if st.button("🎲 Executar Sorteio Agora", use_container_width=True):
                if len(confirmadas_nomes) < qtd_t:
                    st.error("Número insuficiente de confirmadas.")
                else:
                    temp = confirmadas_nomes.copy()
                    random.shuffle(temp)
                    res_times = {f"Time {i+1}": [] for i in range(qtd_t)}
                    for idx, p in enumerate(temp):
                        res_times[f"Time {idx % qtd_t + 1}"].append(p)
                    
                    st.session_state.sorteio_oficial = {
                        "data": data_hoje_id, "hora": f"{hoje_dt.strftime('%H:%M')} (Manual)", "times": res_times
                    }
                    salvar_dados(SORTEIO_FILE, st.session_state.sorteio_oficial)
                    st.rerun()

    with tab_quadra:
        st.write("### ⚡ Sorteio na Quadra")
        confirmadas_nomes = [obter_nome_p(p) for p in confirmadas]
        if not confirmadas_nomes:
            st.info("Nenhuma jogadora confirmada na lista principal.")
        else:
            presentes = st.multiselect("Marque as jogadoras presentes na quadra:", confirmadas_nomes, default=confirmadas_nomes)
            qtd_t_q = st.slider("Dividir em quantos times?", 2, 4, 2, key="slider_quadra")
            if st.button("🎲 Sortear Apenas Presentes", use_container_width=True):
                if len(presentes) < qtd_t_q:
                    st.error("Selecione mais jogadoras.")
                else:
                    temp = presentes.copy()
                    random.shuffle(temp)
                    times_q = [[] for _ in range(qtd_t_q)]
                    for idx, p in enumerate(temp):
                        times_q[idx % qtd_t_q].append(p)
                    cols_q = st.columns(qtd_t_q)
                    for i, t in enumerate(times_q):
                        with cols_q[i]:
                            st.markdown(f"<div class='card-team'><h3>⚽ Time {i+1} (Quadra)</h3>", unsafe_allow_html=True)
                            for item in t:
                                st.markdown(f"<div style='background: #F8FAFC; padding: 6px 10px; border-radius: 6px; margin-bottom: 5px; color: #1E293B;'>• **{item}**</div>", unsafe_allow_html=True)
                            st.markdown("</div>", unsafe_allow_html=True)

elif menu == "📊 Fluxo de Caixa (Admin)":
    if not st.session_state.admin_logged:
        st.error("🔒 Área restrita aos administradores!")
    else:
        st.subheader("📊 Fluxo de Caixa Avançado")
        df_fin = pd.DataFrame(st.session_state.financeiro) if st.session_state.financeiro else pd.DataFrame(columns=["data", "descricao", "tipo", "valor", "categoria"])
        
        if not df_fin.empty and "categoria" not in df_fin.columns:
            df_fin["categoria"] = "Outros"
            for item in st.session_state.financeiro:
                if "categoria" not in item:
                    item["categoria"] = "Outros"

        if not df_fin.empty:
            df_fin["mes_ano"] = df_fin["data"].apply(lambda x: x[3:10] if isinstance(x, str) and len(x) >= 10 else "Geral")
            meses_disp = df_fin["mes_ano"].unique().tolist()
            
            c_f1, c_f2 = st.columns(2)
            with c_f1:
                mes_sel = st.selectbox("📅 Filtrar por Mês/Ano:", ["Todos"] + meses_disp)
            with c_f2:
                tipo_sel = st.selectbox("🏷️ Filtrar por Tipo:", ["Todos", "Entrada", "Saída"])

            df_fin_filtrado = df_fin.copy()
            if mes_sel != "Todos":
                df_fin_filtrado = df_fin_filtrado[df_fin_filtrado["mes_ano"] == mes_sel]
            if tipo_sel != "Todos":
                df_fin_filtrado = df_fin_filtrado[df_fin_filtrado["tipo"] == tipo_sel]
        else:
            df_fin_filtrado = df_fin
            mes_sel, tipo_sel = "Todos", "Todos"

        total_in = df_fin_filtrado[df_fin_filtrado["tipo"] == "Entrada"]["valor"].sum() if not df_fin_filtrado.empty else 0.0
        total_out = df_fin_filtrado[df_fin_filtrado["tipo"] == "Saída"]["valor"].sum() if not df_fin_filtrado.empty else 0.0
        
        m1, m2, m3 = st.columns(3)
        m1.metric("🟢 Entradas", f"R$ {total_in:.2f}")
        m2.metric("🔴 Saídas", f"R$ {total_out:.2f}")
        m3.metric("💰 Saldo do Período", f"R$ {total_in - total_out:.2f}")

        st.markdown("---")
        
        tab_list_fin, tab_add_fin, tab_cat_fin, tab_edit_fin = st.tabs([
            "📜 Extrato em Cards Interativos", 
            "➕ Novo Lançamento", 
            "📊 Resumo por Categoria", 
            "✏️ Editar / Excluir"
        ])

        with tab_list_fin:
            st.write("### 🗂️ Lançamentos Financeiros")
            if not st.session_state.financeiro:
                st.info("Nenhum lançamento cadastrado.")
            else:
                indices_filtrados = []
                for idx, item in enumerate(st.session_state.financeiro):
                    item_mes = item.get("data", "")[3:10] if len(item.get("data", "")) >= 10 else "Geral"
                    item_tipo = item.get("tipo", "Entrada")
                    
                    passou_mes = (mes_sel == "Todos" or item_mes == mes_sel)
                    passou_tipo = (tipo_sel == "Todos" or item_tipo == tipo_sel)
                    
                    if passou_mes and passou_tipo:
                        indices_filtrados.append(idx)

                if not indices_filtrados:
                    st.info("Nenhum registro encontrado para este filtro.")
                else:
                    for i_real in indices_filtrados:
                        reg = st.session_state.financeiro[i_real]
                        t_tipo = reg.get("tipo", "Entrada")
                        t_cat = reg.get("categoria", "Outros")
                        t_desc = reg.get("descricao", "Sem descrição")
                        t_data = reg.get("data", "")
                        t_val = reg.get("valor", 0.0)

                        sinal = "+" if t_tipo == "Entrada" else "-"
                        cor_val = "color: #16A34A;" if t_tipo == "Entrada" else "color: #DC2626;"

                        st.markdown(f"""
                        <div class='card-interactive' style='border-left: 5px solid {"#16A34A" if t_tipo == "Entrada" else "#DC2626"};'>
                            <b>{t_data}</b> | <span style='background: #E2E8F0; padding: 2px 6px; border-radius: 4px; font-size: 0.8rem; color: #334155;'>{t_cat}</span><br>
                            <span style='font-size: 1.05rem; font-weight: 600;'>{t_desc}</span>
                            <div style='float: right; font-size: 1.1rem; font-weight: 700; {cor_val}'>{sinal} R$ {t_val:.2f}</div>
                        </div>
                        """, unsafe_allow_html=True)

        with tab_add_fin:
            st.write("### ➕ Adicionar Novo Lançamento")
            with st.form("form_add_fin", clear_on_submit=True):
                f_desc = st.text_input("Descrição (Ex: Mensalidade de Fulana, Compra de Coletes)")
                f_tipo = st.selectbox("Tipo de Movimentação", ["Entrada", "Saída"])
                f_cat = st.selectbox("Categoria", ["Mensalidade", "Avulso", "Quadra / Aluguel", "Material Esportivo", "Água / Lanche", "Outros"])
                f_val = st.number_input("Valor (R$)", min_value=0.0, format="%.2f")
                f_data = st.text_input("Data", value=hoje_dt.strftime("%d/%m/%Y"))

                if st.form_submit_button("💾 Salvar Lançamento", use_container_width=True):
                    if f_desc and f_val > 0:
                        st.session_state.financeiro.append({
                            "data": f_data,
                            "descricao": f_desc,
                            "tipo": f_tipo,
                            "valor": f_val,
                            "categoria": f_cat
                        })
                        salvar_dados(FINANCE_FILE, st.session_state.financeiro)
                        st.success("Lançamento adicionado com sucesso!")
                        st.rerun()
                    else:
                        st.error("Preencha a descrição e um valor válido.")

        with tab_cat_fin:
            st.write("### 📊 Resumo por Categoria")
            if not st.session_state.financeiro:
                st.info("Sem dados para resumir.")
            else:
                df_res = pd.DataFrame(st.session_state.financeiro)
                resumo_cat = df_res.groupby(["tipo", "categoria"])["valor"].sum().reset_index()
                st.dataframe(resumo_cat, use_container_width=True)

        with tab_edit_fin:
            st.write("### ✏️ Editar ou Excluir Lançamento")
            if not st.session_state.financeiro:
                st.info("Nenhum lançamento disponível.")
            else:
                opcoes_lanc = [f"{i}: [{item['tipo']}] {item['data']} - {item['descricao']} (R$ {item['valor']:.2f})" for i, item in enumerate(st.session_state.financeiro)]
                lanc_escolhido = st.selectbox("Selecione o lançamento:", opcoes_lanc)
                idx_selecionado = int(lanc_escolhido.split(":")[0])
                reg_atual = st.session_state.financeiro[idx_selecionado]

                with st.form("form_edit_fin"):
                    e_desc = st.text_input("Descrição", value=reg_atual.get("descricao", ""))
                    e_tipo = st.selectbox("Tipo", ["Entrada", "Saída"], index=0 if reg_atual.get("tipo") == "Entrada" else 1)
                    e_cat = st.text_input("Categoria", value=reg_atual.get("categoria", "Outros"))
                    e_val = st.number_input("Valor (R$)", value=float(reg_atual.get("valor", 0.0)), format="%.2f")
                    e_data = st.text_input("Data", value=reg_atual.get("data", ""))

                    col_e1, col_e2 = st.columns(2)
                    salvar_alt = col_e1.form_submit_button("💾 Salvar Alterações", use_container_width=True)
                    deletar_alt = col_e2.form_submit_button("🗑️ Excluir Lançamento", use_container_width=True)

                    if salvar_alt:
                        st.session_state.financeiro[idx_selecionado] = {
                            "data": e_data,
                            "descricao": e_desc,
                            "tipo": e_tipo,
                            "valor": e_val,
                            "categoria": e_cat
                        }
                        salvar_dados(FINANCE_FILE, st.session_state.financeiro)
                        st.success("Lançamento atualizado com sucesso!")
                        st.rerun()

                    if deletar_alt:
                        st.session_state.financeiro.pop(idx_selecionado)
                        salvar_dados(FINANCE_FILE, st.session_state.financeiro)
                        st.success("Lançamento excluído com sucesso!")
                        st.rerun()

elif menu == "💸 Pagamento & Pix":
    st.subheader("💸 Pagamentos e Chave Pix")
    st.markdown(f"""
    <div class='card-notice'>
        📌 <b>Informações para Contribuição:</b><br>
        • Vencimento das mensalidades: <b>{st.session_state.avisos.get('vencimento', 'Todo dia 10')}</b>.<br>
        • Chave Pix oficial do Peladinha FC: <code>{st.session_state.avisos.get('pix', 'peladinhafc@email.com')}</code><br>
        <i>Envie o comprovante para a tesouraria após efetuar o pagamento.</i>
    </div>
    """, unsafe_allow_html=True)

    if st.session_state.usuario_logado:
        st.write("#### 📤 Enviar Comprovante de Pagamento (Obrigatório anexar imagem)")
        with st.form("form_envio_comprovante", clear_on_submit=True):
            comp_mes = st.selectbox("Mês Referente:", [mes_vigente_str, "Mês Anterior", "Próximo Mês"])
            comp_obs = st.text_input("Observação (Ex: Pix referente a Mensalidade)")
            arquivo_img = st.file_uploader("Anexar Imagem do Comprovante (PNG, JPG, JPEG) *", type=["png", "jpg", "jpeg"])
            
            btn_enviar_comp = st.form_submit_button("📎 Enviar Notificação de Pagamento", use_container_width=True)

            if btn_enviar_comp:
                if arquivo_img is None:
                    st.error("⚠️ É obrigatório anexar a imagem do comprovante para realizar o envio!")
                else:
                    extensao = arquivo_img.name.split(".")[-1]
                    nome_arquivo_unico = f"{st.session_state.usuario_logado}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{extensao}"
                    caminho_completo = os.path.join(UPLOAD_DIR, nome_arquivo_unico)
                    
                    with open(caminho_completo, "wb") as f:
                        f.write(arquivo_img.getbuffer())

                    st.session_state.comprovantes.append({
                        "jogadora": st.session_state.usuario_logado,
                        "mes": comp_mes,
                        "obs": comp_obs,
                        "arquivo": caminho_completo,
                        "data": hoje_dt.strftime("%d/%m/%Y %H:%M")
                    })
                    salvar_dados(COMPROVANTES_FILE, st.session_state.comprovantes)
                    st.success("🎉 Comprovante enviado com sucesso para validação da administração!")
        
        st.markdown("---")
        st.write("#### 📋 Meus Comprovantes Enviados")
        meus_comps = [c for c in st.session_state.comprovantes if c["jogadora"] == st.session_state.usuario_logado]
        if not meus_comps:
            st.info("Nenhum comprovante enviado recentemente.")
        else:
            for c in meus_comps:
                st.markdown(f"<div class='card-interactive' style='padding: 10px 15px;'>• **{c['mes']}** - {c['obs']} <i>(Enviado em {c['data']})</i></div>", unsafe_allow_html=True)
                if os.path.exists(c.get("arquivo", "")):
                    st.image(c["arquivo"], caption="Comprovante enviado", width=250)

    if st.session_state.admin_logged:
        st.markdown("---")
        st.subheader("🔍 Validar Comprovantes Recebidos (Admin)")
        if not st.session_state.comprovantes:
            st.info("Nenhum comprovante pendente.")
        else:
            for idx, comp in enumerate(st.session_state.comprovantes):
                st.markdown(f"""
                <div class='card-interactive'>
                    <b>{comp['jogadora']}</b> — Mês: <code>{comp['mes']}</code> | Obs: <i>{comp['obs']}</i> ({comp['data']})
                </div>
                """, unsafe_allow_html=True)
                
                if os.path.exists(comp.get("arquivo", "")):
                    st.image(comp["arquivo"], caption=f"Comprovante de {comp['jogadora']}", width=300)

                if st.button(f"✅ Aprovar & Registrar no Caixa", key=f"apr_comp_{idx}"):
                    st.session_state.financeiro.append({
                        "data": hoje_dt.strftime("%d/%m/%Y"),
                        "descricao": f"Mensalidade - {comp['jogadora']} ({comp['mes']})",
                        "tipo": "Entrada",
                        "valor": 50.0,
                        "categoria": "Mensalidade"
                    })
                    salvar_dados(FINANCE_FILE, st.session_state.financeiro)
                    
                    st.session_state.comprovantes.pop(idx)
                    salvar_dados(COMPROVANTES_FILE, st.session_state.comprovantes)
                    st.success(f"Pagamento de {comp['jogadora']} aprovado e adicionado ao caixa!")
                    st.rerun()

elif menu == "📜 Regulamento":
    st.subheader("📜 Regulamento Interno do Peladinha FC")
    for reg in st.session_state.regulamento:
        st.markdown(f"""
        <div class='card-interactive'>
            <h3 style='color: #831843; margin-bottom: 8px;'>{reg['topico']}</h3>
            <p style='margin: 0;'>{reg['regrinha']}</p>
        </div>
        """, unsafe_allow_html=True)

    if st.session_state.admin_logged:
        st.markdown("---")
        st.write("#### 🛠️ Adicionar / Editar Regras (Admin)")
        with st.form("form_add_regra", clear_on_submit=True):
            r_topico = st.text_input("Título do Tópico")
            r_texto = st.text_area("Regra / Descrição")
            if st.form_submit_button("➕ Adicionar Regra", use_container_width=True):
                if r_topico and r_texto:
                    st.session_state.regulamento.append({"topico": r_topico, "regrinha": r_texto})
                    salvar_dados(REGULAMENTO_FILE, st.session_state.regulamento)
                    st.success("Regra adicionada com sucesso!")
                    st.rerun()

elif menu == "📋 Elenco de Jogadoras":
    st.subheader("📋 Gestão e Elenco de Jogadoras")
    if not st.session_state.jogadoras:
        st.info("Nenhuma jogadora cadastrada.")
    else:
        if st.session_state.admin_logged:
            st.write("### ✏️ Gerenciar Credenciais, Editar ou Excluir Jogadoras (Admin)")
            opcoes_jogs = [f"{i}: {j['nome']} ({j.get('tipo', 'Avulso')})" for i, j in enumerate(st.session_state.jogadoras)]
            j_escolhida_idx = st.selectbox("Selecione a jogadora para gerenciar:", range(len(opcoes_jogs)), format_func=lambda x: opcoes_jogs[x])
            
            if j_escolhida_idx is not None:
                jog_reg = st.session_state.jogadoras[j_escolhida_idx]
                with st.form(f"form_admin_edit_jog_{j_escolhida_idx}"):
                    ed_nome = st.text_input("Nome", value=jog_reg.get("nome", ""))
                    ed_nasc = st.text_input("Nascimento", value=jog_reg.get("nascimento", ""))
                    ed_tipo = st.selectbox("Tipo", ["Avulso", "Mensalista"], index=0 if jog_reg.get("tipo", "Avulso") == "Avulso" else 1)
                    ed_login = st.text_input("Login", value=jog_reg.get("login", ""))
                    ed_senha = st.text_input("Senha", value=jog_reg.get("senha", ""))
                    
                    c_e1, c_e2 = st.columns(2)
                    btn_salvar_j = c_e1.form_submit_button("💾 Salvar Alterações", use_container_width=True)
                    btn_excluir_j = c_e2.form_submit_button("🗑️ Excluir Jogadora", use_container_width=True)

                    if btn_salvar_j:
                        jog_reg["nome"] = ed_nome.strip()
                        jog_reg["nascimento"] = ed_nasc.strip()
                        jog_reg["tipo"] = ed_tipo
                        jog_reg["login"] = ed_login.strip()
                        jog_reg["senha"] = ed_senha.strip()
                        salvar_dados(DATA_FILE, st.session_state.jogadoras)
                        st.success("Dados da jogadora atualizados com sucesso!")
                        st.rerun()

                    if btn_excluir_j:
                        st.session_state.jogadoras.pop(j_escolhida_idx)
                        salvar_dados(DATA_FILE, st.session_state.jogadoras)
                        st.success("Jogadora excluída com sucesso!")
                        st.rerun()
            st.markdown("---")

        st.write("### 🏟️ Elenco Atual")
        for j in st.session_state.jogadoras:
            st.markdown(f"""
            <div class='card-interactive' style='display: flex; justify-content: space-between; align-items: center;'>
                <div>
                    <b>⚽ {j['nome']}</b><br>
                    <small>Tipo: <code>{j.get('tipo', 'Avulso')}</code> | Nascimento: {j.get('nascimento', 'Não inf.')}</small>
                </div>
                <div>
                    <span style='background: #FCE7F3; color: #831843; padding: 4px 10px; border-radius: 8px; font-weight: 600; font-size: 0.85rem;'>Ativa</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

elif menu == "⚙️ Painel Admin":
    if not st.session_state.admin_logged:
        st.error("🔒 Faça login como Administrador para acessar este painel.")
    else:
        st.subheader("⚙️ Painel de Controle da Administração")
        tab_ap_cad, tab_ap_avisos = st.tabs([
            "👥 Aprovar Cadastros", 
            "📢 Configurar Avisos & Vagas"
        ])

        with tab_ap_cad:
            st.write("### 👥 Aprovação de Novas Jogadoras")
            pendentes = [j for j in st.session_state.jogadoras if j.get("status") == "Pendente"]
            if not pendentes:
                st.info("Nenhum cadastro pendente no momento.")
            else:
                for idx, j in enumerate(pendentes):
                    col_p1, col_p2, col_p3 = st.columns([3, 1, 1])
                    col_p1.write(f"**{j['nome']}** (`{j['login']}`) - Tipo: *{j.get('tipo', 'Avulso')}*")
                    if col_p2.button("✅ Aprovar", key=f"apr_j_{idx}"):
                        j["status"] = "Ativo"
                        salvar_dados(DATA_FILE, st.session_state.jogadoras)
                        st.success(f"Jogadora {j['nome']} aprovada!")
                        st.rerun()
                    if col_p3.button("❌ Recusar", key=f"rec_j_{idx}"):
                        st.session_state.jogadoras = [item for item in st.session_state.jogadoras if item.get("login") != j.get("login")]
                        salvar_dados(DATA_FILE, st.session_state.jogadoras)
                        st.warning(f"Cadastro de {j['nome']} recusado.")
                        st.rerun()

        with tab_ap_avisos:
            st.write("### 📢 Configurações Gerais")
            with st.form("form_config_geral"):
                cfg_vagas = st.number_input("Limite de Vagas no Jogo", min_value=5, max_value=40, value=int(st.session_state.avisos.get("limite_vagas", 15)))
                cfg_pix = st.text_input("Chave Pix Oficial", value=st.session_state.avisos.get("pix", ""))
                cfg_venc = st.text_input("Data de Vencimento", value=st.session_state.avisos.get("vencimento", ""))
                cfg_recado = st.text_area("Recado Rápido / Aviso do Topo", value=st.session_state.avisos.get("recado", ""))

                if st.form_submit_button("💾 Salvar Configurações", use_container_width=True):
                    st.session_state.avisos = {
                        "limite_vagas": cfg_vagas,
                        "pix": cfg_pix,
                        "vencimento": cfg_venc,
                        "recado": cfg_recado
                    }
                    salvar_dados(AVISOS_FILE, st.session_state.avisos)
                    st.success("Configurações atualizadas com sucesso!")
                    st.rerun()
