import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime

# -----------------------------------------------------------------------------
# CONFIGURAÇÃO DA PÁGINA
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Peladinha FC | Gestão de Futebol",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------------------------------------------------------
# PERSISTÊNCIA DE DADOS (JSON)
# -----------------------------------------------------------------------------
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
    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    except Exception:
        pass

# Lista Padrão de Elenco
ELENCO_PADRAO = [
    {"nome": "Carol", "tipo": "Mensalista"},
    {"nome": "Debora", "tipo": "Mensalista"},
    {"nome": "Barbara", "tipo": "Mensalista"},
    {"nome": "Michele", "tipo": "Mensalista"},
    {"nome": "Duda", "tipo": "Mensalista"},
    {"nome": "Luzinete", "tipo": "Mensalista"},
    {"nome": "Cicera", "tipo": "Mensalista"},
    {"nome": "Dani", "tipo": "Mensalista"},
    {"nome": "Luciana", "tipo": "Mensalista"},
    {"nome": "Amanda", "tipo": "Diarista"},
    {"nome": "kelly", "tipo": "Diarista"}
]

if "jogadoras" not in st.session_state:
    st.session_state.jogadoras = carregar_dados(DATA_FILE, ELENCO_PADRAO)

if "presencas" not in st.session_state:
    st.session_state.presencas = carregar_dados(PRESENCAS_FILE, [])

if "usuario_logado" not in st.session_state:
    st.session_state.usuario_logado = None

# -----------------------------------------------------------------------------
# BARRA LATERAL (MENU ORIGINAL)
# -----------------------------------------------------------------------------
with st.sidebar:
    st.write("Ir para:")
    pagina = st.radio(
        "",
        [
            "📌 Presença no Jogo",
            "🔀 Sorteio de Times",
            "📊 Fluxo de Caixa (Admin)",
            "💸 Pagamento & Pix",
            "📜 Regulamento",
            "📋 Elenco de Jogadoras",
            "⚙️ Painel Admin"
        ],
        label_visibility="collapsed"
    )

    st.markdown("---")
    st.header("👤 Área da Jogadora")
    
    tab_login, tab_cadastro = st.tabs(["Entrar", "Cadastrar"])
    
    with tab_login:
        login_input = st.text_input("Login")
        senha_input = st.text_input("Senha", type="password")
        if st.button("Entrar no Sistema"):
            # Lógica simples de login para a sessão
            if login_input:
                st.session_state.usuario_logado = login_input
                st.success(f"Conectado como {login_input}")

# -----------------------------------------------------------------------------
# PÁGINA 1: PRESENÇA NO JOGO
# -----------------------------------------------------------------------------
if pagina == "📌 Presença no Jogo":
    col_esquerda, col_direita = st.columns([1.2, 1])

    # --- LADO ESQUERDO: LISTA DE PRESENÇA ---
    with col_esquerda:
        st.subheader("🛍️ Lista de Presença")
        
        LIMITE_VAGAS = 12
        confirmadas = st.session_state.presencas[:LIMITE_VAGAS]
        espera = st.session_state.presencas[LIMITE_VAGAS:]

        st.markdown(f"### 📋 Confirmadas ({len(confirmadas)}/{LIMITE_VAGAS})")
        
        if confirmadas:
            for idx, p in enumerate(confirmadas, start=1):
                nome = p.get("nome", p) if isinstance(p, dict) else p
                tipo = p.get("tipo", "Jogadora") if isinstance(p, dict) else "Jogadora"
                hora = p.get("hora", "") if isinstance(p, dict) else ""
                
                info_hora = f" — *(às {hora})*" if hora else ""
                st.write(f"**{idx}. {nome}** `[{tipo}]`{info_hora}")
        else:
            st.info("Nenhuma jogadora confirmada até o momento.")

        st.markdown("---")
        st.markdown(f"### ⏳ Fila de Espera ({len(espera)})")
        if espera:
            for idx, p in enumerate(espera, start=1):
                nome = p.get("nome", p) if isinstance(p, dict) else p
                st.write(f"**{idx}. {nome}**")
        else:
            st.caption("Nenhuma jogadora na fila de espera.")

    # --- LADO DIREITO: MINHA PRESENÇA ---
    with col_direita:
        st.subheader("✍️ Minha Presença")
        
        with st.container(border=True):
            lista_nomes = [j["nome"] for j in st.session_state.jogadoras]
            jogadora_sel = st.selectbox("Selecione a jogadora:", lista_nomes)

            col_b1, col_b2 = st.columns(2)
            
            # --- BOTÃO: CONFIRMAR PRESENÇA ---
            with col_b1:
                if st.button("👍 Confirmar Presença", use_container_width=True):
                    # Padroniza busca para ignorar maiúsculas/minúsculas e espaços extras
                    nomes_ja_confirmados = [
                        (p["nome"].strip().lower() if isinstance(p, dict) else str(p).strip().lower()) 
                        for p in st.session_state.presencas
                    ]
                    
                    nome_alvo_clean = jogadora_sel.strip().lower()

                    if nome_alvo_clean in nomes_ja_confirmados:
                        st.warning("Seu nome já está na lista!")
                    else:
                        # Identifica o tipo (Mensalista ou Diarista)
                        info_obj = next((j for j in st.session_state.jogadoras if j["nome"].strip().lower() == nome_alvo_clean), {"tipo": "Diarista"})
                        
                        nova_presenca = {
                            "nome": jogadora_sel,
                            "tipo": info_obj.get("tipo", "Diarista"),
                            "hora": datetime.now().strftime("%H:%M")
                        }
                        
                        st.session_state.presencas.append(nova_presenca)
                        salvar_dados(PRESENCAS_FILE, st.session_state.presencas)
                        st.success(f"{jogadora_sel} confirmada com sucesso!")
                        st.rerun()

            # --- BOTÃO: CANCELAR PRESENÇA ---
            with col_b2:
                if st.button("❌ Cancelar Presença", use_container_width=True):
                    nome_alvo_clean = jogadora_sel.strip().lower()
                    
                    nova_lista = []
                    removido = False
                    for p in st.session_state.presencas:
                        nome_p = p["nome"] if isinstance(p, dict) else str(p)
                        if nome_p.strip().lower() == nome_alvo_clean:
                            removido = True
                        else:
                            nova_lista.append(p)
                    
                    if removido:
                        st.session_state.presencas = nova_lista
                        salvar_dados(PRESENCAS_FILE, st.session_state.presencas)
                        st.info(f"Presença de {jogadora_sel} removida.")
                        st.rerun()
                    else:
                        st.warning("Esta jogadora não está na lista de presença.")

