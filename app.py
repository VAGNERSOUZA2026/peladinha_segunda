import streamlit as st
import pandas as pd
import json
import os

# Configuração da página
st.set_page_config(
    page_title="Gestão da Peladinha",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilização CSS personalizada
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        color: #1E3A8A;
        font-weight: 800;
        margin-bottom: 0px;
    }
    .sub-header {
        font-size: 1.0rem;
        color: #4B5563;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# Armazenamento simples em JSON local
DATA_FILE = "jogadoras.json"

def carregar_jogadoras():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return [
        {"nome": "Mariana Silva", "posicao": "Atacante", "nivel": 5, "tipo": "Mensalista", "contato": "31999991111", "status": "Ativo"},
        {"nome": "Camila Santos", "posicao": "Goleira", "nivel": 4, "tipo": "Mensalista", "contato": "31999992222", "status": "Ativo"},
        {"nome": "Juliana Costa", "posicao": "Zagueira", "nivel": 3, "tipo": "Avulso", "contato": "31999993333", "status": "Ativo"},
    ]

def salvar_jogadoras(jogadoras):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(jogadoras, f, ensure_ascii=False, indent=4)

if "jogadoras" not in st.session_state:
    st.session_state.jogadoras = carregar_jogadoras()

if "admin_logged" not in st.session_state:
    st.session_state.admin_logged = False

# Sidebar / Menu
st.sidebar.title("⚽ Peladinha FC")
menu = st.sidebar.radio("Navegação", ["📋 Lista de Jogadoras", "⚙️ Painel Admin"])

# Módulo de Autenticação Admin na Sidebar
st.sidebar.markdown("---")
st.sidebar.subheader("🔒 Área Administrativa")

if not st.session_state.admin_logged:
    senha_input = st.sidebar.text_input("Senha Admin", type="password", key="pwd_input")
    if st.sidebar.button("Entrar como Admin"):
        if senha_input == "1980":  # Senha do Admin
            st.session_state.admin_logged = True
            st.sidebar.success("Modo Admin Ativado!")
            st.rerun()
        else:
            st.sidebar.error("Senha incorreta!")
else:
    st.sidebar.info("🔑 **Modo Admin Ativo**")
    if st.sidebar.button("Sair do Modo Admin"):
        st.session_state.admin_logged = False
        st.rerun()

# --- PÁGINA 1: LISTA DE JOGADORAS (PÚBLICA) ---
if menu == "📋 Lista de Jogadoras":
    st.markdown('<div class="main-header">⚽ Elenco da Peladinha</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Confira a lista atualizada das jogadoras cadastradas no grupo.</div>', unsafe_allow_html=True)
    
    if not st.session_state.jogadoras:
        st.warning("Nenhuma jogadora cadastrada ainda.")
    else:
        df = pd.DataFrame(st.session_state.jogadoras)
        
        # Filtros
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            filtro_pos = st.selectbox("Filtrar por Posição", ["Todas"] + list(df['posicao'].unique()))
        with col_f2:
            filtro_tipo = st.selectbox("Filtrar por Tipo", ["Todos"] + list(df['tipo'].unique()))
            
        df_filtered = df.copy()
        if filtro_pos != "Todas":
            df_filtered = df_filtered[df_filtered['posicao'] == filtro_pos]
        if filtro_tipo != "Todos":
            df_filtered = df_filtered[df_filtered['tipo'] == filtro_tipo]

        # Métricas no topo
        c1, c2, c3 = st.columns(3)
        c1.metric("Total de Jogadoras", len(df_filtered))
        c2.metric("Mensalistas", len(df_filtered[df_filtered['tipo'] == 'Mensalista']))
        c3.metric("Avulsas", len(df_filtered[df_filtered['tipo'] == 'Avulso']))

        st.markdown("### 🏃‍♀️ Jogadoras Cadastradas")
        
        # Tabela formatada
        st.dataframe(
            df_filtered[['nome', 'posicao', 'nivel', 'tipo', 'status']],
            use_container_width=True,
            column_config={
                "nome": "Nome Completo",
                "posicao": "Posição Principal",
                "nivel": st.column_config.NumberColumn("Nível ⭐", help="Nível de 1 a 5"),
                "tipo": "Categoria",
                "status": "Situação"
            },
            hide_index=True
        )

# --- PÁGINA 2: PAINEL ADMIN (CADASTRAR / EDITAR) ---
elif menu == "⚙️ Painel Admin":
    st.markdown('<div class="main-header">⚙️ Painel de Administração</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Gestão de cadastro e edição do elenco.</div>', unsafe_allow_html=True)

    if not st.session_state.admin_logged:
        st.error("🔒 **Acesso Restrito ao Administrador!**")
        st.info("Por favor, digite a senha no menu lateral para acessar esta seção.")
    else:
        tab_cad, tab_edit = st.tabs(["➕ Cadastrar Nova Jogadora", "✏️ Gerenciar / Excluir"])

        # CADASTRO DE JOGADORA
        with tab_cad:
            st.markdown("### 📝 Formulário de Cadastro")
            with st.form("form_cadastrar_jogadora", clear_on_submit=True):
                col1, col2 = st.columns(2)
                with col1:
                    nome = st.text_input("Nome Completo *", placeholder="Ex: Ana Maria")
                    posicao = st.selectbox("Posição Principal *", ["Goleira", "Zagueira", "Lateral", "Meio-Campo", "Atacante"])
                    nivel = st.slider("Nível / Habilidade ⭐", min_value=1, max_value=5, value=3)
                
                with col2:
                    tipo = st.selectbox("Tipo de Participação *", ["Mensalista", "Avulso"])
                    contato = st.text_input("WhatsApp / Telefone", placeholder="Ex: (31) 99999-8888")
                    status = st.selectbox("Status *", ["Ativo", "Inativo"])

                submitted = st.form_submit_button("💾 Salvar Cadastro", use_container_width=True)
                
                if submitted:
                    if not nome.strip():
                        st.error("O campo Nome é obrigatório!")
                    else:
                        nova_jogadora = {
                            "nome": nome.strip(),
                            "posicao": posicao,
                            "nivel": nivel,
                            "tipo": tipo,
                            "contato": contato.strip(),
                            "status": status
                        }
                        st.session_state.jogadoras.append(nova_jogadora)
                        salvar_jogadoras(st.session_state.jogadoras)
                        st.success(f"🎉 **{nome}** cadastrada com sucesso!")

        # EDITAR OU EXCLUIR
        with tab_edit:
            st.markdown("### 🛠️ Editar ou Remover Jogadoras")
            if not st.session_state.jogadoras:
                st.info("Nenhuma jogadora para gerenciar.")
            else:
                nomes_jogadoras = [j["nome"] for j in st.session_state.jogadoras]
                jogadora_sel_nome = st.selectbox("Selecione a jogadora:", nomes_jogadoras)
                
                index_sel = next((i for i, item in enumerate(st.session_state.jogadoras) if item["nome"] == jogadora_sel_nome), None)
                
                if index_sel is not None:
                    jog = st.session_state.jogadoras[index_sel]
                    
                    with st.form("form_editar_jogadora"):
                        c1, c2 = st.columns(2)
                        with c1:
                            e_nome = st.text_input("Nome", value=jog["nome"])
                            e_posicao = st.selectbox("Posição", ["Goleira", "Zagueira", "Lateral", "Meio-Campo", "Atacante"], index=["Goleira", "Zagueira", "Lateral", "Meio-Campo", "Atacante"].index(jog.get("posicao", "Meio-Campo")))
                            e_nivel = st.slider("Nível ⭐", 1, 5, value=jog.get("nivel", 3))
                        with c2:
                            e_tipo = st.selectbox("Tipo", ["Mensalista", "Avulso"], index=["Mensalista", "Avulso"].index(jog.get("tipo", "Mensalista")))
                            e_contato = st.text_input("Contato", value=jog.get("contato", ""))
                            e_status = st.selectbox("Status", ["Ativo", "Inativo"], index=["Ativo", "Inativo"].index(jog.get("status", "Ativo")))
                        
                        col_b1, col_b2 = st.columns(2)
                        with col_b1:
                            btn_atualizar = st.form_submit_button("🔄 Atualizar Dados", use_container_width=True)
                        with col_b2:
                            btn_excluir = st.form_submit_button("❌ Excluir Jogadora", use_container_width=True)

                        if btn_atualizar:
                            st.session_state.jogadoras[index_sel] = {
                                "nome": e_nome.strip(),
                                "posicao": e_posicao,
                                "nivel": e_nivel,
                                "tipo": e_tipo,
                                "contato": e_contato.strip(),
                                "status": e_status
                            }
                            salvar_jogadoras(st.session_state.jogadoras)
                            st.success("Dados atualizados com sucesso!")
                            st.rerun()

                        if btn_excluir:
                            del st.session_state.jogadoras[index_sel]
                            salvar_jogadoras(st.session_state.jogadoras)
                            st.warning("Jogadora removida com sucesso!")
                            st.rerun()
