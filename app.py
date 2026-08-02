import streamlit as st
import pandas as pd
import random
from datetime import datetime
from utils import carregar_dados, salvar_dados, DATA_FILE, PRESENCAS_FILE, ELENCO_PADRAO

st.set_page_config(page_title="Peladinha FC", page_icon="⚽", layout="wide")

if "jogadoras" not in st.session_state:
    st.session_state.jogadoras = carregar_dados(DATA_FILE, ELENCO_PADRAO)
if "presencas" not in st.session_state:
    st.session_state.presencas = carregar_dados(PRESENCAS_FILE, [])
if "usuario_logado" not in st.session_state:
    st.session_state.usuario_logado = None
if "e_admin" not in st.session_state:
    st.session_state.e_admin = False
if "simular_17h" not in st.session_state:
    st.session_state.simular_17h = False
if "simular_1830" not in st.session_state:
    st.session_state.simular_1830 = False

# HORÁRIOS
agora = datetime.now()
passou_17 = st.session_state.simular_17h or (agora.weekday() == 0 and agora.hour >= 17)
passou_1830 = st.session_state.simular_1830 or (agora.weekday() == 0 and (agora.hour > 18 or (agora.hour == 18 and agora.minute >= 30)))

mensalistas = [p for p in st.session_state.presencas if p.get("tipo", "").lower() == "mensalista"]
avulsas = [p for p in st.session_state.presencas if p.get("tipo", "").lower() in ["avulsa", "diarista"]]

vagas_libres = max(0, 12 - len(mensalistas))
avulsas_com_vaga = avulsas[:vagas_libres] if passou_17 else []
avulsas_na_fila = avulsas[vagas_libres:] if passou_17 else avulsas
jogadoras_jogo = [p["nome"] for p in mensalistas] + [p["nome"] for p in avulsas_com_vaga]

if passou_1830 and len(jogadoras_jogo) >= 4 and "times_sorteados" not in st.session_state:
    embaralhado = jogadoras_jogo.copy()
    random.shuffle(embaralhado)
    meio = len(embaralhado) // 2
    st.session_state.times_sorteados = {"time_a": embaralhado[:meio], "time_b": embaralhado[meio:]}

# MENU LATERAL
with st.sidebar:
    st.title("⚽ Peladinha FC")
    pagina = st.radio("Navegação:", ["📌 Presença no Jogo", "🔀 Sorteio de Times", "📊 Fluxo de Caixa (Admin)", "💸 Pagamento & Pix", "📜 Regulamento", "📋 Elenco", "⚙️ Painel Admin"])
    st.markdown("---")
    
    if st.session_state.usuario_logado:
        st.success(f"👤 Jogadora: **{st.session_state.usuario_logado['nome']}**")
        if st.button("🚪 Sair"):
            st.session_state.usuario_logado = None
            st.rerun()
    elif st.session_state.e_admin:
        st.success("👑 Logado: **ADMINISTRADOR**")
        if st.button("🚪 Sair"):
            st.session_state.e_admin = False
            st.rerun()
    else:
        tab_u, tab_a = st.tabs(["👤 Jogadora", "👑 Admin"])
        with tab_u:
            with st.form("f_u"):
                n = st.selectbox("Nome:", [j["nome"] for j in st.session_state.jogadoras])
                s = st.text_input("Senha:", type="password")
                if st.form_submit_button("Entrar"):
                    u = next((j for j in st.session_state.jogadoras if j["nome"].lower() == n.lower()), None)
                    if u and u.get("senha", "123") == s:
                        st.session_state.usuario_logado = u
                        st.session_state.e_admin = False
                        st.rerun()
                    else: st.error("Senha incorreta!")
        with tab_a:
            with st.form("f_a"):
                sa = st.text_input("Senha Admin:", type="password")
                if st.form_submit_button("Acessar Admin"):
                    if sa == "admin123":
                        st.session_state.e_admin = True
                        st.session_state.usuario_logado = None
                        st.rerun()
                    else: st.error("Senha incorreta!")

