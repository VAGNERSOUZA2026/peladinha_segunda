import streamlit as st
import pandas as pd

# Configuração da página
st.set_page_config(page_title="Peladinha Segunda", layout="wide")

# ==========================================
# ARQUIVOS E VARIÁVEIS DE SUPORTE
# ==========================================
DATA_FILE = "jogadoras.json"
REGULAMENTO_FILE = "regulamento.json"
AVISOS_FILE = "avisos.json"
ADMINS_FILE = "admins.json"

def salvar_dados(arquivo, dados):
    # Função padrão de salvamento do seu sistema
    pass

# Inicialização de dados no session_state
if "admin_logged" not in st.session_state:
    st.session_state.admin_logged = False

if "admins_lista" not in st.session_state:
    st.session_state.admins_lista = [{"usuario": "dev", "senha": "123"}]

if "jogadoras" not in st.session_state:
    st.session_state.jogadoras = []

if "regulamento" not in st.session_state:
    st.session_state.regulamento = []

if "avisos" not in st.session_state:
    st.session_state.avisos = {"limite_vagas": 15, "recado": "Favor chegarem adiantadas!"}

# ==========================================
# BARRA LATERAL (MENU E LOGIN)
# ==========================================
st.sidebar.title("⚽ Peladinha FC")
st.sidebar.markdown("---")

if not st.session_state.admin_logged:
    st.sidebar.subheader("🔒 Acesso Restrito (Admin)")
    with st.sidebar.form("form_login_lateral"):
        u_input = st.text_input("Usuário Admin")
        s_input = st.text_input("Senha", type="password")
        btn_entrar = st.form_submit_button("Entrar")
        
        if btn_entrar:
            valido = (u_input == "dev" and s_input == "123") or any(a["usuario"] == u_input and a["senha"] == s_input for a in st.session_state.admins_lista)
            if valido:
                st.session_state.admin_logged = True
                st.success("Logado com sucesso!")
                st.rerun()
            else:
                st.error("Usuário ou senha incorretos.")
else:
    st.sidebar.success("Sessão Admin Ativa")
    if st.sidebar.button("Sair / Logout"):
        st.session_state.admin_logged = False
        st.rerun()

st.sidebar.markdown("---")

# Menu dinâmico (Fluxo de Caixa e Painel Admin protegidos)
opcoes_menu = [
    "Presença no Jogo", 
    "Sorteio de Times", 
    "Pagamento & Pix", 
    "📜 Regulamento", 
    "📋 Elenco de Jogadoras"
]

if st.session_state.admin_logged:
    opcoes_menu.extend(["📊 Fluxo de Caixa (Admin)", "⚙️ Painel Admin"])

menu = st.sidebar.radio("Navegação", opcoes_menu)

# ==========================================
# ROTAS / PÁGINAS
# ==========================================

if menu == "Presença no Jogo":
    st.subheader("📌 Presença no Jogo")
    st.write("Gerenciamento de confirmação das jogadoras para a próxima partida.")
    st.info(f"Limite máximo de vagas configurado: {st.session_state.avisos.get('limite_vagas', 15)}")
    st.write(f"Aviso do dia: {st.session_state.avisos.get('recado', '')}")

elif menu == "Sorteio de Times":
    st.subheader("⚽ Sorteio de Times")
    st.write("Área para sortear os times de forma equilibrada.")

elif menu == "Pagamento & Pix":
    st.subheader("💰 Pagamento & Pix")
    st.write("Chave Pix e controle de comprovação de pagamentos.")

elif menu == "📊 Fluxo de Caixa (Admin)" and st.session_state.admin_logged:
    st.subheader("📊 Fluxo de Caixa (Área Administrativa)")
    st.info("Painel financeiro protegido.")
    st.metric(label="Saldo em Caixa", value="R$ 550,00")

elif menu == "📜 Regulamento":
    st.subheader("📜 Regulamento Oficial do Peladinha FC")
    
    if not st.session_state.regulamento:
        st.info("Nenhuma regra cadastrada.")
    else:
        for idx, r in enumerate(st.session_state.regulamento):
            st.markdown(f"**{idx + 1}. {r.get('topico')}**")
            st.write(r.get("regrinha"))
            
            # Opção de excluir regra para o admin diretamente na listagem
            if st.session_state.admin_logged:
                if st.button("🗑️ Excluir Regra", key=f"del_reg_{idx}"):
                    st.session_state.regulamento.pop(idx)
                    salvar_dados(REGULAMENTO_FILE, st.session_state.regulamento)
                    st.success("Regra excluída!")
                    st.rerun()
            st.markdown("---")

    if st.session_state.admin_logged:
        with st.expander("🛠️ [Admin] Adicionar / Editar Regulamento"):
            with st.form("form_novo_reg"):
                novo_topico = st.text_input("Título do Tópico")
                nova_regrinha = st.text_area("Descrição da Regra")
                if st.form_submit_button("Adicionar Regra"):
                    if novo_topico and nova_regrinha:
                        st.session_state.regulamento.append({"topico": novo_topico, "regrinha": nova_regrinha})
                        salvar_dados(REGULAMENTO_FILE, st.session_state.regulamento)
                        st.success("Regra adicionada!")
                        st.rerun()

