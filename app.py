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

if "e_admin" not in st.session_state:
    st.session_state.e_admin = False

if "simular_liberacao_17h" not in st.session_state:
    st.session_state.simular_liberacao_17h = False

if "simular_sorteio_1830" not in st.session_state:
    st.session_state.simular_sorteio_1830 = False

# -----------------------------------------------------------------------------
# LÓGICA DE HORÁRIOS E REGRAS
# -----------------------------------------------------------------------------
agora = datetime.now()
dia_da_semana = agora.weekday()  # 0 = Segunda-feira
hora_minuto = agora.time()

real_passou_17 = (dia_da_semana == 0 and hora_minuto.hour >= 17)
real_passou_1830 = (dia_da_semana == 0 and (hora_minuto.hour > 18 or (hora_minuto.hour == 18 and hora_minuto.minute >= 30)))

passou_das_17_segunda = st.session_state.simular_liberacao_17h or real_passou_17
passou_das_1830_segunda = st.session_state.simular_sorteio_1830 or real_passou_1830

# SEPARAÇÃO DE JOGADORAS
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

jogadoras_confirmadas_jogo = [p["nome"] for p in mensalistas_confirmadas] + [p["nome"] for p in avulsas_com_vaga]

if passou_das_1830_segunda and len(jogadoras_confirmadas_jogo) >= 4:
    if "times_sorteados" not in st.session_state:
        random.seed(agora.strftime("%Y%m%d"))
        embaralhado = jogadoras_confirmadas_jogo.copy()
        random.shuffle(embaralhado)
        meio = len(embaralhado) // 2
        st.session_state.times_sorteados = {
            "time_a": embaralhado[:meio],
            "time_b": embaralhado[meio:]
        }

# -----------------------------------------------------------------------------
# BARRA LATERAL - MENU & LOGIN FIXO
# -----------------------------------------------------------------------------
with st.sidebar:
    st.title("⚽ Peladinha FC")
    
    pagina = st.radio(
        "Navegação do App:",
        [
            "📌 Presença no Jogo",
            "🔀 Sorteio de Times",
            "📊 Fluxo de Caixa (Admin)",
            "💸 Pagamento & Pix",
            "📜 Regulamento",
            "📋 Elenco de Jogadoras",
            "⚙️ Painel Admin"
        ]
    )

    st.markdown("---")
    st.subheader("🔑 ÁREA DE LOGIN")

    if st.session_state.usuario_logado:
        st.success(f"👤 Jogadora: **{st.session_state.usuario_logado['nome']}**")
        if st.button("🚪 Sair do Perfil"):
            st.session_state.usuario_logado = None
            st.rerun()

    elif st.session_state.e_admin:
        st.success("👑 Logado como: **ADMINISTRADOR**")
        if st.button("🚪 Sair do Modo Admin"):
            st.session_state.e_admin = False
            st.rerun()

    else:
        tab_user, tab_admin = st.tabs(["👤 Sou Jogadora", "👑 Sou Admin"])

        with tab_user:
            with st.form("form_login_user"):
                nomes_cadastrados = [j["nome"] for j in st.session_state.jogadoras]
                nome_sel = st.selectbox("Selecione seu Nome:", nomes_cadastrados)
                senha_sel = st.text_input("Senha:", type="password", key="pass_user")
                if st.form_submit_button("Entrar como Jogadora"):
                    user = next((j for j in st.session_state.jogadoras if j["nome"].lower() == nome_sel.lower()), None)
                    if user and user.get("senha", "123") == senha_sel:
                        st.session_state.usuario_logado = user
                        st.session_state.e_admin = False
                        st.rerun()
                    else:
                        st.error("Senha incorreta!")

        with tab_admin:
            with st.form("form_login_admin"):
                pass_admin = st.text_input("Senha do Administrador:", type="password", key="pass_adm")
                if st.form_submit_button("Entrar como Admin"):
                    if pass_admin == "admin123":
                        st.session_state.e_admin = True
                        st.session_state.usuario_logado = None
                        st.rerun()
                    else:
                        st.error("Senha incorreta! (Padrão: admin123)")

