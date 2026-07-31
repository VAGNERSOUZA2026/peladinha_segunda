import streamlit as st
import pandas as pd
import json
import os
import random
import urllib.parse
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

if "avisos" not in st.session_state:
    st.session_state.avisos = carregar_dados(AVISOS_FILE, {
        "vencimento": "Todo dia 10 de cada mês",
        "recado": "Favor chegarem 10 minutos antes para organizar o jogo!",
        "pix": "peladinhafc@email.com",
        "limite_vagas": 10
    })

if "usuario_logado" not in st.session_state:
    st.session_state.usuario_logado = None

if "admin_logged" not in st.session_state:
    st.session_state.admin_logged = False

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
hoje_str = datetime.now().strftime("%d/%m")
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

# Lista de opções padrão (visíveis para todos)
lista_menu = [
    "📌 Presença no Jogo", 
    "🔀 Sorteio de Times", 
    "💸 Pagamento & Pix",
    "📜 Regulamento",
    "📋 Elenco de Jogadoras"
]

# Se for admin, adiciona o Fluxo de Caixa e o Painel Admin nas opções
if st.session_state.admin_logged:
    lista_menu.append("📊 Fluxo de Caixa (Admin)")

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
    senha_adm = st.sidebar.text_input("Senha Admin", type="password")
    if st.sidebar.button("Acessar Como Admin"):
        if senha_adm == "1980":
            st.session_state.admin_logged = True
            st.rerun()
        else:
            st.sidebar.error("Senha incorreta!")
else:
    st.sidebar.info("🔑 Modo Admin Ativo")
    if st.sidebar.button("Sair do Admin"):
        st.session_state.admin_logged = False
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
# PÁGINA 2: SORTEIO DE TIMES
# -----------------------------------------------------------------------------
elif menu == "🔀 Sorteio de Times":
    st.subheader("🔀 Sorteio de Times")
    
    limite = st.session_state.avisos.get("limite_vagas", 10)
    confirmadas = st.session_state.presencas[:limite]

    st.write(f"Total na lista principal: **{len(confirmadas)} jogadoras**")

    qtd_times = st.slider("Dividir em quantos times?", 2, 4, 2)

    if st.button("🎲 Sortear Times Agora", use_container_width=True):
        if len(confirmadas) < qtd_times:
            st.error("Poucas jogadoras para sortear.")
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
# PÁGINA 3: FLUXO DE CAIXA (EXCLUSIVO ADMIN)
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
        col_f1, col_f2 = st.columns([2, 1])

        with col_f1:
            st.write("### 📜 Lançamentos")
            if not df_fin.empty:
                st.dataframe(df_fin, use_container_width=True)
            else:
                st.info("Nenhum registro até o momento.")

        with col_f2:
            st.write("### ➕ Novo Lançamento")
            with st.form("form_fin", clear_on_submit=True):
                f_data = st.text_input("Data (DD/MM/AAAA)", value="30/07/2026")
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
    st.subheader("📜 Regulamento do Grupo")
    st.markdown("""
    * **Respeito em Primeiro Lugar:** Não serão toleradas ofensas ou brigas.
    * **Pontualidade:** Chegar com 10 minutos de antecedência.
    * **Desistências:** Cancele sua presença no app com pelo menos 4 horas de antecedência.
    * **Pagamento:** Mantenha suas mensalidades e avulsos em dia via Pix.
    """)


# -----------------------------------------------------------------------------
# PÁGINA 6: ELENCO DE JOGADORAS
# -----------------------------------------------------------------------------
elif menu == "📋 Elenco de Jogadoras":
    st.subheader("🏃‍♀️ Jogadoras Cadastradas")
    if st.session_state.jogadoras:
        df = pd.DataFrame(st.session_state.jogadoras)
        colunas_mostrar = [c for c in ["nome", "nascimento", "tipo", "status"] if c in df.columns]
        st.dataframe(df[colunas_mostrar], use_container_width=True, hide_index=True)
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
        t_conf, t_cad = st.tabs(["⚙️ Configurações Gerais", "➕ Cadastrar Jogadora"])
        
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
                a_tipo = st.selectbox("Categoria", ["Mensalista", "Avulso"])
                a_user = st.text_input("Login")
                a_pass = st.text_input("Senha", type="password")
                a_cont = st.text_input("WhatsApp")

                if st.form_submit_button("➕ Cadastrar Jogadora", use_container_width=True):
                    if a_nome.strip():
                        st.session_state.jogadoras.append({
                            "nome": a_nome.strip(),
                            "nascimento": a_nasc.strip(),
                            "tipo": a_tipo,
                            "login": a_user.strip(),
                            "senha": a_pass.strip(),
                            "contato": a_cont.strip(),
                            "status": "Ativo"
                        })
                        salvar_dados(DATA_FILE, st.session_state.jogadoras)
                        st.success(f"Jogadora {a_nome} cadastrada com sucesso!")
                        st.rerun()

# RODAPÉ
st.markdown("<div class='developer-footer'>Desenvolvido por <b>Vagner Souza / Ciência da Computação</b></div>", unsafe_allow_html=True)
                        