# -----------------------------------------------------------------------------
# DEMAIS PÁGINAS DO MENU
# -----------------------------------------------------------------------------
elif pagina == "🔀 Sorteio de Times":
    st.subheader("🔀 Sorteio de Times")
    if len(st.session_state.presencas) < 4:
        st.warning("Necessário pelo menos 4 jogadoras confirmadas.")
    else:
        if st.button("🎲 Sorteia Times Automático"):
            import random
            lista_nomes = [p["nome"] if isinstance(p, dict) else p for p in st.session_state.presencas]
            random.shuffle(lista_nomes)
            meio = len(lista_nomes) // 2
            st.session_state.t_a = lista_nomes[:meio]
            st.session_state.t_b = lista_nomes[meio:]

        if "t_a" in st.session_state:
            ca, cb = st.columns(2)
            with ca:
                st.markdown("### 🟢 Time A")
                for item in st.session_state.t_a: st.write(f"- {item}")
            with cb:
                st.markdown("### 🔵 Time B")
                for item in st.session_state.t_b: st.write(f"- {item}")

elif pagina == "📊 Fluxo de Caixa (Admin)":
    st.subheader("📊 Fluxo de Caixa")
    st.info("Módulo financeiro de entradas e saídas do grupo.")

elif pagina == "💸 Pagamento & Pix":
    st.subheader("💸 Pagamento & Pix")
    st.write("**Titular:** Vagner Ferreira de Souza")
    st.write("**Chave Pix:** 31989684010")

elif pagina == "📜 Regulamento":
    st.subheader("📜 Regulamento Interno")
    st.write("1. Prioridade para Mensalistas até 17h de Segunda-Feira.")
    st.write("2. Tolerância de 15 minutos.")

elif pagina == "📋 Elenco de Jogadoras":
    st.subheader("📋 Elenco Registrado")
    st.dataframe(pd.DataFrame(st.session_state.jogadoras), use_container_width=True)

elif pagina == "⚙️ Painel Admin":
    st.subheader("⚙️ Painel Admin")
    if st.button("🚨 Zerar / Limpar Lista de Presença"):
        st.session_state.presencas = []
        salvar_dados(PRESENCAS_FILE, [])
        st.success("Lista de presença limpa!")
        st.rerun()

# -----------------------------------------------------------------------------
# RODAPÉ ORIGINAL
# -----------------------------------------------------------------------------
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown(
    """
    <div style="background-color: #0F172A; padding: 12px; border-radius: 8px; text-align: center; color: white; font-weight: bold;">
        Desenvolvido por Vagner Souza / Ciência da Computação
    </div>
    """,
    unsafe_allow_html=True
)