# CONTEÚDO PRINCIPAL
if pagina == "📌 Presença no Jogo":
    col1, col2 = st.columns([1.2, 1])
    with col1:
        st.subheader("📋 Status da Lista de Presença")
        st.markdown(f"### ⭐ Vaga Garantida ({len(jogadoras_jogo)}/12)")
        for idx, p in enumerate(mensalistas, start=1):
            st.write(f"**{idx}. {p['nome']}** [Mensalista] ✅")
        for idx, p in enumerate(avulsas_com_vaga, start=len(mensalistas)+1):
            st.write(f"**{idx}. {p['nome']}** [Avulsa Promovida] 🟢")
            
        st.markdown("---")
        st.markdown(f"### ⏳ Fila de Espera ({len(avulsas_na_fila)})")
        for idx, p in enumerate(avulsas_na_fila, start=1):
            st.write(f"**{idx}. {p['nome']}** [Avulsa] 🟡")

    with col2:
        st.subheader("✍️ Ações de Presença")
        with st.container(border=True):
            if not st.session_state.usuario_logado and not st.session_state.e_admin:
                st.warning("🔒 Faça login no menu lateral.")
            elif st.session_state.e_admin:
                st.info("👑 **Modo Admin:** Escolha e confirme qualquer jogadora")
                n_sel = st.selectbox("Jogadora do Elenco:", [j["nome"] for j in st.session_state.jogadoras])
                ca1, ca2 = st.columns(2)
                with ca1:
                    if st.button("👍 Confirmar Selecionada", use_container_width=True):
                        u_obj = next((j for j in st.session_state.jogadoras if j["nome"] == n_sel), None)
                        tp = "Avulsa" if u_obj and u_obj['tipo'].lower() in ["avulsa", "diarista"] else "Mensalista"
                        if n_sel.lower() not in [p["nome"].lower() for p in st.session_state.presencas]:
                            st.session_state.presencas.append({"nome": n_sel, "tipo": tp, "hora": datetime.now().strftime("%H:%M")})
                            salvar_dados(PRESENCAS_FILE, st.session_state.presencas)
                            st.rerun()
                with ca2:
                    if st.button("❌ Remover Selecionada", use_container_width=True):
                        st.session_state.presencas = [p for p in st.session_state.presencas if p["nome"].lower() != n_sel.lower()]
                        salvar_dados(PRESENCAS_FILE, st.session_state.presencas)
                        st.rerun()
            else:
                u = st.session_state.usuario_logado
                st.success(f"Conectado: **{u['nome']}**")
                c1, c2 = st.columns(2)
                with c1:
                    if st.button("👍 Confirmar Minha Presença", use_container_width=True):
                        tp = "Avulsa" if u['tipo'].lower() in ["avulsa", "diarista"] else "Mensalista"
                        if u["nome"].lower() not in [p["nome"].lower() for p in st.session_state.presencas]:
                            st.session_state.presencas.append({"nome": u["nome"], "tipo": tp, "hora": datetime.now().strftime("%H:%M")})
                            salvar_dados(PRESENCAS_FILE, st.session_state.presencas)
                            st.rerun()
                with c2:
                    if st.button("❌ Cancelar Presença", use_container_width=True):
                        st.session_state.presencas = [p for p in st.session_state.presencas if p["nome"].lower() != u["nome"].lower()]
                        salvar_dados(PRESENCAS_FILE, st.session_state.presencas)
                        st.rerun()

elif pagina == "🔀 Sorteio de Times":
    st.subheader("🔀 Sorteio de Times")
    if "times_sorteados" in st.session_state:
        st.success("🎲 **Times Sorteados!**")
        ca, cb = st.columns(2)
        with ca:
            st.markdown("### 🟢 Time A")
            for item in st.session_state.times_sorteados["time_a"]: st.write(f"- {item}")
        with cb:
            st.markdown("### 🔵 Time B")
            for item in st.session_state.times_sorteados["time_b"]: st.write(f"- {item}")
    else: st.info("⏳ Sorteio automático às 18:30 de Segunda-feira.")

elif pagina == "⚙️ Painel Admin":
    if st.session_state.e_admin:
        st.subheader("⚙️ Testes & Painel Admin")
        c_t1, c_t2 = st.columns(2)
        with c_t1: st.session_state.simular_17h = st.checkbox("Simular pós-17:00", value=st.session_state.simular_17h)
        with c_t2: st.session_state.simular_1830 = st.checkbox("Simular pós-18:30", value=st.session_state.simular_1830)
        if st.button("🗑️ Limpar Presenças"):
            st.session_state.presencas = []
            if "times_sorteados" in st.session_state: del st.session_state["times_sorteados"]
            salvar_dados(PRESENCAS_FILE, [])
            st.rerun()
    else: st.error("Acesso restrito.")
