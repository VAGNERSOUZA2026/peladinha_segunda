import streamlit as st
import pandas as pd
import json
import os
import random
from datetime import datetime

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

if "jogadoras" not in st.session_state:
    st.session_state.jogadoras = carregar_dados(DATA_FILE, [])

if "presencas" not in st.session_state:
    st.session_state.presencas = carregar_dados(PRESENCAS_FILE, [])

if "financeiro" not in st.session_state:
    st.session_state.financeiro = carregar_dados(FINANCE_FILE, [])

if "administradores" not in st.session_state:
    def_admins = [
        {"nome": "Admin Principal", "login": "admin", "senha": "1980", "principal": True}
    ]
    st.session_state.administradores = carregar_dados(ADMINS_FILE, def_admins)

if "avisos" not in st.session_state:
    st.session_state.avisos = carregar_dados(AVISOS_FILE, {
        "vencimento": "Todo dia 10 de cada mês",
        "recado": "Favor chegarem 10 minutos antes para organizar o jogo!",
        "pix": "peladinhafc@email.com",
        "limite_vagas": 10
    })

if "regulamento" not in st.session_state:
    st.session_state.regulamento = carregar_dados(REGULAMENTO_FILE, [
        {"topico": "📌 1. Prioridade nas Vagas", "regrinha": "As jogadoras MENSALISTAS têm prioridade na confirmação de presença até 24 horas antes da partida."},
        {"topico": "⏳ 2. Fila de Espera e Horários", "regrinha": "Atingido o limite de vagas, as confirmações adicionais entram automaticamente na fila de espera."},
        {"topico": "❌ 3. Desistências e Faltas", "regrinha": "Desistências devem ser avisadas com antecedência pelo aplicativo. Faltas sem aviso sujeitam à taxa avulsa."},
        {"topico": "💸 4. Mensalidades e Pagamento", "regrinha": "As mensalidades devem ser pagas via Pix até a data estipulada de vencimento."},
        {"topico": "🤝 5. Fair Play e Respeito", "regrinha": "Respeito mútuo entre todas as jogadoras e administradores. Jogamos pela diversão e saúde!"},
        {"topico": "📌 6. Sorteio Oficial e Ajuste de Quadra", "regrinha": "• Sorteio Oficial: Feito automaticamente pelo aplicativo às 18:00.\n• Ajuste na Quadra: No início do jogo, se faltar alguém do sorteio oficial, é feito um sorteio rápido na quadra apenas entre as presentes para não atrasar a partida."}
    ])

if "sorteio_oficial" not in st.session_state:
    st.session_state.sorteio_oficial = carregar_dados(SORTEIO_FILE, {})

if "usuario_logado" not in st.session_state:
    st.session_state.usuario_logado = None

if "admin_logged" not in st.session_state:
    st.session_state.admin_logged = False

if "admin_nome" not in st.session_state:
    st.session_state.admin_nome = ""

# -----------------------------------------------------------------------------
# AUTOMAÇÕES POR HORÁRIO (18:00 SORTEIO AUTOMÁTICO | 20:00 ZERAR LISTA)
# -----------------------------------------------------------------------------
hoje_dt = datetime.now()
hoje_str = hoje_dt.strftime("%d/%m")
mes_vigente_str = hoje_dt.strftime("%m/%Y")
data_hoje_id = hoje_dt.strftime("%Y-%m-%d")

limite_vagas_at = st.session_state.avisos.get("limite_vagas", 10)

# 1. SORTEIO AUTOMÁTICO ÀS 18:00
if hoje_dt.hour >= 18 and st.session_state.get("sorteio_auto_dia") != data_hoje_id:
    confirmadas_nomes = [obter_nome_p(p) for p in st.session_state.presencas[:limite_vagas_at]]
    if len(confirmadas_nomes) >= 2:
        temp = confirmadas_nomes.copy()
        random.shuffle(temp)
        
        # Divide em 2 times automaticamente
        t1 = temp[::2]
        t2 = temp[1::2]
        
        st.session_state.sorteio_oficial = {
            "data": data_hoje_id,
            "hora": "18:00 (Automático)",
            "times": {"Time 1": t1, "Time 2": t2}
        }
        salvar_dados(SORTEIO_FILE, st.session_state.sorteio_oficial)
        st.session_state.sorteio_auto_dia = data_hoje_id