elif menu == "📋 Elenco de Jogadoras":
    st.subheader("📋 Elenco Cadastrado")
    if not st.session_state.jogadoras:
        st.info("Nenhuma jogadora cadastrada.")
    else:
        df_joga = pd.DataFrame(st.session_state.jogadoras)
        cols_mostrar = ["nome", "tipo", "status", "nascimento", "contato"]
        cols_disponiveis = [c for c in cols_mostrar if c in df_joga.columns]
        st.dataframe(df_joga[cols_disponiveis], use_container_width=True, hide_index=True)

        if st.session_state.admin_logged:
            st.markdown("---")
            st.subheader("🛠️ Gerenciar Elenco (Admin)")
            
            for index, joga in enumerate(st.session_state.jogadoras):
                with st.expander(f"⚙️ Editar / Excluir: {joga.get('nome')} ({joga.get('tipo', 'Mensalista')})"):
                    with st.form(f"form_edit_joga_{index}"):
                        novo_nome = st.text_input("Nome", value=joga.get("nome", ""))
                        
                        tipo_atual = joga.get("tipo", "Mensalista")
                        idx_tipo = 0 if tipo_atual == "Mensalista" else 1
                        novo_tipo = st.selectbox("Categoria", ["Mensalista", "Avulsa"], index=idx_tipo, key=f"t_{index}")
                        
                        status_atual = joga.get("status", "Ativo")
                        idx_status = 0 if status_atual == "Ativo" else 1
                        novo_status = st.selectbox("Status", ["Ativo", "Inativo"], index=idx_status, key=f"s_{index}")
                        
                        col_btn1, col_btn2 = st.columns(2)
                        with col_btn1:
                            salvar_alt = st.form_submit_button("💾 Salvar Alterações")
                        with col_btn2:
                            excluir_btn = st.form_submit_button("🗑️ Excluir Definitivamente", type="primary")
                            
                        if salvar_alt:
                            st.session_state.jogadoras[index]["nome"] = novo_nome
                            st.session_state.jogadoras[index]["tipo"] = novo_tipo
                            st.session_state.jogadoras[index]["status"] = novo_status
                            salvar_dados(DATA_FILE, st.session_state.jogadoras)
                            st.success(f"Jogadora {novo_nome} atualizada!")
                            st.rerun()
                            
                        if excluir_btn:
                            nome_removido = joga.get("nome")
                            st.session_state.jogadoras.pop(index)
                            salvar_dados(DATA_FILE, st.session_state.jogadoras)
                            st.success(f"Jogadora {nome_removido} excluída com sucesso!")
                            st.rerun()

elif menu == "⚙️ Painel Admin":
    st.subheader("⚙️ Configurações Gerais do Sistema")
    if not st.session_state.admin_logged:
        st.error("🔒 Faça login como Administrador na barra lateral para acessar estas configurações.")
    else:
        tab_cfg, tab_admins = st.tabs(["🛠️ Configurações do Jogo", "🔑 Gerenciar Administradores"])
        
        with tab_cfg:
            with st.form("form_config_geral"):
                novo_limite = st.number_input("Limite Máximo de Vagas no Jogo", min_value=1, max_value=50, value=int(st.session_state.avisos.get("limite_vagas", 15)))
                novo_recado = st.text_input("Recado / Aviso Principal", value=st.session_state.avisos.get("recado", ""))
                if st.form_submit_button("💾 Salvar Configurações"):
                    st.session_state.avisos["limite_vagas"] = int(novo_limite)
                    st.session_state.avisos["recado"] = novo_recado
                    salvar_dados(AVISOS_FILE, st.session_state.avisos)
                    st.success("Configurações atualizadas com sucesso!")
                    st.rerun()
                    
        with tab_admins:
            st.subheader("Cadastrar Novos Administradores")
            with st.form("form_novo_admin"):
                novo_user = st.text_input("Novo Usuário Admin")
                nova_senha = st.text_input("Senha do Novo Admin", type="password")
                btn_cad_adm = st.form_submit_button("Cadastrar Administrador")
                
                if btn_cad_adm:
                    if novo_user and nova_senha:
                        if any(a["usuario"] == novo_user for a in st.session_state.admins_lista):
                            st.error("Este usuário já existe!")
                        else:
                            st.session_state.admins_lista.append({"usuario": novo_user, "senha": nova_senha})
                            salvar_dados(ADMINS_FILE, st.session_state.admins_lista)
                            st.success(f"Administrador '{novo_user}' cadastrado com sucesso!")
                            st.rerun()
                    else:
                        st.warning("Preencha usuário e senha.")
            
            st.markdown("### Administradores Cadastrados:")
            for adm in st.session_state.admins_lista:
                st.text(f"👤 Usuário: {adm['usuario']}")

# Rodapé
st.markdown("<div style='text-align: center; color: #94A3B8; margin-top: 40px; font-size: 0.85rem;'>Peladinha FC ⚽ — Todos os direitos reservados</div>", unsafe_allow_html=True)
