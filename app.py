import streamlit as st
import pandas as pd
import json
import os
import random

# Configuração da página
st.set_page_config(
    page_title="Peladinha FC - Gestão de Jogos",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilização CSS Personalizada
st.markdown("""
<style>
    .main-title { font-size: 2.3rem; color: #0f172a; font-weight: 800; text-align: center; margin-bottom: 5px; }
    .sub-title { font-size: 1.0rem; color: #475569; text-align: center; margin-bottom: 25px; }
    .card-team { background-color: #f8fafc; border: 2px solid #e2e8f0; border-radius: 12px; padding: 15px; margin-bottom: 15px; }
    .badge-pos { background-color: #2563eb; color: white; padding: 2px 8px; border-radius: 6px; font-size: 0.8rem; }
</style>
""", unsafe_allow_html=True)

DATA_FILE = "jogadoras.json"
PRESENCAS_FILE = "presencas.json"

def carregar_dados(filename, default):
    if os.path.exists(filename):
        try:
            with open(filename, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return default
    return default

def salvar_dados(filename, data):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

if "jogadoras" not in st.session_state:
    st.session_state.jogadoras = carregar_dados(DATA_FILE, [
        {"nome": "Mariana Silva", "posicao": "Atacante", "nivel": 5, "tipo": "Mensalista", "contato": "31999991111", "status": "Ativo"},
        {"nome": "Camila Santos", "posicao": "Goleira", "nivel": 4, "tipo": "Mensalista", "contato": "31999992222", "status": "Ativo"},
        {"nome": "Juliana Costa", "posicao": "Zagueira", "nivel": 3, "tipo": "Avulso", "contato": "31999993333", "status": "Ativo"},
    ])

if "presencas" not in st.session_state:
    st.session_state.presencas = carregar_dados(PRESENCAS_FILE, [])

if "admin_logged" not in st.session_state:
    st.session_state.admin_logged = False

# MENU LATERAL
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/53/53283.png", width=60)
st.sidebar.title("⚽ Peladinha FC")
menu = st.sidebar.radio("Navegação", [
    "📌 Presença no Jogo", 
    "🔀 Sorteio de Times", 
    "📋 Elenco de Jogadoras", 
    "⚙️ Painel Admin"
])

# LOGIN ADMIN
st.sidebar.markdown("---")
st.sidebar.subheader("🔒 Acesso Restrito")
if not st.session_state.admin_logged:
    senha = st.sidebar.text_input("Senha Admin", type="password")
    if st.sidebar.button("Entrar"):
        if senha == "1980":
            st.session_state.admin_logged = True
            st.sidebar.success("Modo Admin Ativo!")
            st.rerun()
        else:
            st.sidebar.error("Senha incorreta")
else:
    st.sidebar.info("🔑 Modo Admin Ativado")
    if st.sidebar.button("Sair do Admin"):
        st.session_state.admin_logged = False
        st.rerun()

# --- PÁGINA 1: CONFIRMAR PRESENÇA ---
if menu == "📌 Presença no Jogo":
    st.markdown("<h1 class='main-title'>⚽ Lista de Confirmadas</h1>", unsafe_allow_html=True)
    st.markdown("<p class='sub-title'>Garanta sua vaga na pelada de hoje!</p>", unsafe_allow_html=True)

    jogadoras_ativas = [j["nome"] for j in st.session_state.jogadoras if j.get("status") == "Ativo"]
    
    col_c1, col_c2 = st.columns([2, 1])

    with col_c1:
        st.subheader("✅ Confirmar Presença")
        if not jogadoras_ativas:
            st.warning("Nenhuma jogadora ativa cadastrada.")
        else:
            jogadora_sel = st.selectbox("Selecione seu nome:", jogadoras_ativas)
            
            c_btn1, c_btn2 = st.columns(2)
            with c_btn1:
                if st.button("👍 Confirmar Minha Presença", use_container_width=True):
                    if jogadora_sel in st.session_state.presencas:
                        st.warning("Você já está confirmada!")
                    else:
                        st.session_state.presencas.append(jogadora_sel)
                        salvar_dados(PRESENCAS_FILE, st.session_state.presencas)
                        st.success(f"{jogadora_sel} confirmada!")
                        st.rerun()
            with c_btn2:
                if st.button("❌ Remover Minha Presença", use_container_width=True):
                    if jogadora_sel in st.session_state.presencas:
                        st.session_state.presencas.remove(jogadora_sel)
                        salvar_dados(PRESENCAS_FILE, st.session_state.presencas)
                        st.info(f"{jogadora_sel} removida da lista.")
                        st.rerun()

        # RECURSO ADMIN: CONFIRMAÇÃO POR TERCEIROS
        if st.session_state.admin_logged:
            st.markdown("---")
            st.subheader("🛠️ Gestão de Presença (Admin)")
            st.caption("Confirme presença para jogadoras que não estão conseguindo mexer no celular.")
            
            jogadora_admin_sel = st.selectbox("Selecionar Jogadora (Admin):", jogadoras_ativas, key="admin_presence")
            ca1, ca2 = st.columns(2)
            with ca1:
                if st.button("➕ Confirmar para Jogadora", use_container_width=True):
                    if jogadora_admin_sel not in st.session_state.presencas:
                        st.session_state.presencas.append(jogadora_admin_sel)
                        salvar_dados(PRESENCAS_FILE, st.session_state.presencas)
                        st.success(f"Presença de {jogadora_admin_sel} adicionada!")
                        st.rerun()
            with ca2:
                if st.button("🗑️ Zerar Lista de Presenças", use_container_width=True):
                    st.session_state.presencas = []
                    salvar_dados(PRESENCAS_FILE, [])
                    st.warning("Lista zerada!")
                    st.rerun()

    with col_c2:
        st.subheader(f"📋 Confirmadas ({len(st.session_state.presencas)})")
        if not st.session_state.presencas:
            st.write("Nenhuma jogadora confirmada ainda.")
        else:
            for idx, nome in enumerate(st.session_state.presencas, 1):
                st.write(f"**{idx}.** {nome}")


# --- PÁGINA 2: SORTEIO DE TIMES ---
elif menu == "🔀 Sorteio de Times":
    st.markdown("<h1 class='main-title'>🔀 Gerador de Times</h1>", unsafe_allow_html=True)
    st.markdown("<p class='sub-title'>Sorteie times equilibrados ou faça o jogo de início com quem já chegou!</p>", unsafe_allow_html=True)

    tab_oficial, tab_atraso = st.tabs(["⭐ Sorteio Oficial (Lista Completa)", "⏱️ Sorteio de Início (Atrasados)"])

    # SORTEIO OFICIAL
    with tab_oficial:
        st.write("Sorteio baseado no nível das jogadoras confirmadas.")
        qtd_times = st.slider("Quantidade de Times:", 2, 4, 2, key="qtd_oficial")
        
        if st.button("🎲 Gerar Times Oficiais", use_container_width=True):
            if len(st.session_state.presencas) < qtd_times:
                st.error("Número insuficiente de jogadoras confirmadas.")
            else:
                jog_dados = [j for j in st.session_state.jogadoras if j["nome"] in st.session_state.presencas]
                jog_dados = sorted(jog_dados, key=lambda x: x.get("nivel", 3), reverse=True)
                
                times = [[] for _ in range(qtd_times)]
                for idx, j in enumerate(jog_dados):
                    times[idx % qtd_times].append(j)
                
                cols = st.columns(qtd_times)
                for i, t in enumerate(times):
                    with cols[i]:
                        st.markdown(f"<div class='card-team'><h3>Time {i+1}</h3>", unsafe_allow_html=True)
                        for item in t:
                            st.write(f"• **{item['nome']}** ({item['posicao']}) - ⭐{item['nivel']}")
                        st.markdown("</div>", unsafe_allow_html=True)

    # SORTEIO PROVISÓRIO PARA QUEM CHEGOU NO HORÁRIO
    with tab_atraso:
        st.info("💡 Use esta opção se o jogo vai começar e algumas jogadoras ainda não chegaram. Selecione apenas quem está **presente na quadra** agora.")
        
        presentes_quadra = st.multiselect("Quem já chegou na quadra?", st.session_state.presencas)
        
        if st.button("⚡ Gerar Time Provisório (Começar Agora)", use_container_width=True):
            if len(presentes_quadra) < 2:
                st.error("Selecione pelo menos 2 jogadoras que já chegaram.")
            else:
                st.success("⚽ Times Provisórios Gerados para o 1º Jogo!")
                random.shuffle(presentes_quadra)
                meio = len(presentes_quadra) // 2
                t1, t2 = presentes_quadra[:meio], presentes_quadra[meio:]
                
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown("<div class='card-team'><h3>🔴 Time Colete</h3>", unsafe_allow_html=True)
                    for p in t1: st.write(f"• {p}")
                    st.markdown("</div>", unsafe_allow_html=True)
                with c2:
                    st.markdown("<div class='card-team'><h3>🔵 Time Sem Colete</h3>", unsafe_allow_html=True)
                    for p in t2: st.write(f"• {p}")
                    st.markdown("</div>", unsafe_allow_html=True)


# --- PÁGINA 3: ELENCO DE JOGADORAS ---
elif menu == "📋 Elenco de Jogadoras":
    st.markdown("<h1 class='main-title'>🏃‍♀️ Elenco Cadastrado</h1>", unsafe_allow_html=True)
    if st.session_state.jogadoras:
        df = pd.DataFrame(st.session_state.jogadoras)
        st.dataframe(df[['nome', 'posicao', 'nivel', 'tipo', 'status']], use_container_width=True, hide_index=True)


# --- PÁGINA 4: PAINEL ADMIN ---
elif menu == "⚙️ Painel Admin":
    st.markdown("<h1 class='main-title'>⚙️ Painel do Administrador</h1>", unsafe_allow_html=True)
    
    if not st.session_state.admin_logged:
        st.error("🔒 Área restrita! Digite a senha no menu lateral.")
    else:
        t_cad, t_ger = st.tabs(["➕ Cadastrar Jogadora", "✏️ Editar / Excluir"])
        
        with t_cad:
            with st.form("cad_form", clear_on_submit=True):
                nome = st.text_input("Nome Completo *")
                pos = st.selectbox("Posição", ["Goleira", "Zagueira", "Lateral", "Meio-Campo", "Atacante"])
                niv = st.slider("Nível (Habilidade)", 1, 5, 3)
                tip = st.selectbox("Categoria", ["Mensalista", "Avulso"])
                tel = st.text_input("WhatsApp / Contato")
                sta = st.selectbox("Status", ["Ativo", "Inativo"])
                
                if st.form_submit_button("💾 Salvar Jogadora"):
                    if nome.strip():
                        st.session_state.jogadoras.append({
                            "nome": nome.strip(), "posicao": pos, "nivel": niv, 
                            "tipo": tip, "contato": tel.strip(), "status": sta
                        })
                        salvar_dados(DATA_FILE, st.session_state.jogadoras)
                        st.success(f"{nome} cadastrada com sucesso!")
                        st.rerun()

        with t_ger:
            if st.session_state.jogadoras:
                nomes = [j["nome"] for j in st.session_state.jogadoras]
                sel_j = st.selectbox("Escolha para editar/excluir:", nomes)
                idx = next(i for i, item in enumerate(st.session_state.jogadoras) if item["nome"] == sel_j)
                
                j_atual = st.session_state.jogadoras[idx]
                
                with st.form("edit_form"):
                    e_nome = st.text_input("Nome", value=j_atual["nome"])
                    e_pos = st.selectbox("Posição", ["Goleira", "Zagueira", "Lateral", "Meio-Campo", "Atacante"], index=["Goleira", "Zagueira", "Lateral", "Meio-Campo", "Atacante"].index(j_atual.get("posicao", "Atacante")))
                    e_niv = st.slider("Nível", 1, 5, value=j_atual.get("nivel", 3))
                    
                    b1, b2 = st.columns(2)
                    if b1.form_submit_button("🔄 Atualizar"):
                        st.session_state.jogadoras[idx]["nome"] = e_nome
                        st.session_state.jogadoras[idx]["posicao"] = e_pos
                        st.session_state.jogadoras[idx]["nivel"] = e_niv
                        salvar_dados(DATA_FILE, st.session_state.jogadoras)
                        st.success("Atualizado!")
                        st.rerun()
                        
                    if b2.form_submit_button("❌ Excluir"):
                        del st.session_state.jogadoras[idx]
                        salvar_dados(DATA_FILE, st.session_state.jogadoras)
                        st.warning("Excluída!")
                        st.rerun()