# 2. ZERAR LISTA AUTOMATICAMENTE APÓS AS 20:00
if hoje_dt.hour >= 20 and st.session_state.get("ultima_zeragem") != data_hoje_id:
    st.session_state.presencas = []
    salvar_dados(PRESENCAS_FILE, [])
    st.session_state.sorteio_oficial = {}
    salvar_dados(SORTEIO_FILE, {})
    st.session_state.ultima_zeragem = data_hoje_id

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
aniversariantes_hoje = [
    j["nome"] for j in st.session_state.jogadoras 
    if j.get("nascimento", "").strip() == hoje_str
]

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

lista_menu = [
    "📌 Presença no Jogo", 
    "🔀 Sorteio de Times",
    "💸 Pagamento & Pix",
    "📜 Regulamento",
    "📋 Elenco de Jogadoras"
]

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
    tab_log, tab_cad = st.sidebar.tabs(["Entrar", "Cadastrar"])
    
    # FORMULÁRIO DE LOGIN (PERMITE ENTER DIRETO)
    with tab_log:
        with st.form("form_login_player"):
            l_user = st.text_input("Login")
            l_pass = st.text_input("Senha", type="password")
            btn_log = st.form_submit_button("🔑 Entrar", use_container_width=True)
            
            if btn_log:
                user_found = next((j for j in st.session_state.jogadoras if j.get("login") == l_user and j.get("senha") == l_pass), None)
                if user_found:
                    st.session_state.usuario_logado = user_found["nome"]
                    st.rerun()
                else:
                    st.error("Login ou senha incorretos!")

    with tab_cad:
        with st.form("form_cad_player"):
            c_nome = st.text_input("Seu Nome *")
            c_nasc = st.text_input("Nascimento (DD/MM) *", placeholder="Ex: 15/05")
            c_user = st.text_input("Escolha um Login *")
            c_pass = st.text_input("Escolha uma Senha *", type="password")
            btn_cad = st.form_submit_button("📝 Criar Conta", use_container_width=True)
            
            if btn_cad:
                if c_nome and c_user and c_pass:
                    st.session_state.jogadoras.append({
                        "nome": c_nome.strip(), 
                        "nascimento": c_nasc.strip(),
                        "login": c_user.strip(), 
                        "senha": c_pass.strip(),
                        "tipo": "Avulso", 
                        "mes_vigente": mes_vigente_str,
                        "contato": "", 
                        "status": "Ativo"
                    })
                    salvar_dados(DATA_FILE, st.session_state.jogadoras)
                    st.success("Conta criada! Agora faça seu login.")
                    st.rerun()
                else:
                    st.error("Preencha Nome, Login e Senha!")

st.sidebar.markdown("---")
st.sidebar.subheader("🔒 Área do Administrador")

