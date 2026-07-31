import streamlit as st
import pandas as pd
import json
import os
import random

# Configuração da página
st.set_page_config(
    page_title="Peladinha FC",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilização CSS Personalizada
st.markdown("""
<style>
    .main-title { font-size: 2.2rem; color: #1E3A8A; font-weight: 800; text-align: center; margin-bottom: 5px; }
    .sub-title { font-size: 1.0rem; color: #4B5563; text-align: center; margin-bottom: 20px; }
    .card-notice { background-color: #FEF3C7; border-left: 5px solid #F59E0B; padding: 15px; border-radius: 8px; margin-bottom: 15px; }
    .card-pix { background-color: #ECFDF5; border: 2px dashed #10B981; padding: 15px; border-radius: 10px; text-align: center; margin-bottom: 20px; }
    .card-team { background-color: #F3F4F6; border: 2px solid #E5E7EB; border-radius: 12px; padding: 15px; margin-bottom: 15px; }
</style>
""", unsafe_allow_html=True)

DATA_FILE = "jogadoras.json"
PRESENCAS_FILE = "presencas.json"
AVISOS_FILE = "avisos.json"

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

# Inicialização dos dados
if "jogadoras" not in st.session_state:
    st.session_state.jogadoras = carregar_dados(DATA_FILE, [
        {"nome": "Mariana Silva", "posicao": "Jogadora", "tipo": "Mensalista", "contato": "(31) 99999-1111", "status": "Ativo"},
        {"nome": "Camila Santos", "posicao": "Jogadora", "tipo": "Mensalista", "contato": "(31) 99999-2222", "status": "Ativo"},
    ])

if "presencas" not in st.session_state:
    st.session_state.presencas = carregar_dados(PRESENCAS_FILE, [])

if "avisos" not in st.session_state:
    st.session_state.avisos = carregar_dados(AVISOS_FILE, {
        "vencimento": "Todo dia 10 de cada mês",
        "recado": "Lembrar de levar colete limpo e garrafa de água individual!",
        "pix": "peladinhafc@email.com"
    })

if "admin_logged" not in st.session_state:
    st.session_state.admin_logged = False

# MENU LATERAL
st.sidebar.title("⚽ Peladinha FC")
menu = st.sidebar.radio("Navegação", [
    "📌 Presença no Jogo", 
    "🔀 Sorteio de Times", 
    "💸 Pagamento & Pix",
    "📜 Regulamento",
    "📋 Elenco de Jogadoras", 
    "⚙️ Painel Admin"
])

# LOGIN ADMIN
st.sidebar.markdown("---")
st.sidebar.subheader("🔒 Acesso Restrito")
if not st.session_state.admin_logged:
    senha = st.sidebar.text_input("Senha Admin", type="password")
    if st.sidebar.button("Entrar como Admin"):
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
    st.markdown("<h1 class='main-title'>⚽ Lista da Pelada</h1>", unsafe_allow_html=True)
    
    # Mural de avisos rápido no topo
    st.markdown(f"""
    <div class='card-notice'>
        📢 <b>MURAL DE AVISOS DO GRUPO:</b><br>
        📅 <b>Vencimento da Mensalidade:</b> {st.session_state.avisos.get('vencimento')}<br>
        💡 <b>Lembrete:</b> {st.session_state.avisos.get('recado')}
    </div>
    """, unsafe_allow_html=True)

    jogadoras_ativas = [j["nome"] for j in st.session_state.jogadoras if j.get("status") == "Ativo"]
    
    col_c1, col_c2 = st.columns([2, 1])

    with col_c1:
        st.subheader("✅ Confirmar Presença")
        if not jogadoras_ativas:
            st.warning("Nenhuma jogadora ativa cadastrada.")
        else:
            jogadora_sel = st.selectbox("Selecione seu nome na lista:", jogadoras_ativas)
            
            c_btn1, c_btn2 = st.columns(2)
            with c_btn1:
                if st.button("👍 Confirmar Minha Presença", use_container_width=True):
                    if jogadora_sel in st.session_state.presencas:
                        st.warning("Você já está na lista!")
                    else:
                        st.session_state.presencas.append(jogadora_sel)
                        salvar_dados(PRESENCAS_FILE, st.session_state.presencas)
                        st.success(f"{jogadora_sel} confirmada!")
                        st.rerun()
            with c_btn2:
                if st.button("❌ Tirar Meu Nome", use_container_width=True):
                    if jogadora_sel in st.session_state.presencas:
                        st.session_state.presencas.remove(jogadora_sel)
                        salvar_dados(PRESENCAS_FILE, st.session_state.presencas)
                        st.info(f"{jogadora_sel} removida.")
                        st.rerun()

        # RECURSO ADMIN: CONFIRMAÇÃO POR TERCEIROS
        if st.session_state.admin_logged:
            st.markdown("---")
            st.subheader("🛠️ Gestão de Presença (Admin)")
            st.caption("Adicione ou remova qualquer jogadora que tenha pedido no WhatsApp.")
            
            jogadora_admin_sel = st.selectbox("Selecionar Jogadora (Admin):", jogadoras_ativas, key="admin_presence")
            ca1, ca2 = st.columns(2)
            with ca1:
                if st.button("➕ Adicionar à Lista", use_container_width=True):
                    if jogadora_admin_sel not in st.session_state.presencas:
                        st.session_state.presencas.append(jogadora_admin_sel)
                        salvar_dados(PRESENCAS_FILE, st.session_state.presencas)
                        st.success(f"{jogadora_admin_sel} adicionada!")
                        st.rerun()
            with ca2:
                if st.button("🗑️ Zerar Lista do Jogo", use_container_width=True):
                    st.session_state.presencas = []
                    salvar_dados(PRESENCAS_FILE, [])
                    st.warning("Lista zerada com sucesso!")
                    st.rerun()

    with col_c2:
        st.subheader(f"📋 Confirmadas ({len(st.session_state.presencas)})")
        if not st.session_state.presencas:
            st.write("Ninguém confirmou ainda.")
        else:
            for idx, nome in enumerate(st.session_state.presencas, 1):
                st.write(f"**{idx}.** {nome}")


# --- PÁGINA 2: SORTEIO DE TIMES ---
elif menu == "🔀 Sorteio de Times":
    st.markdown("<h1 class='main-title'>🔀 Sorteio de Times</h1>", unsafe_allow_html=True)

    tab_oficial, tab_atraso = st.tabs(["⭐ Sorteio Geral (Confirmadas)", "⏱️ Sorteio Provisório (Quem Já Chegou)"])

    with tab_oficial:
        qtd_times = st.slider("Dividir em quantos times?", 2, 4, 2, key="qtd_oficial")
        if st.button("🎲 Sortear Times Aleatórios", use_container_width=True):
            if len(st.session_state.presencas) < qtd_times:
                st.error("Poucas jogadoras confirmadas para dividir os times.")
            else:
                lista_temp = st.session_state.presencas.copy()
                random.shuffle(lista_temp)
                
                times = [[] for _ in range(qtd_times)]
                for idx, p in enumerate(lista_temp):
                    times[idx % qtd_times].append(p)
                
                cols = st.columns(qtd_times)
                for i, t in enumerate(times):
                    with cols[i]:
                        st.markdown(f"<div class='card-team'><h3>Time {i+1}</h3>", unsafe_allow_html=True)
                        for item in t:
                            st.write(f"• **{item}**")
                        st.markdown("</div>", unsafe_allow_html=True)

    with tab_atraso:
        st.info("💡 Marque apenas quem está **presente na quadra agora** para iniciar o jogo sem atrasos.")
        presentes_quadra = st.multiselect("Quem já chegou no campo/quadra?", st.session_state.presencas)
        
        if st.button("⚡ Gerar Times para Começar Agora", use_container_width=True):
            if len(presentes_quadra) < 2:
                st.error("Selecione pelo menos 2 jogadoras.")
            else:
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


# --- PÁGINA 3: PIX E PAGAMENTO ---
elif menu == "💸 Pagamento & Pix":
    st.markdown("<h1 class='main-title'>💸 Chave Pix para Pagamento</h1>", unsafe_allow_html=True)
    st.markdown("<p class='sub-title'>Efetue o pagamento da sua mensalidade ou taxa avulsa diretamente pelo Pix.</p>", unsafe_allow_html=True)

    chave_pix = st.session_state.avisos.get("pix", "Não informada")

    st.markdown(f"""
    <div class='card-pix'>
        <h3>💰 Chave Pix Oficial</h3>
        <p style='font-size: 1.5rem; font-weight: bold; color: #047857;'>{chave_pix}</p>
        <p><b>Vencimento:</b> {st.session_state.avisos.get('vencimento')}</p>
    </div>
    """, unsafe_allow_html=True)

    st.text_input("Copiar Chave Pix:", value=chave_pix, help="Selecione o texto acima ou use este campo para copiar.")


# --- PÁGINA 4: REGULAMENTO ---
elif menu == "📜 Regulamento":
    st.markdown("<h1 class='main-title'>📜 Regulamento e Boa Convivência</h1>", unsafe_allow_html=True)
    
    st.markdown("""
    ### ⚠️ Regras Oficiais da Peladinha
    
    Para garantir um ambiente divertido, respeitoso e organizado, todas as participantes devem seguir o regulamento abaixo:

    1. **Respeito em Primeiro Lugar:** Não serão toleradas ofensas, agressões verbais ou físicas, xingamentos ou qualquer tipo de desrespeito entre as jogadoras ou organizadores.
    2. **Compromisso com o Horário:** Chegue com pelo menos 10 minutos de antecedência. O jogo começará no horário marcado.
    3. **Confirmação de Presença:** Cancele sua presença na lista com antecedência caso surja um imprevisto, permitindo que outra pessoa jogue.
    4. **Pagamentos em Dia:** O pagamento da mensalidade/avulso deve ser feito até a data limite estipulada.
    5. **Jogo Limpo (Fair Play):** Evite jogadas violentas ou de risco. O objetivo principal do grupo é a prática esportiva e a amizade.

    ---
    > 🔴 **ATENÇÃO:** O descumprimento das regras acima, condutas antidesportivas frequentes ou falta de respeito com as demais integrantes **resultará na exclusão definitiva da jogadora da pelada.**
    """)


# --- PÁGINA 5: ELENCO COMPLETO ---
elif menu == "📋 Elenco de Jogadoras":
    st.markdown("<h1 class='main-title'>🏃‍♀️ Elenco de Jogadoras</h1>", unsafe_allow_html=True)
    if st.session_state.jogadoras:
        df = pd.DataFrame(st.session_state.jogadoras)
        st.dataframe(df[['nome', 'tipo', 'contato', 'status']], use_container_width=True, hide_index=True)


# --- PÁGINA 6: PAINEL ADMIN ---
elif menu == "⚙️ Painel Admin":
    st.markdown("<h1 class='main-title'>⚙️ Painel do Administrador</h1>", unsafe_allow_html=True)
    
    if not st.session_state.admin_logged:
        st.error("🔒 Área restrita! Digite a senha no menu lateral para acessar.")
    else:
        t_cad, t_ger, t_avisos = st.tabs(["➕ Cadastrar Jogadora", "✏️ Gerenciar Jogadoras", "📢 Lembretes & Pix"])
        
        # CADASTRAR JOGADORA (SEM HABILIDADES/ESTRELAS)
        with t_cad:
            st.subheader("Cadastrar Nova Jogadora")
            with st.form("cad_form", clear_on_submit=True):
                col1, col2 = st.columns(2)
                with col1:
                    nome = st.text_input("Nome Completo *")
                    tipo = st.selectbox("Categoria *", ["Mensalista", "Avulso"])
                with col2:
                    contato = st.text_input("WhatsApp / Contato")
                    status = st.selectbox("Status *", ["Ativo", "Inativo"])
                
                if st.form_submit_button("💾 Salvar Cadastro", use_container_width=True):
                    if nome.strip():
                        st.session_state.jogadoras.append({
                            "nome": nome.strip(),
                            "posicao": "Jogadora",
                            "tipo": tipo,
                            "contato": contato.strip(),
                            "status": status
                        })
                        salvar_dados(DATA_FILE, st.session_state.jogadoras)
                        st.success(f"**{nome}** cadastrada com sucesso!")
                        st.rerun()

        # EDITAR / EXCLUIR JOGADORA
        with t_ger:
            st.subheader("Editar ou Excluir Jogadora")
            if st.session_state.jogadoras:
                nomes = [j["nome"] for j in st.session_state.jogadoras]
                sel_j = st.selectbox("Escolha uma jogadora:", nomes)
                idx = next(i for i, item in enumerate(st.session_state.jogadoras) if item["nome"] == sel_j)
                
                j_atual = st.session_state.jogadoras[idx]
                
                with st.form("edit_form"):
                    e_nome = st.text_input("Nome", value=j_atual["nome"])
                    e_tipo = st.selectbox("Categoria", ["Mensalista", "Avulso"], index=["Mensalista", "Avulso"].index(j_atual.get("tipo", "Mensalista")))
                    e_contato = st.text_input("Contato", value=j_atual.get("contato", ""))
                    e_status = st.selectbox("Status", ["Ativo", "Inativo"], index=["Ativo", "Inativo"].index(j_atual.get("status", "Ativo")))
                    
                    b1, b2 = st.columns(2)
                    if b1.form_submit_button("🔄 Atualizar Dados", use_container_width=True):
                        st.session_state.jogadoras[idx] = {
                            "nome": e_nome.strip(),
                            "posicao": "Jogadora",
                            "tipo": e_tipo,
                            "contato": e_contato.strip(),
                            "status": e_status
                        }
                        salvar_dados(DATA_FILE, st.session_state.jogadoras)
                        st.success("Dados atualizados!")
                        st.rerun()
                        
                    if b2.form_submit_button("❌ Excluir do Cadastro", use_container_width=True):
                        del st.session_state.jogadoras[idx]
                        salvar_dados(DATA_FILE, st.session_state.jogadoras)
                        st.warning("Jogadora excluída!")
                        st.rerun()

        # GERENCIAR MURAL DE AVISOS E PIX
        with t_avisos:
            st.subheader("📢 Configurar Lembretes e Pix")
            with st.form("form_avisos"):
                venc = st.text_input("Dia de Vencimento:", value=st.session_state.avisos.get("vencimento", ""))
                rec = st.text_area("Lembrete / Recado do Grupo:", value=st.session_state.avisos.get("recado", ""))
                pix = st.text_input("Chave Pix:", value=st.session_state.avisos.get("pix", ""))
                
                if st.form_submit_button("💾 Salvar Avisos e Pix", use_container_width=True):
                    st.session_state.avisos = {
                        "vencimento": venc,
                        "recado": rec,
                        "pix": pix
                    }
                    salvar_dados(AVISOS_FILE, st.session_state.avisos)
                    st.success("Mural e Pix atualizados com sucesso!")
                    st.rerun()
