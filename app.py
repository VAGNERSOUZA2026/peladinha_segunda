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

    /* Cards de Fluxo de Caixa */
    .card-fin-entrada {
        background: #F0FDF4;
        border: 1px solid #BBF7D0;
        border-left: 5px solid #22C55E;
        padding: 12px 15px;
        border-radius: 10px;
        margin-bottom: 10px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.02);
    }
    .card-fin-saida {
        background: #FEF2F2;
        border: 1px solid #FECACA;
        border-left: 5px solid #EF4444;
        padding: 12px 15px;
        border-radius: 10px;
        margin-bottom: 10px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.02);
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
    def_admins = [{"nome": "Desenvolvedor", "login": "admin", "senha": "1980", "principal": True}]
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
            st.success("🎉 Cadastro realizado com sucesso! Aguarde a aprovação de um Administrador.")
            st.session_state.msg_cadastro_sucesso = False
        with st.form("form_login_player"):
            l_user = st.text_input("Login")
            l_pass = st.text_input("Senha", type="password")
            if st.form_submit_button("🔑 Entrar", use_container_width=True):
                user_found = next((j for j in st.session_state.jogadoras if j.get("login") == l_user and j.get("senha") == l_pass), None)
                if user_found:
                    if user_found.get("status") == "Ativo":
                        st.session_state.usuario_logado = user_found["nome"]
                        st.rerun()
                    else:
                        st.warning("⚠️ Seu cadastro está pendente de aprovação pela administração.")
                else:
                    st.error("Login ou senha incorretos!")
    with tab_cad:
        with st.form("form_cad_player", clear_on_submit=True):
            c_nome = st.text_input("Seu Nome *")
            c_nasc = st.text_input("Nascimento (DD/MM) *", placeholder="Ex: 15/05")
            c_tipo = st.selectbox("Deseja se cadastrar como:", ["Avulso", "Mensalista"])
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
                            "tipo": c_tipo, "mes_vigente": mes_vigente_str,
                            "contato": "", "status": "Pendente"
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
                st.session_state.admin_nome = admin_encontrado["nome"] if admin_encontrado else "Desenvolvedor"
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
# LÓGICA DE ORDENAÇÃO DE PRESENÇA (MENSALISTAS x AVULSAS) - SOMENTE ATIVAS
# -----------------------------------------------------------------------------
jogadoras_ativas = [j for j in st.session_state.jogadoras if j.get("status") == "Ativo"]
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
                                st.write(f"• **{item}**")
                            st.markdown("</div>", unsafe_allow_html=True)