if not st.session_state.admin_logged:
    # FORMULÁRIO DE LOGIN ADMIN (PERMITE ENTER DIRETO)
    with st.sidebar.form("form_login_admin"):
        adm_input = st.text_input("Login ou Senha Admin", type="password")
        btn_adm = st.form_submit_button("Acessar Como Admin", use_container_width=True)
        
        if btn_adm:
            admin_encontrado = None
            for adm in st.session_state.administradores:
                if adm_input == adm.get("senha") or adm_input == adm.get("login"):
                    admin_encontrado = adm
                    break
            
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
# PÁGINA 1: PRESENÇA NO JOGO
# -----------------------------------------------------------------------------
if menu == "📌 Presença no Jogo":
    limite = st.session_state.avisos.get("limite_vagas", 10)

    st.markdown(f"""
    <div class='card-notice'>
        📢 <b>AVISOS:</b> Limitado a <b>{limite} vagas</b>. <br>
        💡 <i>{st.session_state.avisos.get('recado')}</i><br>
        ⏰ <i>Sorteio oficial automático realizado diariamente às <b>18:00</b>.</i>
    </div>
    """, unsafe_allow_html=True)

    col_lista, col_acoes = st.columns([1, 1])

    with col_lista:
        st.subheader("📋 Lista de Presença")
        
        lista_atual = st.session_state.presencas
        confirmadas = lista_atual[:limite]
        espera = lista_atual[limite:]

        st.markdown(f"### 🟢 Confirmadas ({len(confirmadas)}/{limite})")
        if not confirmadas:
            st.info("Nenhuma presença confirmada ainda.")
        else:
            for i, p in enumerate(confirmadas, 1):
                nome_p = obter_nome_p(p)
                hora_p = obter_hora_p(p)
                txt_hora = f" — *(às {hora_p})*" if hora_p else ""
                st.write(f"**{i}.** {nome_p}{txt_hora}")

        if espera:
            st.markdown("---")
            st.markdown(f"### ⏳ Fila de Espera ({len(espera)})")
            for i, p in enumerate(espera, 1):
                nome_p = obter_nome_p(p)
                hora_p = obter_hora_p(p)
                txt_hora = f" — *(às {hora_p})*" if hora_p else ""
                st.write(f"**{i}.** {nome_p}{txt_hora}")

    with col_acoes:
        st.subheader("✍️ Marcar Minha Presença")
        
        pode_mexer = st.session_state.usuario_logado or st.session_state.admin_logged

        if not pode_mexer:
            st.warning("⚠️ **Você precisa estar logada para confirmar presença!**")
            st.info("👈 Faça Login na **Área da Jogadora** no menu lateral.")
        else:
            if st.session_state.admin_logged and not st.session_state.usuario_logado:
                nomes_cad = [j["nome"] for j in st.session_state.jogadoras]
                jogadora_sel = st.selectbox("Selecione a jogadora para alterar:", nomes_cad) if nomes_cad else None
            else:
                jogadora_sel = st.session_state.usuario_logado
                st.success(f"Conectada como: **{jogadora_sel}**")

            if jogadora_sel:
                ja_na_lista = any(obter_nome_p(p) == jogadora_sel for p in st.session_state.presencas)

                if st.button("👍 Confirmar Presença", use_container_width=True):
                    if ja_na_lista:
                        st.warning("Seu nome já está na lista!")
                    else:
                        hora_agora = datetime.now().strftime("%H:%M")
                        st.session_state.presencas.append({"nome": jogadora_sel, "hora": hora_agora})
                        salvar_dados(PRESENCAS_FILE, st.session_state.presencas)
                        st.success(f"Presença confirmada às {hora_agora}!")
                        st.rerun()

                if st.button("❌ Cancelar Presença", use_container_width=True):
                    if ja_na_lista:
                        st.session_state.presencas = [p for p in st.session_state.presencas if obter_nome_p(p) != jogadora_sel]
                        salvar_dados(PRESENCAS_FILE, st.session_state.presencas)
                        st.info("Presença cancelada.")
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
                st.warning("Lista e sorteios zerados!")
                st.rerun()


# -----------------------------------------------------------------------------
# PÁGINA 2: SORTEIO DE TIMES
# -----------------------------------------------------------------------------
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
            st.info("⏰ O Sorteio Oficial é realizado automaticamente às **18:00**.")

        if st.session_state.admin_logged:
            st.markdown("---")
            st.write("#### 🛠️ Forçar Novo Sorteio Oficial (Admin)")
            limite = st.session_state.avisos.get("limite_vagas", 10)
            confirmadas = [obter_nome_p(p) for p in st.session_state.presencas[:limite]]
            qtd_t = st.slider("Dividir em quantos times?", 2, 4, 2, key="slider_oficial")
            
            if st.button("🎲 Executar Sorteio Agora", use_container_width=True):
                if len(confirmadas) < qtd_t:
                    st.error("Número insuficiente de jogadoras confirmadas.")
                else:
                    temp = confirmadas.copy()
                    random.shuffle(temp)
                    res_times = {f"Time {i+1}": [] for i in range(qtd_t)}
                    for idx, p in enumerate(temp):
                        res_times[f"Time {idx % qtd_t + 1}"].append(p)
                    
                    st.session_state.sorteio_oficial = {
                        "data": data_hoje_id,
                        "hora": f"{datetime.now().strftime('%H:%M')} (Manual)",
                        "times": res_times
                    }
                    salvar_dados(SORTEIO_FILE, st.session_state.sorteio_oficial)
                    st.success("Sorteio atualizado!")
                    st.rerun()

    with tab_quadra:
        st.write("### ⚡ Sorteio na Quadra (Com as jogadoras presentes)")
        st.caption("Use esta opção no momento do apito inicial caso faltem jogadoras do sorteio oficial.")
        
        limite = st.session_state.avisos.get("limite_vagas", 10)
        todas_conf = [obter_nome_p(p) for p in st.session_state.presencas[:limite]]

        if not todas_conf:
            st.info("Nenhuma jogadora confirmada na lista.")
        else:
            presentes = st.multiselect("Marque as jogadoras que JÁ CHEGARAM na quadra:", todas_conf, default=todas_conf)
            qtd_t_q = st.slider("Dividir em quantos times?", 2, 4, 2, key="slider_quadra")

            if st.button("🎲 Sortear Apenas Presentes", use_container_width=True):
                if len(presentes) < qtd_t_q:
                    st.error("Selecione mais jogadoras presentes para sortear.")
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


