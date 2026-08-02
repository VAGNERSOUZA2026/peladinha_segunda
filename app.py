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
# AUTOMAÇÃO DE HORÁRIOS (SEGUNDA-FEIRA)
# -----------------------------------------------------------------------------
agora = datetime.now()
dia_da_semana = agora.weekday()  # 0 = Segunda-feira
hora_minuto = agora.time()

# 1. Liberação de vagas das Avulsas (Segunda pós 17:00 ou outros dias)
passou_das_17_segunda = (dia_da_semana == 0 and hora_minuto.hour >= 17) or (dia_da_semana > 0)

# 2. Sorteio Automático (Segunda pós 18:30 ou outros dias)
passou_das_1830_segunda = (dia_da_semana == 0 and (hora_minuto.hour > 18 or (hora_minuto.hour == 18 and hora_minuto.minute >= 30))) or (dia_da_semana > 0)

# Lógica de separação dos nomes para o sorteio
mensalistas_confirmadas = [p for p in st.session_state.presencas if p.get("tipo", "").lower() == "mensalista"]
avulsas_confirmadas = [p for p in st.session_state.presencas if p.get("tipo", "").lower() in ["avulsa", "diarista"]]

LIMITE_TOTAL = 12
vagas_restantes = max(0, LIMITE_TOTAL - len(mensalistas_confirmadas))

if passou_das_17_segunda:
    avulsas_com_vaga = avulsas_confirmadas[:vagas_restantes]
    avulsas_na_fila = avulsas_confirmadas[vagas_restantes:]
else:
    avulsas_com_vaga = []
    avulsas_na_fila = avulsas_confirmadas

# Lista final das jogadoras com vaga garantida no jogo
jogadoras_confirmadas_jogo = [p["nome"] for p in mensalistas_confirmadas] + [p["nome"] for p in avulsas_com_vaga]

# Execução automática do sorteio às 18:30
if passou_das_1830_segunda and len(jogadoras_confirmadas_jogo) >= 4:
    if "times_sorteados" not in st.session_state:
        random.seed(agora.strftime("%Y%m%d"))  # Garante sorteio consistente no dia
        embaralhado = jogadoras_confirmadas_jogo.copy()
        random.shuffle(embaralhado)
        meio = len(embaralhado) // 2
        st.session_state.times_sorteados = {
            "time_a": embaralhado[:meio],
            "time_b": embaralhado[meio:]
        }

# -----------------------------------------------------------------------------
# BARRA LATERAL (MENU + LOGIN)
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
# PÁGINA 1: PRESENÇA NO JOGO
# -----------------------------------------------------------------------------
if pagina == "📌 Presença no Jogo":
    col_esquerda, col_direita = st.columns([1.2, 1])

    with col_esquerda:
        st.subheader("📋 Lista de Presença")
        
        # Alertas de Status das Horas
        if passou_das_1830_segunda:
            st.success("🎲 **Sorteio Realizado Automaticamente às 18:30!** Confira na aba Sorteio de Times.")
        elif passou_das_17_segunda:
            st.info("🟢 **Vagas de Avulsas Liberadas!** (Aguardando 18:30 para o sorteio automático).")
        else:
            st.warning("⏳ **Aguardando 17:00** para subir Avulsas e **18:30** para o Sorteio Automático.")

        # 1. MENSALISTAS
        st.markdown(f"### ⭐ Mensalistas ({len(mensalistas_confirmadas)}/12)")
        if mensalistas_confirmadas:
            for idx, p in enumerate(mensalistas_confirmadas, start=1):
                st.write(f"**{idx}. {p['nome']}** — *(às {p.get('hora', '')})* ✅")
        else:
            st.caption("Nenhuma mensalista confirmada.")

        st.markdown("---")

        # 2. AVULSAS CONFIRMADAS NA LISTA PRINCIPAL
        st.markdown(f"### ⚽ Jogadoras Avulsas Confirmadas ({len(avulsas_com_vaga)}/{vagas_restantes} vagas)")
        if avulsas_com_vaga:
            for idx, p in enumerate(avulsas_com_vaga, start=1):
                st.write(f"**{idx}. {p['nome']}** [Avulsa] — *(às {p.get('hora', '')})* 🟢")
        else:
            st.caption("Nenhuma avulsa na lista principal. Avulsas sobem automaticamente às 17:00.")

        st.markdown("---")

        # 3. FILA DE ESPERA
        st.markdown(f"### ⏳ Fila de Espera ({len(avulsas_na_fila)})")
        if avulsas_na_fila:
            for idx, p in enumerate(avulsas_na_fila, start=1):
                st.write(f"**{idx}. {p['nome']}** [Avulsa] — *(às {p.get('hora', '')})* 🟡")
        else:
            st.caption("Nenhuma jogadora na fila de espera.")

    # --- LADO DIREITO: CONFIRMAÇÃO ---
    with col_direita:
        st.subheader("✍️ Minha Presença")
        
        with st.container(border=True):
            if not st.session_state.usuario_logado:
                st.warning("⚠️ **Acesso Negado!**")
                st.write("Faça login no menu lateral para confirmar ou cancelar sua presença.")
            else:
                user_atual = st.session_state.usuario_logado
                tipo_exibicao = "Avulsa" if user_atual['tipo'].lower() in ["avulsa", "diarista"] else "Mensalista"
                
                st.success(f"Conectada como: **{user_atual['nome']}** ({tipo_exibicao})")

                col_b1, col_b2 = st.columns(2)
                
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
                            
                            # Limpa sorteio antigo se alguém entrar
                            if "times_sorteados" in st.session_state:
                                del st.session_state["times_sorteados"]
                                
                            st.success("Presença gravada com sucesso!")
                            st.rerun()

                with col_b2:
                    if st.button("❌ Cancelar Presença", use_container_width=True):
                        nome_alvo = user_atual["nome"].strip().lower()
                        nova_lista = [p for p in st.session_state.presencas if p["nome"].strip().lower() != nome_alvo]
                        
                        if len(nova_lista) < len(st.session_state.presencas):
                            st.session_state.presencas = nova_lista
                            salvar_dados(PRESENCAS_FILE, st.session_state.presencas)
                            if "times_sorteados" in st.session_state:
                                del st.session_state["times_sorteados"]
                            st.info("Presença removida com sucesso.")
                            st.rerun()
                        else:
                            st.warning("Seu nome não estava registrado.")