elif menu == "📊 Fluxo de Caixa (Admin)":
    if not st.session_state.admin_logged:
        st.error("🔒 Área restrita aos administradores!")
    else:
        st.subheader("📊 Fluxo de Caixa Avançado")
        df_fin = pd.DataFrame(st.session_state.financeiro) if st.session_state.financeiro else pd.DataFrame(columns=["data", "descricao", "tipo", "valor", "categoria"])
        
        # Garantir colunas padrão se os dados antigos não tiverem categoria
        if not df_fin.empty and "categoria" not in df_fin.columns:
            df_fin["categoria"] = "Outros"
            for item in st.session_state.financeiro:
                if "categoria" not in item:
                    item["categoria"] = "Outros"

        # Filtros e Períodos
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
            st.write("### 🗂️ Lançamentos Financeiros (Clique nos cards ou botões abaixo)")
            if not st.session_state.financeiro:
                st.info("Nenhum lançamento cadastrado.")
            else:
                # Filtrar os índices reais com base nos filtros aplicados
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

                        css_card = "card-fin-entrada" if t_tipo == "Entrada" else "card-fin-saida"
                        sinal = "+" if t_tipo == "Entrada" else "-"

                        # Layout do Card Interativo
                        c_card_info, c_card_btn1, c_card_btn2 = st.columns([5, 1, 1])
                        
                        with c_card_info:
                            st.markdown(f"""
                            <div class='{css_card}'>
                                <b>[{t_data}] {t_cat}</b> — {t_desc}<br>
                                <span style='font-size: 1.1rem; font-weight: bold; color: {"#16A34A" if t_tipo=="Entrada" else "#DC2626"};'>
                                    {sinal} R$ {t_val:.2f}
                                </span>
                            </div>
                            """, unsafe_allow_html=True)

                        with c_card_btn1:
                            if st.button("✏️", key=f"btn_edit_card_{i_real}", help="Editar este lançamento"):
                                st.session_state.edit_fin_idx_temp = i_real
                                st.rerun()

                        with c_card_btn2:
                            if st.button("🗑️", key=f"btn_del_card_{i_real}", help="Excluir este lançamento"):
                                st.session_state.financeiro.pop(i_real)
                                salvar_dados(FINANCE_FILE, st.session_state.financeiro)
                                st.success("Lançamento excluído com sucesso!")
                                st.rerun()

                    st.markdown("---")
                    # Botão de exportação CSV geral filtrado
                    df_fin_filtrado = df.iloc[indices_filtrados] if 'df' in locals() and not df.empty else pd.DataFrame(st.session_state.financeiro)
                    if not df_fin_filtrado.empty:
                        cols_to_show = [c for c in ["data", "descricao", "categoria", "tipo", "valor"] if c in df_fin_filtrado.columns]
                        csv_data = df_fin_filtrado[cols_to_show].to_csv(index=False).encode('utf-8')
                        st.download_button(
                            label="📥 Baixar Extrato em CSV",
                            data=csv_data,
                            file_name=f"extrato_financeiro_{hoje_dt.strftime('%Y%m%d')}.csv",
                            mime="text/csv",
                            use_container_width=True
                        )

        with tab_add_fin:
            categorias_entrada = ["Mensalidade", "Avulsa", "Doação / Patrocínio", "Outras Entradas"]
            categorias_saida = ["Aluguel de Quadra", "Água / Gelo", "Material Esportivo (Bolas/Coletes)", "Premiação / Troféus", "Outras Saídas"]

            with st.form("form_fin_melhorado", clear_on_submit=True):
                f_data = st.text_input("Data (DD/MM/AAAA)", value=hoje_dt.strftime("%d/%m/%Y"))
                f_tipo = st.selectbox("Tipo de Lançamento", ["Entrada", "Saída"])
                
                if f_tipo == "Entrada":
                    f_cat = st.selectbox("Categoria", categorias_entrada)
                else:
                    f_cat = st.selectbox("Categoria", categorias_saida)

                f_desc = st.text_input("Descrição / Nome (Ex: Mensalidade da Maria / Aluguel Quadra Terça)")
                f_valor = st.number_input("Valor (R$)", min_value=0.01, step=5.0)
                
                if st.form_submit_button("💾 Salvar Lançamento no Caixa", use_container_width=True):
                    st.session_state.financeiro.append({
                        "data": f_data, 
                        "descricao": f_desc if f_desc else f_cat, 
                        "tipo": f_tipo, 
                        "categoria": f_cat,
                        "valor": float(f_valor)
                    })
                    salvar_dados(FINANCE_FILE, st.session_state.financeiro)
                    st.success("Lançamento salvo com sucesso!")
                    st.rerun()

        with tab_cat_fin:
            st.write("### 📊 Totais por Categoria")
            if not df_fin_filtrado.empty:
                resumo_cat = df_fin_filtrado.groupby(["tipo", "categoria"])["valor"].sum().reset_index()
                st.dataframe(resumo_cat, use_container_width=True, hide_index=True)
                
                st.markdown("---")
                st.write("💡 *Dica: Use o filtro de Mês acima para ver o resumo de categorias de meses específicos.*")
            else:
                st.info("Sem dados suficientes para gerar resumo por categoria.")

        with tab_edit_fin:
            if not st.session_state.financeiro:
                st.info("Nenhum lançamento cadastrado.")
            else:
                # Verifica se veio o índice direto do card clicado
                idx_inicial = st.session_state.get("edit_fin_idx_temp", 0)
                if idx_inicial >= len(st.session_state.financeiro):
                    idx_inicial = 0

                opcoes_fin = [f"{i}. {item['data']} - {item.get('categoria', 'Outros')} - {item['descricao']} (R$ {item['valor']:.2f})" for i, item in enumerate(st.session_state.financeiro)]
                
                idx_sel = st.selectbox("Escolha o registro para editar/apagar:", range(len(opcoes_fin)), index=idx_inicial, format_func=lambda x: opcoes_fin[x])
                
                # Limpa a session state após ler para não travar
                if "edit_fin_idx_temp" in st.session_state:
                    del st.session_state.edit_fin_idx_temp

                reg_sel = st.session_state.financeiro[idx_sel]

                with st.form("form_edit_fin"):
                    ef_data = st.text_input("Data", value=reg_sel.get("data", ""))
                    ef_tipo = st.selectbox("Tipo", ["Entrada", "Saída"], index=0 if reg_sel.get("tipo") == "Entrada" else 1)
                    ef_cat = st.text_input("Categoria", value=reg_sel.get("categoria", "Outros"))
                    ef_desc = st.text_input("Descrição", value=reg_sel.get("descricao", ""))
                    ef_valor = st.number_input("Valor (R$)", value=float(reg_sel.get("valor", 0.0)), min_value=0.01)

                    if st.form_submit_button("💾 Salvar Alterações", use_container_width=True):
                        st.session_state.financeiro[idx_sel] = {
                            "data": ef_data, 
                            "descricao": ef_desc, 
                            "tipo": ef_tipo, 
                            "categoria": ef_cat,
                            "valor": float(ef_valor)
                        }
                        salvar_dados(FINANCE_FILE, st.session_state.financeiro)
                        st.success("Atualizado com sucesso!")
                        st.rerun()

                if st.button("🗑️ Excluir Lançamento", type="primary", use_container_width=True):
                    st.session_state.financeiro.pop(idx_sel)
                    salvar_dados(FINANCE_FILE, st.session_state.financeiro)
                    st.success("Excluído com sucesso!")
                    st.rerun()