# -----------------------------------------------------------------------------
# PÁGINA 3: FLUXO DE CAIXA (EXCLUSIVO ADMIN)
# -----------------------------------------------------------------------------
elif menu == "📊 Fluxo de Caixa (Admin)":
    if not st.session_state.admin_logged:
        st.error("🔒 Área restrita aos administradores!")
    else:
        st.subheader("📊 Fluxo de Caixa")

        df_fin = pd.DataFrame(st.session_state.financeiro) if st.session_state.financeiro else pd.DataFrame(columns=["data", "descricao", "tipo", "valor"])

        total_in = df_fin[df_fin["tipo"] == "Entrada"]["valor"].sum() if not df_fin.empty else 0.0
        total_out = df_fin[df_fin["tipo"] == "Saída"]["valor"].sum() if not df_fin.empty else 0.0
        
        m1, m2, m3 = st.columns(3)
        m1.metric("🟢 Entradas", f"R$ {total_in:.2f}")
        m2.metric("🔴 Saídas", f"R$ {total_out:.2f}")
        m3.metric("💰 Saldo", f"R$ {total_in - total_out:.2f}")

        st.markdown("---")
        tab_list_fin, tab_add_fin, tab_edit_fin = st.tabs(["📜 Extrato", "➕ Novo Registro", "✏️ Editar / Excluir"])

        with tab_list_fin:
            if not df_fin.empty:
                st.dataframe(df_fin, use_container_width=True)
            else:
                st.info("Nenhum registro postado.")

        with tab_add_fin:
            with st.form("form_fin", clear_on_submit=True):
                f_data = st.text_input("Data", value=datetime.now().strftime("%d/%m/%Y"))
                f_desc = st.text_input("Descrição")
                f_tipo = st.selectbox("Tipo", ["Entrada", "Saída"])
                f_valor = st.number_input("Valor (R$)", min_value=0.01, step=5.0)

                if st.form_submit_button("💾 Salvar Registro", use_container_width=True):
                    st.session_state.financeiro.append({
                        "data": f_data, "descricao": f_desc, "tipo": f_tipo, "valor": float(f_valor)
                    })
                    salvar_dados(FINANCE_FILE, st.session_state.financeiro)
                    st.success("Lançamento salvo!")
                    st.rerun()

        with tab_edit_fin:
            if not st.session_state.financeiro:
                st.info("Nenhum lançamento para editar.")
            else:
                opcoes_fin = [f"{i+1}. {item['data']} - {item['descricao']} (R$ {item['valor']:.2f})" for i, item in enumerate(st.session_state.financeiro)]
                idx_sel = st.selectbox("Escolha o registro:", range(len(opcoes_fin)), format_func=lambda x: opcoes_fin[x])
                reg_sel = st.session_state.financeiro[idx_sel]

                with st.form("form_edit_fin"):
                    ef_data = st.text_input("Data", value=reg_sel.get("data", ""))
                    ef_desc = st.text_input("Descrição", value=reg_sel.get("descricao", ""))
                    ef_tipo = st.selectbox("Tipo", ["Entrada", "Saída"], index=0 if reg_sel.get("tipo") == "Entrada" else 1)
                    ef_valor = st.number_input("Valor (R$)", value=float(reg_sel.get("valor", 0.0)), min_value=0.01)

                    if st.form_submit_button("💾 Salvar Alterações", use_container_width=True):
                        st.session_state.financeiro[idx_sel] = {
                            "data": ef_data, "descricao": ef_desc, "tipo": ef_tipo, "valor": float(ef_valor)
                        }
                        salvar_dados(FINANCE_FILE, st.session_state.financeiro)
                        st.success("Atualizado!")
                        st.rerun()

                if st.button("🗑️ Excluir Lançamento", type="primary", use_container_width=True):
                    st.session_state.financeiro.pop(idx_sel)
                    salvar_dados(FINANCE_FILE, st.session_state.financeiro)
                    st.success("Excluído com sucesso!")
                    st.rerun()


