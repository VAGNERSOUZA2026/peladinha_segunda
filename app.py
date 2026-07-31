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
        {"topico": "📌 1. Prioridade nas Vagas", "regrinha": "As jogadoras MENSALISTAS têm prioridade na confirmação de presença até 24 horas antes da partida. Após esse prazo, as vagas restantes ficam liberadas para as jogadoras AVULSAS."},
        {"topico": "⏳ 2. Fila de Espera e Horários", "regrinha": "Atingido o limite de vagas, as confirmações adicionais entram automaticamente na fila de espera. Chegar com pelo menos 10 minutos de antecedência."},
        {"topico": "❌ 3. Desistências e Faltas", "regrinha": "Desistências devem ser avisadas com no mínimo 4 horas de antecedência pelo aplicativo. Faltas sem aviso prévio sujeitam a jogadora ao pagamento da taxa avulsa."},
        {"topico": "💸 4. Mensalidades e Pagamento", "regrinha": "As mensalidades devem ser pagas impreterivelmente até a data de vencimento estipulada via Pix. O não pagamento impede a prioridade na lista de confirmação."},
        {"topico": "🤝 5. Fair Play e Respeito", "regrinha": "Respeito mútuo entre todas as jogadoras e administradores. Discussões ríspidas ou faltas desleais não serão toleradas."}
    ])

if "usuario_logado" not in st.session_state:
    st.session_state.usuario_logado = None

if "admin_logged" not in st.session_state:
    st.session_state.admin_logged = False