elif menu == "💸 Pagamento & Pix":
    st.subheader("💸 Dados para Pagamento e Envio de Comprovante")
    
    st.markdown("### 🔑 Chave Pix Atual")
    pix_atual = st.session_state.avisos.get('pix', 'Não informada')
    st.code(pix_atual, language="text")
    st.write(f"📅 **Vencimento:** {st.session_state.avisos.get('vencimento')}")

    st.markdown("---")

    if st.session_state.admin_logged:
        with st.expander("🛠️ [Admin] Editar Chave Pix e Vencimento"):
            with st.form("form_edit_pix_direto"):
                novo_pix = st.text_input("Chave Pix", value=pix_atual)
                novo_venc = st.text_input("Dia de Vencimento", value=st.session_state.avisos.get("vencimento", ""))
                if st.form_submit_button("💾 Atualizar Chave Pix"):
                    st.session_state.avisos["pix"] = novo_pix
                    st.session_state.avisos["vencimento"] = novo_venc
                    salvar_dados(AVISOS_FILE, st.session_state.avisos)
                    st.success("Chave Pix atualizada com sucesso!")
                    st.rerun()
        st.markdown("---")

    st.subheader("📤 Enviar Comprovante de Pagamento")
    if not st.session_state.usuario_logado and not st.session_state.admin_logged:
        st.warning("⚠️ **Faça login na sua conta no menu lateral para enviar o comprovante automaticamente em seu nome!**")
    else:
        with st.form("form_enviar_comprovante", clear_on_submit=True):
            if st.session_state.admin_logged and not st.session_state.usuario_logado:
                nomes_j_todas = [j["nome"] for j in jogadoras_ativas]
                remetente_sel = st.selectbox("Enviar em nome de:", nomes_j_todas) if nomes_j_todas else "Admin"
            else:
                remetente_sel = st.session_state.usuario_logado
                st.write(f"Enviando comprovante como: **{remetente_sel}**")

            detalhes_pag = st.text_input("Detalhes / Observação (Ex: Mensalidade Referente a Agosto)")
            
            if st.form_submit_button("🚀 Enviar Comprovante", use_container_width=True):
                if remetente_sel:
                    st.session_state.comprovantes.append({
                        "nome": remetente_sel,
                        "detalhes": detalhes_pag.strip() if detalhes_pag else "Pagamento Pix",
                        "data": hoje_dt.strftime("%d/%m/%Y %H:%M"),
                        "status": "Pendente"
                    })
                    salvar_dados(COMPROVANTES_FILE, st.session_state.comprovantes)
                    st.success("Comprovante enviado com sucesso para a análise da administração!")
                else:
                    st.error("Erro ao identificar a jogadora.")

    if st.session_state.admin_logged:
        st.markdown("---")
        st.subheader("📥 Comprovantes Recebidos (Admin)")
        if not st.session_state.comprovantes:
            st.info("Nenhum comprovante enviado no momento.")
        else:
            for idx, comp in enumerate(st.session_state.comprovantes):
                col_c1, col_c2, col_c3 = st.columns([2, 2, 1])
                col_c1.write(f"**{comp['nome']}**")
                col_c2.write(f"{comp['detalhes']} — *{comp['data']}*")
                
                if comp.get("status") == "Pendente":
                    if col_c3.button("✅ Confirmar", key=f"conf_comp_{idx}"):
                        st.session_state.financeiro.append({
                            "data": hoje_dt.strftime("%d/%m/%Y"),
                            "descricao": f"Mensalidade - {comp['nome']}",
                            "tipo": "Entrada",
                            "categoria": "Mensalidade",
                            "valor": 0.0
                        })
                        salvar_dados(FINANCE_FILE, st.session_state.financeiro)
                        
                        st.session_state.comprovantes.pop(idx)
                        salvar_dados(COMPROVANTES_FILE, st.session_state.comprovantes)
                        st.success(f"Pagamento de {comp['nome']} confirmado e adicionado ao caixa!")
                        st.rerun()
                else:
                    col_c3.write("Aprovado")