# -----------------------------------------------------------------------------
# PÁGINA 1: PRESENÇA NO JOGO
# -----------------------------------------------------------------------------
if pagina == "📌 Presença no Jogo":
    col_esq, col_dir = st.columns([1.2, 1])

    with col_esq:
        st.subheader("📋 Status da Lista de Presença")
        
        if passou_das_1830_segunda:
            st.success("🎲 **Sorteio das 18:30 REALIZADO!** Acesse a aba 'Sorteio de Times'.")
        elif passou_das_17_segunda:
            st.info("🟢 **Vagas de Avulsas Liberadas (17:00)!**")
        else:
            st.warning("⏳ **Aguardando Segunda-feira 17:00:** Avulsas na Fila de Espera.")

        st.markdown(f"### ⭐ Lista Principal com Vaga Garantida ({len(jogadoras_confirmadas_jogo)}/12)")
        
        # MENSALISTAS
        if mensalistas_confirmadas:
            for idx, p in enumerate(mensalistas_confirmadas, start=1):
                st.write(f"**{idx}. {p['nome']}** [Mensalista] — *(às {p.get('hora', '')})* ✅")
        
        # AVULSAS PROMOVIDAS
        if avulsas_com_vaga:
            offset = len(mensalistas_confirmadas) + 1
            for idx, p in enumerate(avulsas_com_vaga, start=offset):
                st.write(f"**{idx}. {p['nome']}** [⚽ Avulsa Promovida] — *(às {p.get('hora', '')})* 🟢")

        if not jogadoras_confirmadas_jogo:
            st.caption("Nenhuma jogadora confirmada na lista principal ainda.")

        st.markdown("---")

        st.markdown(f"### ⏳ Fila de Espera ({len(avulsas_na_fila)})")
        if avulsas_na_fila:
            for idx, p in enumerate(avulsas_na_fila, start=1):
                st.write(f"**{idx}. {p['nome']}** [Avulsa] — *(às {p.get('hora', '')})* 🟡")
        else:
            st.caption("Fila de espera vazia.")

    with col_dir:
        st.subheader("✍️ Marcar / Cancelar Presença")
        with st.container(border=True):
            if not st.session_state.usuario_logado and not st.session_state.e_admin:
                st.warning("🔒 **Acesso Negado!** Faça login no menu lateral para acessar.")
            
            # -----------------------------------------------------------------
            # PAINEL EXCLUSIVO DO ADMIN (AUTONOMIA TOTAL)
            # -----------------------------------------------------------------
            elif st.session_state.e_admin:
                st.info("👑 **Modo Administrador:** Gestão Direta de Presenças")
                
                # Lista de jogadoras cadastradas no elenco
                nomes_elenco = [j["nome"] for j in st.session_state.jogadoras]
                
                st.markdown("#### 1. Selecionar do Elenco Cadastrado")
                nome_admin_sel = st.selectbox("Escolha a jogadora:", nomes_elenco, key="select_admin_jogadora")
                
                col_adm1, col_adm2 = st.columns(2)
                
                with col_adm1:
                    if st.button("👍 Confirmar Selecionada", use_container_width=True):
                        user_obj = next((j for j in st.session_state.jogadoras if j["nome"] == nome_admin_sel), None)
                        tipo_e = "Avulsa" if user_obj and user_obj['tipo'].lower() in ["avulsa", "diarista"] else "Mensalista"
                        
                        nomes_atuais = [p["nome"].strip().lower() for p in st.session_state.presencas]
                        if nome_admin_sel.strip().lower() in nomes_atuais:
                            st.warning(f"**{nome_admin_sel}** já está na lista!")
                        else:
                            st.session_state.presencas.append({
                                "nome": nome_admin_sel,
                                "tipo": tipo_e,
                                "hora": datetime.now().strftime("%H:%M")
                            })
                            salvar_dados(PRESENCAS_FILE, st.session_state.presencas)
                            if "times_sorteados" in st.session_state:
                                del st.session_state["times_sorteados"]
                            st.success(f"✅ {nome_admin_sel} confirmada com sucesso!")
                            st.rerun()

                with col_adm2:
                    if st.button("❌ Remover Selecionada", use_container_width=True):
                        st.session_state.presencas = [
                            p for p in st.session_state.presencas 
                            if p["nome"].strip().lower() != nome_admin_sel.strip().lower()
                        ]
                        salvar_dados(PRESENCAS_FILE, st.session_state.presencas)
                        if "times_sorteados" in st.session_state:
                            del st.session_state["times_sorteados"]
                        st.info(f"🗑️ {nome_admin_sel} removida da lista.")
                        st.rerun()

                st.markdown("---")
                
                st.markdown("#### 2. Confirmar Convidada Extra (Fora do Elenco)")
                nome_extra = st.text_input("Nome da Convidada:", key="input_nome_extra")
                tipo_extra = st.radio("Tipo:", ["Avulsa", "Mensalista"], horizontal=True, key="radio_tipo_extra")
                
                if st.button("➕ Adicionar Convidada Manualmente", use_container_width=True):
                    if not nome_extra.strip():
                        st.error("Digite o nome da jogadora antes de adicionar!")
                    else:
                        nomes_atuais = [p["nome"].strip().lower() for p in st.session_state.presencas]
                        if nome_extra.strip().lower() in nomes_atuais:
                            st.warning(f"**{nome_extra}** já está na lista!")
                        else:
                            st.session_state.presencas.append({
                                "nome": nome_extra.strip(),
                                "tipo": tipo_extra,
                                "hora": datetime.now().strftime("%H:%M")
                            })
                            salvar_dados(PRESENCAS_FILE, st.session_state.presencas)
                            if "times_sorteados" in st.session_state:
                                del st.session_state["times_sorteados"]
                            st.success(f"✅ {nome_extra} adicionada com sucesso!")
                            st.rerun()

            # -----------------------------------------------------------------
            # PAINEL DA JOGADORA (SÓ AFETA A PRÓPRIA CONTA)
            # -----------------------------------------------------------------
            else:
                user = st.session_state.usuario_logado
                st.success(f"Conectada como: **{user['nome']}** ({user['tipo']})")

                cb1, cb2 = st.columns(2)
                with cb1:
                    if st.button("👍 Confirmar Minha Presença", use_container_width=True):
                        tipo_e = "Avulsa" if user['tipo'].lower() in ["avulsa", "diarista"] else "Mensalista"
                        nomes_atuais = [p["nome"].strip().lower() for p in st.session_state.presencas]
                        
                        if user["nome"].strip().lower() in nomes_atuais:
                            st.warning("Seu nome já está na lista!")
                        else:
                            st.session_state.presencas.append({
                                "nome": user["nome"],
                                "tipo": tipo_e,
                                "hora": datetime.now().strftime("%H:%M")
                            })
                            salvar_dados(PRESENCAS_FILE, st.session_state.presencas)
                            if "times_sorteados" in st.session_state:
                                del st.session_state["times_sorteados"]
                            st.rerun()

                with cb2:
                    if st.button("❌ Cancelar Minha Presença", use_container_width=True):
                        nome_alvo = user["nome"].strip().lower()
                        st.session_state.presencas = [
                            p for p in st.session_state.presencas 
                            if p["nome"].strip().lower() != nome_alvo
                        ]
                        salvar_dados(PRESENCAS_FILE, st.session_state.presencas)
                        if "times_sorteados" in st.session_state:
                            del st.session_state["times_sorteados"]
                        st.rerun()