# -----------------------------------------------------------------------------
# PÁGINA 4: PAGAMENTO & PIX
# -----------------------------------------------------------------------------
elif menu == "💸 Pagamento & Pix":
    st.subheader("💸 Dados para Pagamento")
    pix_key = st.session_state.avisos.get("pix", "Não informada")
    st.info(f"🔑 **Chave Pix:** {pix_key}")
    st.write(f"📅 **Vencimento:** {st.session_state.avisos.get('vencimento')}")


# -----------------------------------------------------------------------------
# PÁGINA 5: REGULAMENTO
# -----------------------------------------------------------------------------
elif menu == "📜 Regulamento":
    st.subheader("📜 Regulamento do Peladinha FC")
    st.markdown("---")

    for item in st.session_state.regulamento:
        with st.expander(f"**{item['topico']}**", expanded=True):
            st.write(item["regrinha"])


# -----------------------------------------------------------------------------
# PÁGINA 6: ELENCO DE JOGADORAS
# -----------------------------------------------------------------------------
elif menu == "📋 Elenco de Jogadoras":
    st.subheader("🏃‍♀️ Jogadoras Cadastradas")
    if st.session_state.jogadoras:
        df = pd.DataFrame(st.session_state.jogadoras)
        for j in st.session_state.jogadoras:
            if "mes_vigente" not in j:
                j["mes_vigente"] = mes_vigente_str

        cols_visiveis = [c for c in ["nome", "tipo", "mes_vigente", "nascimento", "status"] if c in df.columns]
        st.dataframe(df[cols_visiveis], use_container_width=True, hide_index=True)
    else:
        st.info("Nenhuma jogadora cadastrada.")