elif menu == "📜 Regulamento":
    st.subheader("📜 Regulamento do Peladinha FC")
    st.markdown("---")
    for item in st.session_state.regulamento:
        with st.expander(f"**{item['topico']}**", expanded=True):
            st.write(item["regrinha"])

elif menu == "📋 Elenco de Jogadoras":
    st.subheader("🏃‍♀️ Elenco do Peladinha FC")
    tab_elenco, tab_mensalistas = st.tabs(["Todas as Cadastradas", "🌟 Mensalistas Ativas"])
    
    if st.session_state.jogadoras:
        df = pd.DataFrame(st.session_state.jogadoras)
        for j in st.session_state.jogadoras:
            if "mes_vigente" not in j:
                j["mes_vigente"] = mes_vigente_str

        cols_visiveis = [c for c in ["nome", "tipo", "nascimento", "status"] if c in df.columns]
        
        with tab_elenco:
            st.dataframe(df[cols_visiveis], use_container_width=True, hide_index=True)
            
        with tab_mensalistas:
            df_mensalistas = df[(df["tipo"] == "Mensalista") & (df["status"] == "Ativo")]
            if not df_mensalistas.empty:
                st.write("Essas são as mensalistas ativas do nosso grupo neste ano/mês:")
                st.dataframe(df_mensalistas[cols_visiveis], use_container_width=True, hide_index=True)
            else:
                st.info("Nenhuma mensalista ativa registrada no momento.")
    else:
        st.info("Nenhuma jogadora cadastrada.")