if "admin_nome" not in st.session_state:
    st.session_state.admin_nome = ""

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
# VERIFICAÇÃO DE ANIVERSÁRIO DO DIA
# -----------------------------------------------------------------------------
hoje_dt = datetime.now()
hoje_str = hoje_dt.strftime("%d/%m")
mes_vigente_str = hoje_dt.strftime("%m/%Y")

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
        O Peladinha FC deseja a você um FELIZ ANIVERSÁRIO! Muita saúde, alegria e gols hoje e sempre! ⚽🎈
    </div>
    """, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# MENU LATERAL (SIDEBAR)
# -----------------------------------------------------------------------------
st.sidebar.title("📌 Navegação")

lista_menu = [
    "📌 Presença no Jogo", 
    "💸 Pagamento & Pix",
    "📜 Regulamento",
    "📋 Elenco de Jogadoras"
]

if st.session_state.admin_logged:
    lista_menu.insert(1, "🔀 Sorteio de Times (Admin)")
    lista_menu.insert(2, "📊 Fluxo de Caixa (Admin)")

lista_menu.append("⚙️ Painel Admin")

menu = st.sidebar.radio("Ir para:", lista_menu)

st.sidebar.markdown("---")
st.sidebar.title("👤 Área da Jogadora")

if st.session_state.usuario_logado:
    st.sidebar.success(f"Logada: **{st.session_state.usuario_logado}**")
    if st.sidebar.button("🚪 Sair"):
        st.session_state.usuario_logado = None
        st.rerun()
else:
    tab_log, tab_cad = st.sidebar.tabs(["Entrar", "Cadastrar"])
    with tab_log:
        l_user = st.text_input("Login", key="l_user")
        l_pass = st.text_input("Senha", type="password", key="l_pass")
        if st.button("🔑 Entrar"):
            user_found = next((j for j in st.session_state.jogadoras if j.get("login") == l_user and j.get("senha") == l_pass), None)
            if user_found:
                st.session_state.usuario_logado = user_found["nome"]
                st.rerun()
            else:
                st.sidebar.error("Login incorreto!")

    with tab_cad:
        c_nome = st.text_input("Seu Nome *")
        c_nasc = st.text_input("Data de Nascimento (DD/MM) *", placeholder="Ex: 15/05")
        c_user = st.text_input("Escolha um Login *")
        c_pass = st.text_input("Escolha uma Senha *", type="password")
        if st.button("📝 Criar Conta"):
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
                st.sidebar.success("Conta criada! Faça login.")
                st.rerun()
            else:
                st.sidebar.error("Preencha Nome, Login e Senha!")

st.sidebar.markdown("---")
st.sidebar.subheader("🔒 Área do Administrador")

if not st.session_state.admin_logged:
    adm_input = st.sidebar.text_input("Login ou Senha Admin", type="password")
    if st.sidebar.button("Acessar Como Admin"):
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
            st.sidebar.error("Senha/Login Admin incorreto!")
else:
    st.sidebar.info(f"🔑 Admin: **{st.session_state.admin_nome}**")
    if st.sidebar.button("Sair do Admin"):
        st.session_state.admin_logged = False
        st.session_state.admin_nome = ""
        st.rerun()


# -----------------------------------------------------------------------------
# PÁGINA 1: PRESENÇA NO JOGO (PÚBLICA)
# -----------------------------------------------------------------------------
if menu == "📌 Presença no Jogo":
    limite = st.session_state.avisos.get("limite_vagas", 10)

    st.markdown(f"""
    <div class='card-notice'>
        📢 <b>AVISOS:</b> Limitado a <b>{limite} vagas</b>. <br>
        💡 <i>{st.session_state.avisos.get('recado')}</i>
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
            for i, nome in enumerate(confirmadas, 1):
                st.write(f"**{i}.** {nome}")

        if espera:
            st.markdown("---")
            st.markdown(f"### ⏳ Fila de Espera ({len(espera)})")
            for i, nome in enumerate(espera, 1):
                st.write(f"**{i}.** {nome} *(Aguardando vaga)*")

    with col_acoes:
        st.subheader("✍️ Marcar Minha Presença")
        
        pode_mexer = st.session_state.usuario_logado or st.session_state.admin_logged

        if not pode_mexer:
            st.warning("⚠️ **Você precisa estar logado para confirmar presença!**")
            st.info("👈 Acesse a **Área da Jogadora** na barra lateral para fazer Login ou Criar Conta.")
        else:
            if st.session_state.admin_logged and not st.session_state.usuario_logado:
                nomes_cad = [j["nome"] for j in st.session_state.jogadoras]
                jogadora_sel = st.selectbox("Selecione a jogadora para alterar:", nomes_cad) if nomes_cad else None
            else:
                jogadora_sel = st.session_state.usuario_logado
                st.success(f"Conectada como: **{jogadora_sel}**")

            if jogadora_sel:
                if st.button("👍 Confirmar Presença", use_container_width=True):
                    if jogadora_sel in st.session_state.presencas:
                        st.warning("Você já está na lista!")
                    else:
                        st.session_state.presencas.append(jogadora_sel)
                        salvar_dados(PRESENCAS_FILE, st.session_state.presencas)
                        st.success("Presença confirmada!")
                        st.rerun()

                if st.button("❌ Cancelar Presença", use_container_width=True):
                    if jogadora_sel in st.session_state.presencas:
                        st.session_state.presencas.remove(jogadora_sel)
                        salvar_dados(PRESENCAS_FILE, st.session_state.presencas)
                        st.info("Presença cancelada.")
                        st.rerun()
                    else:
                        st.error("Seu nome não está na lista.")

        if st.session_state.admin_logged:
            st.markdown("---")
            st.subheader("🚨 Ações de Admin")
            if st.button("🧹 Zerar Toda a Lista", use_container_width=True):
                st.session_state.presencas = []
                salvar_dados(PRESENCAS_FILE, [])
                st.warning("Lista zerada!")
                st.rerun()


