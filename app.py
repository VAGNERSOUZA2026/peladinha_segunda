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
    page_title="Peladinha FC | Gestão de Futebol Feminino",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------------------------------------------------------
# ESTILIZAÇÃO CSS CUSTOMIZADA
# -----------------------------------------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;800&display=swap');
    html, body, [class*="css"] { font-family: 'Poppins', sans-serif; }

    .hero-banner {
        background: linear-gradient(rgba(15, 23, 42, 0.75), rgba(15, 23, 42, 0.85)), 
                    url('https://images.unsplash.com/photo-1518091043644-c1d4457512c6?q=80&w=1200&auto=format&fit=crop');
        background-size: cover;
        background-position: center;
        border-radius: 16px;
        padding: 25px 15px;
        text-align: center;
        color: #FFFFFF;
        box-shadow: 0px 8px 20px rgba(0, 0, 0, 0.15);
        margin-bottom: 20px;
    }
    .hero-title { font-size: 2.0rem; font-weight: 800; margin-bottom: 5px; color: #FFFFFF; }
    .hero-subtitle { font-size: 0.9rem; font-weight: 300; color: #E2E8F0; }

    .card-notice {
        background: #FEF3C7;
        border-left: 6px solid #F59E0B;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 15px;
        color: #78350F;
    }

    .card-bday {
        background: linear-gradient(135deg, #FCE7F3 0%, #FBCFE8 100%);
        border-left: 6px solid #EC4899;
        padding: 18px;
        border-radius: 12px;
        margin-bottom: 20px;
        color: #831843;
        text-align: center;
        font-size: 1.1rem;
        box-shadow: 0px 4px 12px rgba(0,0,0,0.05);
    }

    .card-team {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-top: 5px solid #EC4899;
        border-radius: 12px;
        padding: 15px;
        margin-bottom: 15px;
    }

    .developer-footer {
        background: #0F172A;
        color: #94A3B8;
        text-align: center;
        padding: 12px;
        border-radius: 10px;
        margin-top: 30px;
        font-size: 0.85rem;
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
    def_admins = [{"nome": "Admin Principal", "login": "admin", "senha": "1980", "principal": True}]
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
if "aba_ativa" not in st.session_state:
    st.session_state.aba_ativa = "Entrar"
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
# MENU LATERAL (SIDEBAR)
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
    tab_log, tab_cad = st.sidebar.tabs(["Entrar", "Cadastrar"] if st.session_state.aba_ativa == "Entrar" else ["Cadastrar", "Entrar"])
    with tab_log:
        if st.session_state.msg_cadastro_sucesso:
            st.success("🎉 Cadastro realizado com sucesso! Faça login:")
            st.session_state.msg_cadastro_sucesso = False
        with st.form("form_login_player"):
            l_user = st.text_input("Login")
            l_pass = st.text_input("Senha", type="password")
            if st.form_submit_button("🔑 Entrar", use_container_width=True):
                user_found = next((j for j in st.session_state.jogadoras if j.get("login") == l_user and j.get("senha") == l_pass), None)
                if user_found:
                    st.session_state.usuario_logado = user_found["nome"]
                    st.rerun()
                else:
                    st.error("Login ou senha incorretos!")
    with tab_cad:
        with st.form("form_cad_player", clear_on_submit=True):
            c_nome = st.text_input("Seu Nome *")
            c_nasc = st.text_input("Nascimento (DD/MM) *", placeholder="Ex: 15/05")
            c_user = st.text_input("Escolha um Login *")
            c_pass = st.text_input("Escolha uma Senha *", type="password")
            if st.form_submit_button("📝 Criar Conta", use_container_width=True):
                if c_nome and c_user and c_pass:
                    if any(j.get("login") == c_user.strip() for j in st.session_state.jogadoras):
                        st.error("Este Login já está em uso. Escolha outro!")
                    else:
                        st.session_state.jogadoras.append({
                            "nome": c_nome.strip(), "nascimento": c_nasc.strip(),
                            "login": c_user.strip(), "senha": c_pass.strip(),
                            "tipo": "Avulso", "mes_vigente": mes_vigente_str,
                            "contato": "", "status": "Ativo"
                        })
                        salvar_dados(DATA_FILE, st.session_state.jogadoras)
                        st.session_state.aba_ativa = "Entrar"
                        st.session_state.msg_cadastro_sucesso = True
                        st.rerun()
                else:
                    st.error("Preencha Nome, Login e Senha!")

st.sidebar.markdown("---")
st.sidebar.subheader("🔒 Área do Administrador")

if not st.session_state.admin_logged:
    with st.sidebar.form("form_login_admin"):
        adm_input = st.text_input("Login ou Senha Admin", type="password")
        if st.form_submit_button("Acessar Como Admin", use_container_width=True):
            admin_encontrado = next((adm for adm in st.session_state.administradores if adm_input in [adm.get("senha"), adm.get("login")]), None)
            if admin_encontrado or adm_input == "1980":
                st.session_state.admin_logged = True
                st.session_state.admin_nome = admin_encontrado["nome"] if admin_encontrado else "Admin Principal"
                st.rerun()
            else:
                st.error("Senha/Login Admin incorreto!")
else:
    st.sidebar.info(f"🔑 Admin: **{st.session_state.admin_nome}**")
    if st.sidebar.button("Sair do Admin"):
        st.session_state.admin_logged = False
        st.session_state.admin_nome = ""
        st.rerun()

# -----------------------------------------------------------------------------
# LÓGICA DE ORDENAÇÃO DE PRESENÇA (MENSALISTAS x AVULSAS)
# -----------------------------------------------------------------------------
lista_atual = sorted(st.session_state.presencas, key=lambda x: x.get("dt_confirmacao", x.get("hora", "")))
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
# SORTEIO AUTOMÁTICO (SEGUNDA-FEIRA ÀS 18:30)
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
                st.write(f"**{i}.** {nome_p} `[{tipo_p}]` — *(às {hora_p})*")

        st.markdown("---")
        st.markdown(f"### ⏳ Fila de Espera ({len(espera)})")
        if not espera:
            st.caption("Nenhuma jogadora na fila de espera.")
        else:
            for i, p in enumerate(espera, 1):
                nome_p, hora_p, tipo_p = obter_nome_p(p), obter_hora_p(p), obter_tipo_p(p)
                badge = "🏃 Avulsa" if tipo_p == "Avulso" else "⭐ Mensalista"
                st.write(f"**{i}º na espera:** {nome_p} `[{badge}]` — *(às {hora_p})*")

    with col_acoes:
        st.subheader("✍️ Marcar Minha Presença")
        if not (st.session_state.usuario_logado or st.session_state.admin_logged):
            st.warning("⚠️ **Faça Login no menu lateral para confirmar presença!**")
        else:
            with st.form("form_presenca_express"):
                if st.session_state.admin_logged and not st.session_state.usuario_logado:
                    nomes_cad = [j["nome"] for j in st.session_state.jogadoras]
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
                        st.warning("Seu nome já está registrado na lista!")
                    else:
                        st.session_state.presencas.append({
                            "nome": jogadora_sel, 
                            "hora": hoje_dt.strftime("%H:%M"),
                            "tipo": tipo_j,
                            "dt_confirmacao": hoje_dt.isoformat()
                        })
                        salvar_dados(PRESENCAS_FILE, st.session_state.presencas)
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
            if st.button("🧹 Zerar Toda a Lista", use_container_width=True):
                st.session_state.presencas = []
                salvar_dados(PRESENCAS_FILE, [])
                st.session_state.sorteio_oficial = {}
                salvar_dados(SORTEIO_FILE, {})
                st.warning("Lista e sorteios zerados!")
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
                        st.write(f"• **{item}**")
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
                   
