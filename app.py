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

# Elenco padronizado com termo "Avulsa"
ELENCO_PADRAO = [
    {"nome": "Carol", "tipo": "Mensalista", "senha": "123"},
    {"nome": "Debora", "tipo": "Mensalista", "senha": "123"},
    {"nome": "Barbara", "tipo": "Mensalista", "senha": "123"},
    {"nome": "Michele", "tipo": "Mensalista", "senha": "123"},
    {"nome": "Duda", "tipo": "Mensalista", "senha": "123"},
    {"nome": "Luzinete", "tipo": "Mensalista", "senha": "123"},
    {"nome": "Cicera", "tipo": "Mensalista", "senha": "123"},
    {"nome": "Dani", "tipo": "Mensalista", "senha": "123"},
    {"nome": "Luciana", "tipo": "Mensalista", "senha": "123"},
    {"nome": "Amanda", "tipo": "Avulsa", "senha": "123"},
    {"nome": "kelly", "tipo": "Avulsa", "senha": "123"}
]

if "jogadoras" not in st.session_state:
    st.session_state.jogadoras = carregar_dados(DATA_FILE, ELENCO_PADRAO)

if "presencas" not in st.session_state:
    st.session_state.presencas = carregar_dados(PRESENCAS_FILE, [])

if "usuario_logado" not in st.session_state:
    st.session_state.usuario_logado = None

# -----------------------------------------------------------------------------
# BARRA LATERAL (MENU + LOGIN OBRIGATÓRIO)
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
    st.header("👤 Login Obrigatório")
    
    if st.session_state.usuario_logado:
        st.success(f"Conectada: **{st.session_state.usuario_logado['nome']}**")
        st.caption(f"Tipo: {st.session_state.usuario_logado['tipo']}")
        if st.button("🚪 Sair / Trocar Conta"):
            st.session_state.usuario_logado = None
            st.rerun()
    else:
        st.warning("🔒 Nenhuma jogadora logada")
        with st.form("form_login"):
            nomes_cadastrados = [j["nome"] for j in st.session_state.jogadoras]
            nome_login = st.selectbox("Selecione seu Nome:", nomes_cadastrados)
            senha_login = st.text_input("Senha", type="password")
            if st.form_submit_button("Entrar"):
                user = next((j for j in st.session_state.jogadoras if j["nome"].lower() == nome_login.lower()), None)
                if user and user.get("senha", "123") == senha_login:
                    st.session_state.usuario_logado = user
                    st.success("Login realizado com sucesso!")
                    st.rerun()
                else:
                    st.error("Senha incorreta!")