# -----------------------------------------------------------------------------
# PÁGINA 7: PAINEL ADMIN
# -----------------------------------------------------------------------------
elif menu == "⚙️ Painel Admin":
    st.subheader("⚙️ Painel do Administrador")
    if not st.session_state.admin_logged:
        st.error("🔒 Faça login como Admin na barra lateral para acessar esta área!")
    else:
        t_conf, t_cad, t_ger_jog, t_admins, t_reg = st.tabs([
            "⚙️ Configurações Gerais", 
            "➕ Cadastrar Jogadora", 
            "📋 Gerenciar Elenco", 
            "👥 Gerenciar Admins", 
            "📜 Editar Regulamento"
        ])
        
        with t_conf:
            limite_v = st.number_input("Limite de Vagas do Jogo:", value=st.session_state.avisos.get("limite_vagas", 10))
            pix_v = st.text_input("Chave Pix:", value=st.session_state.avisos.get("pix", ""))
            venc_v = st.text_input("Vencimento:", value=st.session_state.avisos.get("vencimento", ""))
            rec_v = st.text_area("Recado/Aviso:", value=st.session_state.avisos.get("recado", ""))
            
            if st.button("💾 Salvar Alterações", use_container_width=True):
                st.session_state.avisos = {
                    "limite_vagas": int(limite_v),
                    "pix": pix_v,
                    "vencimento": venc_v,
                    "recado": rec_v
                }
                salvar_dados(AVISOS_FILE, st.session_state.avisos)
                st.success("Configurações salvadas!")
                st.rerun()

        with t_cad:
            with st.form("form_adm_cad", clear_on_submit=True):
                a_nome = st.text_input("Nome Completo *")
                a_nasc = st.text_input("Data de Nascimento (DD/MM)")
                a_tipo = st.selectbox("Categoria Inicial", ["Mensalista", "Avulso"])
                a_user = st.text_input("Login")
                a_pass = st.text_input("Senha", type="password")
                a_cont = st.text_input("WhatsApp")

                if st.form_submit_button("➕ Cadastrar Jogadora", use_container_width=True):
                    if a_nome.strip():
                        st.session_state.jogadoras.append({
                            "nome": a_nome.strip(),
                            "nascimento": a_nasc.strip(),
                            "tipo": a_tipo,
                            "mes_vigente": mes_vigente_str,
                            "login": a_user.strip(),
                            "senha": a_pass.strip(),
                            "contato": a_cont.strip(),
                            "status": "Ativo"
                        })
                        salvar_dados(DATA_FILE, st.session_state.jogadoras)
                        st.success(f"Jogadora {a_nome} cadastrada!")
                        st.rerun()

        with t_ger_jog:
            st.write("### ✏️ Editar ou Excluir Jogadoras")
            if not st.session_state.jogadoras:
                st.info("Nenhuma jogadora no elenco.")
            else:
                nomes_jog = [f"{j['nome']} ({j.get('tipo', 'Avulso')})" for j in st.session_state.jogadoras]
                idx_j_sel = st.selectbox("Selecione a jogadora:", range(len(nomes_jog)), format_func=lambda x: nomes_jog[x])
                j_obj = st.session_state.jogadoras[idx_j_sel]

                with st.form("form_edit_jog"):
                    ej_nome = st.text_input("Nome Completo", value=j_obj.get("nome", ""))
                    ej_tipo = st.selectbox("Categoria no Mês Vigente", ["Mensalista", "Avulso"], index=0 if j_obj.get("tipo") == "Mensalista" else 1)
                    ej_nasc = st.text_input("Data Nascimento (DD/MM)", value=j_obj.get("nascimento", ""))
                    ej_user = st.text_input("Login", value=j_obj.get("login", ""))
                    ej_pass = st.text_input("Senha", value=j_obj.get("senha", ""), type="password")
                    ej_cont = st.text_input("WhatsApp", value=j_obj.get("contato", ""))

                    if st.form_submit_button("💾 Salvar Alterações", use_container_width=True):
                        st.session_state.jogadoras[idx_j_sel] = {
                            "nome": ej_nome.strip(),
                            "nascimento": ej_nasc.strip(),
                            "tipo": ej_tipo,
                            "mes_vigente": mes_vigente_str,
                            "login": ej_user.strip(),
                            "senha": ej_pass.strip(),
                            "contato": ej_cont.strip(),
                            "status": "Ativo"
                        }
                        salvar_dados(DATA_FILE, st.session_state.jogadoras)
                        st.success(f"Dados atualizados!")
                        st.rerun()

                if st.button("🗑️ Excluir Jogadora", type="primary", use_container_width=True):
                    jog_removida = st.session_state.jogadoras.pop(idx_j_sel)
                    salvar_dados(DATA_FILE, st.session_state.jogadoras)
                    st.success(f"Jogadora {jog_removida['nome']} removida!")
                    st.rerun()

        with t_admins:
            st.write("### 👥 Administradores Cadastrados")
            for index, adm in enumerate(st.session_state.administradores):
                col_info, col_btn = st.columns([3, 1])
                with col_info:
                    st.write(f"👤 **{adm['nome']}** | Login: `{adm['login']}`")
                with col_btn:
                    if adm.get("principal") or index == 0:
                        st.caption("🔒 Principal")
                    else:
                        if st.button("🗑️ Excluir", key=f"del_adm_{index}"):
                            st.session_state.administradores.pop(index)
                            salvar_dados(ADMINS_FILE, st.session_state.administradores)
                            st.success("Removido!")
                            st.rerun()

            total_admins = len(st.session_state.administradores)
            if total_admins < 4:
                st.markdown("---")
                st.write("#### ➕ Adicionar Novo Administrador")
                with st.form("form_novo_adm", clear_on_submit=True):
                    adm_n = st.text_input("Nome *")
                    adm_l = st.text_input("Login *")
                    adm_s = st.text_input("Senha *", type="password")

                    if st.form_submit_button("💾 Salvar Administrador", use_container_width=True):
                        if adm_n.strip() and adm_l.strip() and adm_s.strip():
                            st.session_state.administradores.append({
                                "nome": adm_n.strip(),
                                "login": adm_l.strip(),
                                "senha": adm_s.strip(),
                                "principal": False
                            })
                            salvar_dados(ADMINS_FILE, st.session_state.administradores)
                            st.success("Admin adicionado!")
                            st.rerun()

        with t_reg:
            st.write("### 📝 Adicionar Novo Tópico ao Regulamento")
            with st.form("form_novo_reg", clear_on_submit=True):
                r_topico = st.text_input("Título do Tópico")
                r_texto = st.text_area("Descrição da Regra")

                if st.form_submit_button("➕ Adicionar Regra", use_container_width=True):
                    if r_topico and r_texto:
                        st.session_state.regulamento.append({
                            "topico": r_topico.strip(),
                            "regrinha": r_texto.strip()
                        })
                        salvar_dados(REGULAMENTO_FILE, st.session_state.regulamento)
                        st.success("Regra salva!")
                        st.rerun()

# RODAPÉ
st.markdown("<div class='developer-footer'>Desenvolvido por <b>Vagner Souza / Ciência da Computação</b></div>", unsafe_allow_html=True)