# -----------------------------------------------------------------------------
# PÁGINA 2: SORTEIO DE TIMES (EXCLUSIVO ADMIN)
# -----------------------------------------------------------------------------
elif menu == "🔀 Sorteio de Times (Admin)":
    if not st.session_state.admin_logged:
        st.error("🔒 Área restrita! Apenas administradores podem sortear os times.")
    else:
        st.subheader("🔀 Sorteio de Times")
        
        limite = st.session_state.avisos.get("limite_vagas", 10)
        confirmadas = st.session_state.presencas[:limite]

        st.write(f"Total na lista de confirmadas: **{len(confirmadas)} jogadoras**")

        qtd_times = st.slider("Dividir em quantos times?", 2, 4, 2)

        if st.button("🎲 Sortear Times Agora", use_container_width=True):
            if len(confirmadas) < qtd_times:
                st.error("Poucas jogadoras na lista de confirmadas para realizar o sorteio.")
            else:
                temp = confirmadas.copy()
                random.shuffle(temp)
                times = [[] for _ in range(qtd_times)]
                for idx, p in enumerate(temp):
                    times[idx % qtd_times].append(p)

                cols = st.columns(qtd_times)
                for i, t in enumerate(times):
                    with cols[i]:
                        st.markdown(f"<div class='card-team'><h3>⚽ Time {i+1}</h3>", unsafe_allow_html=True)
                        for item in t:
                            st.write(f"• **{item}**")
                        st.markdown("</div>", unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# PÁGINA 3: FLUXO DE CAIXA COM EDIÇÃO E EXCLUSÃO (EXCLUSIVO ADMIN)
# -----------------------------------------------------------------------------
elif menu == "📊 Fluxo de Caixa (Admin)":
    if not st.session_state.admin_logged:
        st.error("🔒 Área restrita! Faça login como administrador.")
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
        
        tab_list_fin, tab_add_fin, tab_edit_fin = st.tabs(["📜 Extrato Lançamentos", "➕ Novo Lançamento", "✏️ Editar / Excluir Lançamentos"])

        with tab_list_fin:
            if not df_fin.empty:
                st.dataframe(df_fin, use_container_width=True)
            else:
                st.info("Nenhum registro até o momento.")

        with tab_add_fin:
            with st.form("form_fin", clear_on_submit=True):
                f_data = st.text_input("Data (DD/MM/AAAA)", value=datetime.now().strftime("%d/%m/%Y"))
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
                st.write("### Select a despesa/receita para gerenciar:")
                opcoes_fin = [f"{i+1}. {item['data']} - {item['descricao']} (R$ {item['valor']:.2f})" for i, item in enumerate(st.session_state.financeiro)]
                idx_sel = st.selectbox("Escolha o registro:", range(len(opcoes_fin)), format_func=lambda x: opcoes_fin[x])
                
                reg_sel = st.session_state.financeiro[idx_sel]

                with st.form("form_edit_fin"):
                    ef_data = st.text_input("Data", value=reg_sel.get("data", ""))
                    ef_desc = st.text_input("Descrição", value=reg_sel.get("descricao", ""))
                    ef_tipo = st.selectbox("Tipo", ["Entrada", "Saída"], index=0 if reg_sel.get("tipo") == "Entrada" else 1)
                    ef_valor = st.number_input("Valor (R$)", value=float(reg_sel.get("valor", 0.0)), min_value=0.01)

                    c_salv, c_exc = st.columns(2)
                    with c_salv:
                        if st.form_submit_button("💾 Salvar Alterações", use_container_width=True):
                            st.session_state.financeiro[idx_sel] = {
                                "data": ef_data, "descricao": ef_desc, "tipo": ef_tipo, "valor": float(ef_valor)
                            }
                            salvar_dados(FINANCE_FILE, st.session_state.financeiro)
                            st.success("Lançamento atualizado!")
                            st.rerun()

                if st.button("🗑️ Excluir Lançamento", type="primary", use_container_width=True):
                    st.session_state.financeiro.pop(idx_sel)
                    salvar_dados(FINANCE_FILE, st.session_state.financeiro)
                    st.success("Lançamento excluído com sucesso!")
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
# PÁGINA 5: REGULAMENTO POR TÓPICOS
# -----------------------------------------------------------------------------
elif menu == "📜 Regulamento":
    st.subheader("📜 Regulamento do Peladinha FC")
    st.write("Confira as regras oficiais para a boa organização dos nossos jogos:")
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
        
        # Garante a coluna mes_vigente exibida
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
                st.success("Configurações salvas!")
                st.rerun()

        with t_cad:
            with st.form("form_adm_cad", clear_on_submit=True):
                a_nome = st.text_input("Nome Completo *")
                a_nasc = st.text_input("Data de Nascimento (DD/MM)", placeholder="Ex: 22/08")
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
                        st.success(f"Jogadora {a_nome} cadastrada com sucesso!")
                        st.rerun()

        with t_ger_jog:
            st.write("### ✏️ Editar ou Excluir Jogadoras")
            if not st.session_state.jogadoras:
                st.info("Nenhuma jogadora no elenco.")
            else:
                nomes_jog = [f"{j['nome']} ({j.get('tipo', 'Avulso')})" for j in st.session_state.jogadoras]
                idx_j_sel = st.selectbox("Selecione a jogadora para gerenciar:", range(len(nomes_jog)), format_func=lambda x: nomes_jog[x])
                
                j_obj = st.session_state.jogadoras[idx_j_sel]

                st.markdown("---")
                st.info(f"📅 **Mês Vigente Aplicado:** {mes_vigente_str}")

                with st.form("form_edit_jog"):
                    ej_nome = st.text_input("Nome Completo", value=j_obj.get("nome", ""))
                    ej_tipo = st.selectbox("Categoria no Mês Vigente", ["Mensalista", "Avulso"], index=0 if j_obj.get("tipo") == "Mensalista" else 1)
                    ej_nasc = st.text_input("Data Nascimento (DD/MM)", value=j_obj.get("nascimento", ""))
                    ej_user = st.text_input("Login", value=j_obj.get("login", ""))
                    ej_pass = st.text_input("Senha", value=j_obj.get("senha", ""), type="password")
                    ej_cont = st.text_input("WhatsApp", value=j_obj.get("contato", ""))

                    if st.form_submit_button("💾 Salvar Alterações da Jogadora", use_container_width=True):
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
                        st.success(f"Dados de {ej_nome} salvos para o mês {mes_vigente_str}!")
                        st.rerun()

                if st.button("🗑️ Excluir Jogadora do Elenco", type="primary", use_container_width=True):
                    jog_removida = st.session_state.jogadoras.pop(idx_j_sel)
                    salvar_dados(DATA_FILE, st.session_state.jogadoras)
                    st.success(f"Jogadora {jog_removida['nome']} removida permanentemente!")
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
                            st.success("Administrador removido!")
                            st.rerun()

            total_admins = len(st.session_state.administradores)
            st.markdown("---")
            st.info(f"Cadastrados: **{total_admins} / 4 administradores**")

            if total_admins < 4:
                st.write("#### ➕ Adicionar Novo Administrador Secundário")
                with st.form("form_novo_adm", clear_on_submit=True):
                    adm_n = st.text_input("Nome do Admin *")
                    adm_l = st.text_input("Login do Admin *")
                    adm_s = st.text_input("Senha do Admin *", type="password")

                    if st.form_submit_button("💾 Salvar Administrador", use_container_width=True):
                        if adm_n.strip() and adm_l.strip() and adm_s.strip():
                            st.session_state.administradores.append({
                                "nome": adm_n.strip(),
                                "login": adm_l.strip(),
                                "senha": adm_s.strip(),
                                "principal": False
                            })
                            salvar_dados(ADMINS_FILE, st.session_state.administradores)
                            st.success(f"Admin {adm_n} cadastrado!")
                            st.rerun()
                        else:
                            st.error("Preencha todos os campos do Administrador!")

        with t_reg:
            st.write("### 📝 Adicionar Novo Tópico ao Regulamento")
            with st.form("form_novo_reg", clear_on_submit=True):
                r_topico = st.text_input("Título do Tópico", placeholder="Ex: 📌 6. Uso de Uniformes")
                r_texto = st.text_area("Descrição da Regra")

                if st.form_submit_button("➕ Adicionar Regra", use_container_width=True):
                    if r_topico and r_texto:
                        st.session_state.regulamento.append({
                            "topico": r_topico.strip(),
                            "regrinha": r_texto.strip()
                        })
                        salvar_dados(REGULAMENTO_FILE, st.session_state.regulamento)
                        st.success("Regra adicionada ao regulamento!")
                        st.rerun()

# RODAPÉ
st.markdown("<div class='developer-footer'>Desenvolvido por <b>Vagner Souza / Ciência da Computação</b></div>", unsafe_allow_html=True)