# -----------------------------------------------------------------------------
# DEMAIS PÁGINAS
# -----------------------------------------------------------------------------
elif pagina == "🔀 Sorteio de Times":
    st.subheader("🔀 Sorteio de Times (Automático às 18:30)")
    
    if "times_sorteados" in st.session_state:
        st.success("🎲 **Times Sorteados!**")
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
        st.info("⏳ O sorteio automático acontece às **18:30** de Segunda-feira.")

elif pagina == "📊 Fluxo de Caixa (Admin)":
    st.subheader("📊 Fluxo de Caixa")
    if not st.session_state.e_admin:
        st.error("🔒 Área restrita ao Administrador.")
    else:
        st.success("Módulo de Caixa liberado.")

elif pagina == "💸 Pagamento & Pix":
    st.subheader("💸 Pagamento & Pix")
    st.write("**Titular:** Vagner Ferreira de Souza")
    st.write("**Chave Pix:** 31989684010")

elif pagina == "📜 Regulamento":
    st.subheader("📜 Regulamento Interno")
    st.write("1. Prioridade para Mensalistas até Segunda-Feira às 17:00.")
    st.write("2. Avulsas entram na Fila de Espera até as 17:00 de Segunda-Feira.")
    st.write("3. Às 17:00, o sistema promove as Avulsas para as vagas restantes.")
    st.write("4. Às 18:30, o Sorteio de Times é gerado automaticamente.")

elif pagina == "📋 Elenco de Jogadoras":
    st.subheader("📋 Elenco Registrado")
    df_elenco = pd.DataFrame(st.session_state.jogadoras)[["nome", "tipo"]]
    st.dataframe(df_elenco, use_container_width=True)

elif pagina == "⚙️ Painel Admin":
    st.subheader("⚙️ Painel de Controle do Administrador")
    
    if not st.session_state.e_admin:
        st.error("🔒 **Acesso Restrito!** Entre na aba '👑 Sou Admin' no menu lateral.")
    else:
        st.success("👑 Bem-vindo, Vagner!")
        
        st.markdown("---")
        st.subheader("🧪 Testador de Horários (Simulador)")
        col_t1, col_t2 = st.columns(2)
        with col_t1:
            st.session_state.simular_liberacao_17h = st.checkbox("Simular 'Já passou das 17:00 de Segunda'", value=st.session_state.simular_liberacao_17h)
        with col_t2:
            st.session_state.simular_sorteio_1830 = st.checkbox("Simular 'Já passou das 18:30 de Segunda'", value=st.session_state.simular_sorteio_1830)

        st.markdown("---")
        st.subheader("🚨 Ações do Sistema")
        if st.button("🗑️ Zerar / Limpar Lista de Presença e Sorteio"):
            st.session_state.presencas = []
            if "times_sorteados" in st.session_state:
                del st.session_state["times_sorteados"]
            salvar_dados(PRESENCAS_FILE, [])
            st.success("Tudo limpo com sucesso!")
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