# -----------------------------------------------------------------------------
# PÁGINA 2: SORTEIO DE TIMES AUTOMÁTICO
# -----------------------------------------------------------------------------
elif pagina == "🔀 Sorteio de Times":
    st.subheader("🔀 Sorteio de Times (Automático às 18:30)")
    
    if "times_sorteados" in st.session_state:
        st.success("🎲 **Times Sorteados Automaticamente!**")
        ca, cb = st.columns(2)
        with ca:
            st.markdown("### 🟢 Time A")
            for item in st.session_state.times_sorteados["time_a"]:
                st.write(f"- **{item}**")
        with cb:
            st.markdown("### 🔵 Time B")
            for item in st.session_state.times_sorteados["time_b"]:
                st.write(f"- **{item}**")
    else:
        if passou_das_1830_segunda:
            st.warning("Aguardando pelo menos 4 jogadoras confirmadas para sortear.")
        else:
            st.info("⏳ O sorteio automático dos times acontecerá hoje exatamente às **18:30**.")

        # Opção manual para o Admin se precisar adiantar
        if st.button("🎲 Forçar Sorteio Manual Agora"):
            if len(jogadoras_confirmadas_jogo) >= 4:
                embaralhado = jogadoras_confirmadas_jogo.copy()
                random.shuffle(embaralhado)
                meio = len(embaralhado) // 2
                st.session_state.times_sorteados = {
                    "time_a": embaralhado[:meio],
                    "time_b": embaralhado[meio:]
                }
                st.rerun()
            else:
                st.error("Necessário pelo menos 4 jogadoras com vaga para sortear.")

# -----------------------------------------------------------------------------
# DEMAIS PÁGINAS
# -----------------------------------------------------------------------------
elif pagina == "📊 Fluxo de Caixa (Admin)":
    st.subheader("📊 Fluxo de Caixa")
    st.info("Módulo financeiro do grupo.")

elif pagina == "💸 Pagamento & Pix":
    st.subheader("💸 Pagamento & Pix")
    st.write("**Titular:** Vagner Ferreira de Souza")
    st.write("**Chave Pix:** 31989684010")

elif pagina == "📜 Regulamento":
    st.subheader("📜 Regulamento Interno")
    st.write("1. Prioridade para Mensalistas até Segunda-Feira às 17:00.")
    st.write("2. Às **17:00**, as Avulsas sobem automaticamente da Fila de Espera para as vagas restantes.")
    st.write("3. Às **18:30**, o sistema realiza o **Sorteio Automático dos Times** entre todas as jogadoras confirmadas.")

elif pagina == "📋 Elenco de Jogadoras":
    st.subheader("📋 Elenco Registrado")
    df_elenco = pd.DataFrame(st.session_state.jogadoras)[["nome", "tipo"]]
    st.dataframe(df_elenco, use_container_width=True)

elif pagina == "⚙️ Painel Admin":
    st.subheader("⚙️ Painel Admin")
    st.write("### 🚨 Gerenciamento")
    if st.button("Zerar / Limpar Lista e Refazer Sorteio"):
        st.session_state.presencas = []
        if "times_sorteados" in st.session_state:
            del st.session_state["times_sorteados"]
        salvar_dados(PRESENCAS_FILE, [])
        st.success("Lista de presença e sorteio zerados!")
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