# -----------------------------------------------------------------------------
# PÁGINA 1: PRESENÇA NO JOGO (TERMO "AVULSA" CORRIGIDO)
# -----------------------------------------------------------------------------
if pagina == "📌 Presença no Jogo":
    col_esquerda, col_direita = st.columns([1.2, 1])

    # --- LADO ESQUERDO: LISTA DE PRESENÇA ---
    with col_esquerda:
        st.subheader("📋 Lista de Presença")
        
        # Normalização para reconhecer tanto 'Avulsa' quanto antigos 'Diarista'
        mensalistas_confirmadas = [
            p for p in st.session_state.presencas 
            if p.get("tipo", "").lower() == "mensalista"
        ]
        
        avulsas_confirmadas = [
            p for p in st.session_state.presencas 
            if p.get("tipo", "").lower() in ["avulsa", "diarista"]
        ]

        # 1. EXIBIÇÃO MENSALISTAS
        st.markdown(f"### ⭐ Mensalistas ({len(mensalistas_confirmadas)})")
        if mensalistas_confirmadas:
            for idx, p in enumerate(mensalistas_confirmadas, start=1):
                st.write(f"**{idx}. {p['nome']}** — *(às {p.get('hora', '')})* ✅")
        else:
            st.info("Nenhuma mensalista confirmada ainda.")

        st.markdown("---")

        # 2. EXIBIÇÃO AVULSAS (Com limite e Fila de Espera explicita)
        LIMITE_TOTAL = 12
        vagas_restantes = max(0, LIMITE_TOTAL - len(mensalistas_confirmadas))
        
        avulsas_com_vaga = avulsas_confirmadas[:vagas_restantes]
        avulsas_fila = avulsas_confirmadas[vagas_restantes:]

        st.markdown(f"### ⚽ Jogadoras Avulsas ({len(avulsas_com_vaga)}/{vagas_restantes} vagas)")
        if avulsas_com_vaga:
            for idx, p in enumerate(avulsas_com_vaga, start=1):
                st.write(f"**{idx}. {p['nome']}** [Avulsa] — *(às {p.get('hora', '')})* 🟢")
        else:
            st.caption("Nenhuma jogadora avulsa nas vagas principais.")

        # FILA DE ESPERA (Aparece obrigatoriamente se houver excedente)
        st.markdown("---")
        st.markdown(f"### ⏳ Fila de Espera ({len(avulsas_fila)})")
        if avulsas_fila:
            for idx, p in enumerate(avulsas_fila, start=1):
                st.write(f"**{idx}. {p['nome']}** [Avulsa] — *(às {p.get('hora', '')})* 🟡")
        else:
            st.caption("Nenhuma jogadora na fila de espera.")

    # --- LADO DIREITO: MINHA PRESENÇA ---
    with col_direita:
        st.subheader("✍️ Minha Presença")
        
        with st.container(border=True):
            if not st.session_state.usuario_logado:
                st.warning("⚠️ **Acesso Negado!**")
                st.write("Faça o login no menu lateral para confirmar ou cancelar sua presença.")
            else:
                user_atual = st.session_state.usuario_logado
                # Garantia de exibição do tipo "Avulsa"
                tipo_exibicao = "Avulsa" if user_atual['tipo'].lower() in ["avulsa", "diarista"] else "Mensalista"
                
                st.success(f"Conectada como: **{user_atual['nome']}** ({tipo_exibicao})")

                col_b1, col_b2 = st.columns(2)
                
                # --- CONFIRMAR ---
                with col_b1:
                    if st.button("👍 Confirmar Presença", use_container_width=True):
                        nomes_na_lista = [p["nome"].strip().lower() for p in st.session_state.presencas]
                        
                        if user_atual["nome"].strip().lower() in nomes_na_lista:
                            st.warning("Seu nome já está na lista!")
                        else:
                            nova_presenca = {
                                "nome": user_atual["nome"],
                                "tipo": tipo_exibicao,
                                "hora": datetime.now().strftime("%H:%M")
                            }
                            st.session_state.presencas.append(nova_presenca)
                            salvar_dados(PRESENCAS_FILE, st.session_state.presencas)
                            st.success("Presença confirmada!")
                            st.rerun()

                # --- CANCELAR ---
                with col_b2:
                    if st.button("❌ Cancelar Presença", use_container_width=True):
                        nome_alvo = user_atual["nome"].strip().lower()
                        nova_lista = [p for p in st.session_state.presencas if p["nome"].strip().lower() != nome_alvo]
                        
                        if len(nova_lista) < len(st.session_state.presencas):
                            st.session_state.presencas = nova_lista
                            salvar_dados(PRESENCAS_FILE, st.session_state.presencas)
                            st.info("Presença removida.")
                            st.rerun()
                        else:
                            st.warning("Seu nome não estava na lista.")

# -----------------------------------------------------------------------------
# DEMAIS PÁGINAS DO MENU
# -----------------------------------------------------------------------------
elif pagina == "🔀 Sorteio de Times":
    st.subheader("🔀 Sorteio de Times")
    if len(st.session_state.presencas) < 4:
        st.warning("Necessário pelo menos 4 jogadoras confirmadas.")
    else:
        if st.button("🎲 Sortear Times Automático"):
            import random
            lista_nomes = [p["nome"] for p in st.session_state.presencas]
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
    st.info("Módulo financeiro do grupo.")

elif pagina == "💸 Pagamento & Pix":
    st.subheader("💸 Pagamento & Pix")
    st.write("**Titular:** Vagner Ferreira de Souza")
    st.write("**Chave Pix:** 31989684010")

elif pagina == "📜 Regulamento":
    st.subheader("📜 Regulamento Interno")
    st.write("1. Prioridade para Mensalistas até 17h de Segunda-Feira.")
    st.write("2. Vagas remanescentes abertas para Avulsas por ordem de confirmação.")

elif pagina == "📋 Elenco de Jogadoras":
    st.subheader("📋 Elenco Registrado")
    # Atualiza visualização no elenco
    df_elenco = pd.DataFrame(st.session_state.jogadoras)[["nome", "tipo"]]
    df_elenco['tipo'] = df_elenco['tipo'].replace({"Diarista": "Avulsa"})
    st.dataframe(df_elenco, use_container_width=True)

elif pagina == "⚙️ Painel Admin":
    st.subheader("⚙️ Painel Admin")
    if st.button("🚨 Zerar / Limpar Toda a Lista de Presença"):
        st.session_state.presencas = []
        salvar_dados(PRESENCAS_FILE, [])
        st.success("Lista de presença zerada com sucesso!")
        st.rerun()

# -----------------------------------------------------------------------------
# RODAPÉ
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