elif menu == "⚙️ Painel Admin":
    if not st.session_state.admin_logged:
        st.error("🔒 Área restrita aos administradores!")
    else:
        st.subheader("⚙️ Painel de Controle do Administrador")
        
        tab_pendentes, tab_jogadoras, tab_regulamento, tab_admins = st.tabs([
            "👤 Aprovação de Cadastros", 
            "🏃‍♀️ Gerenciar Jogadoras", 
            "📜 Gerenciar Regulamento", 
            "🛡️ Gerenciar Administradores"
        ])

        with tab_pendentes:
            st.write("### Aprovação de Cadastros Pendentes")
            pendentes = [j for j in st.session_state.jogadoras if j.get("status") == "Pendente"]
            if not pendentes:
                st.info("Nenhum cadastro pendente no momento.")
            else:
                for idx, j in enumerate(pendentes):
                    c_p1, c_p2, c_p3 = st.columns([2, 2, 1])
                    c_p1.write(f"**{j['nome']}** `[{j['tipo']}]`")
                    c_p2.write(f"Nasc: {j.get('nascimento', 'N/I')} | Login: `{j['login']}`")
                    
                    if c_p3.button("✅ Aprovar", key=f"aprovar_j_{idx}"):
                        for jog in st.session_state.jogadoras:
                            if jog["login"] == j["login"]:
                                jog["status"] = "Ativo"
                        salvar_dados(DATA_FILE, st.session_state.jogadoras)
                        st.success(f"Cadastro de {j['nome']} aprovado com sucesso!")
                        st.rerun()

        with tab_jogadoras:
            st.write("### Gerenciar Elenco de Jogadoras Cadastradas")
            if not st.session_state.jogadoras:
                st.info("Nenhuma jogadora cadastrada.")
            else:
                opcoes_jogs = [f"{i}. {j['nome']} ({j.get('tipo', 'Avulso')} - {j.get('status', 'Ativo')})" for i, j in enumerate(st.session_state.jogadoras)]
                j_sel_idx = st.selectbox("Selecione a jogadora para gerenciar:", range(len(opcoes_jogs)), format_func=lambda x: opcoes_jogs[x])
                jog_selecionada = st.session_state.jogadoras[j_sel_idx]

                with st.form("form_edit_jogadora_admin"):
                    edit_nome = st.text_input("Nome", value=jog_selecionada.get("nome", ""))
                    edit_tipo = st.selectbox("Tipo", ["Avulso", "Mensalista"], index=0 if jog_selecionada.get("tipo", "Avulso") == "Avulso" else 1)
                    edit_status = st.selectbox("Status", ["Ativo", "Pendente", "Inativo"], index=["Ativo", "Pendente", "Inativo"].index(jog_selecionada.get("status", "Ativo")))
                    edit_nasc = st.text_input("Nascimento (DD/MM)", value=jog_selecionada.get("nascimento", ""))

                    if st.form_submit_button("💾 Salvar Alterações na Jogadora", use_container_width=True):
                        st.session_state.jogadoras[j_sel_idx].update({
                            "nome": edit_nome.strip(),
                            "tipo": edit_tipo,
                            "status": edit_status,
                            "nascimento": edit_nasc.strip()
                        })
                        salvar_dados(DATA_FILE, st.session_state.jogadoras)
                        st.success("Dados da jogadora atualizados com sucesso!")
                        st.rerun()

                if st.button("🗑️ Excluir Esta Jogadora do Sistema", type="primary", use_container_width=True):
                    removida = st.session_state.jogadoras.pop(j_sel_idx)
                    salvar_dados(DATA_FILE, st.session_state.jogadoras)
                    st.session_state.presencas = [p for p in st.session_state.presencas if obter_nome_p(p) != removida["nome"]]
                    salvar_dados(PRESENCAS_FILE, st.session_state.presencas)
                    st.warning(f"Jogadora {removida['nome']} removida!")
                    st.rerun()

        with tab_regulamento:
            st.write("### Gerenciar Tópicos do Regulamento")
            
            with st.form("form_add_regulamento", clear_on_submit=True):
                st.write("**Adicionar Novo Tópico:**")
                novo_topico = st.text_input("Título do Tópico (Ex: 📌 5. Horário)")
                nova_regrinha = st.text_area("Descrição / Regra")
                if st.form_submit_button("➕ Adicionar Regra", use_container_width=True):
                    if novo_topico and nova_regrinha:
                        st.session_state.regulamento.append({"topico": novo_topico.strip(), "regrinha": nova_regrinha.strip()})
                        salvar_dados(REGULAMENTO_FILE, st.session_state.regulamento)
                        st.success("Regra adicionada!")
                        st.rerun()
                    else:
                        st.error("Preencha o título e a descrição.")

            st.markdown("---")
            st.write("**Editar ou Remover Regras Existentes:**")
            if not st.session_state.regulamento:
                st.info("Nenhum regulamento cadastrado.")
            else:
                opcoes_reg = [f"{i}. {r['topico']}" for i, r in enumerate(st.session_state.regulamento)]
                reg_sel_idx = st.selectbox("Escolha a regra:", range(len(opcoes_reg)), format_func=lambda x: opcoes_reg[x])
                reg_atual = st.session_state.regulamento[reg_sel_idx]

                with st.form("form_edit_regulamento"):
                    ed_top = st.text_input("Título", value=reg_atual["topico"])
                    ed_reg = st.text_area("Descrição", value=reg_atual["regrinha"])
                    if st.form_submit_button("💾 Salvar Alteração na Regra", use_container_width=True):
                        st.session_state.regulamento[reg_sel_idx] = {"topico": ed_top.strip(), "regrinha": ed_reg.strip()}
                        salvar_dados(REGULAMENTO_FILE, st.session_state.regulamento)
                        st.success("Regulamento atualizado!")
                        st.rerun()

                if st.button("🗑️ Excluir Esta Regra", type="primary", use_container_width=True):
                    st.session_state.regulamento.pop(reg_sel_idx)
                    salvar_dados(REGULAMENTO_FILE, st.session_state.regulamento)
                    st.success("Regra removida!")
                    st.rerun()

        with tab_admins:
            st.write("### Gerenciamento de Administradores (Limite de até 3)")
            st.info("ℹ️ O Desenvolvedor (Admin Principal) possui acesso imutável e não pode ser excluído.")

            for idx, adm in enumerate(st.session_state.administradores):
                col_a1, col_a2 = st.columns([3, 1])
                col_a1.write(f"• **{adm['nome']}** (Login: `{adm.get('login')}`)" + (" *(Admin Principal)*" if adm.get("principal") else ""))
                if not adm.get("principal") and len(st.session_state.administradores) > 1:
                    if col_a2.button("🗑️ Remover", key=f"del_adm_{idx}"):
                        st.session_state.administradores.pop(idx)
                        salvar_dados(ADMINS_FILE, st.session_state.administradores)
                        st.success("Administrador removido com sucesso!")
                        st.rerun()

            st.markdown("---")
            st.write("#### ➕ Cadastrar Novo Administrador")
            if len(st.session_state.administradores) >= 3:
                st.warning("⚠️ O limite máximo de 3 administradores já foi atingido.")
            else:
                with st.form("form_novo_admin", clear_on_submit=True):
                    novo_nome_adm = st.text_input("Nome do Administrador")
                    novo_login_adm = st.text_input("Login do Administrador")
                    novo_senha_adm = st.text_input("Senha do Administrador", type="password")
                    
                    if st.form_submit_button("💾 Salvar Novo Administrador", use_container_width=True):
                        if novo_nome_adm and novo_login_adm and novo_senha_adm:
                            if len(st.session_state.administradores) < 3:
                                st.session_state.administradores.append({
                                    "nome": novo_nome_adm.strip(),
                                    "login": novo_login_adm.strip(),
                                    "senha": novo_senha_adm.strip(),
                                    "principal": False
                                })
                                salvar_dados(ADMINS_FILE, st.session_state.administradores)
                                st.success("Novo administrador cadastrado com sucesso!")
                                st.rerun()
                            else:
                                st.error("Limite máximo de 3 administradores atingido.")
                        else:
                            st.error("Preencha todos os campos do administrador!")
