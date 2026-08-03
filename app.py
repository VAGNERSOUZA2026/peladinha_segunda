import streamlit as st
import pandas as pd

# Configuração inicial do app
st.set_page_config(page_title="Peladinha Segunda", layout="wide")

# ==========================================
# SIMULAÇÃO / INICIALIZAÇÃO DE DADOS E ARQUIVOS
# ==========================================
# (Substitua ou mantenha as suas funções de salvar/carregar dados originais aqui)
DATA_FILE = "jogadoras.json"
REGULAMENTO_FILE = "regulamento.json"
AVISOS_FILE = "avisos.json"
ADMINS_FILE = "admins.json"

# Funções auxiliares fictícias caso não estejam no seu escopo principal
def salvar_dados(arquivo, dados):
    # Insira aqui a sua lógica real de salvamento (ex: json.dump ou salvamento em arquivo)
    pass

# Inicializando session_states caso não existam
if "admin_logged" not in st.session_state:
    st.session_state.admin_logged = False

if "jogadoras" not in st.session_state:
    st.session_state.jogadoras = [
        {"nome": "Maria Silva", "tipo": "Mensalista", "status": "Ativo", "nascimento": "01/01/1990", "contato": "31999999999"},
        {"nome": "Ana Souza", "tipo": "Avulsa", "status": "Ativo", "nascimento": "05/05/1995", "contato": "31888888888"}
    ]

if "regulamento" not in st.session_state:
    st.session_state.regulamento = [
        {"topico": "Chegada", "regrinha": "Chegar 10 minutos antes para organizar o jogo."},
        {"topico": "Mensalidade", "regrinha": "Pagamento até o dia 10 de cada mês."}
    ]

if "avisos" not in st.session_state:
    st.session_state.avisos = {"limite_vagas": 15, "recado": "Favor chegarem adiantadas!"}

if "admins_lista" not in st.session_state:
    st.session_state.admins_lista = [{"usuario": "admin", "senha": "123"}]

# ==========================================
# BARRA LATERAL (MENU E LOGIN)
# ==========================================
st.sidebar.title("⚽ Peladinha FC")

# Área de Login de Administrador na Sidebar
st.sidebar.markdown("---")
if not st.session_state.admin_logged:
    st.sidebar.subheader("🔒 Acesso Restrito")
    with st.sidebar.form("form_login_lateral"):
        u_input = st.text_input("Usuário")
        s_input = st.text_input("Senha", type="password")
        btn_entrar = st.form_submit_button("Entrar")
        if btn_entrar:
            # Verifica se bate com o dev ou com a lista de admins cadastrados
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

# Menu dinâmico: Fluxo de Caixa e Painel Admin só aparecem se logado!
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
# ROTAS / PÁGINAS DO APLICATIVO
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
    
    for idx, r in enumerate(st.session_state.regulamento):
        st.markdown(f"**{idx + 1}. {r.get('topico')}**")
        st.write(r.get("regrinha"))
        
        # Opção de excluir regra diretamente para o administrador
        if st.session_state.admin_logged:
            if st.button(f"🗑️ Excluir Regra {idx + 1}", key=f"del_reg_{idx}"):
                st.session_state.regulamento.pop(idx)
                salvar_dados(REGULAMENTO_FILE, st.session_state.regulamento)
                st.success("Regra excluída com sucesso!")
                st.rerun()
        st.markdown("---")

    if st.session_state.admin_logged:
        with st.expander("🛠️ [Admin] Adicionar Novo Regulamento"):
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

        # Gerenciamento completo (Editar Categoria, Status e Excluir) visível apenas para Admin
        if st.session_state.admin_logged:
            st.markdown("---")
            st.subheader("🛠️ Gerenciar Elenco Detalhado (Admin)")
            
            for index, joga in enumerate(st.session_state.jogadoras):
                with st.expander(f"⚙️ Editar / Excluir: {joga.get('nome')} ({joga.get('tipo', 'Mensalista')})"):
                    with st.form(f"form_edit_joga_{index}"):
                        novo_nome = st.text_input("Nome", value=joga.get("nome", ""))
                        
                        # Tipo: Mensalista ou Avulsa
                        tipo_atual = joga.get("tipo", "Mensalista")
                        idx_tipo = 0 if tipo_atual == "Mensalista" else 1
                        novo_tipo = st.selectbox("Categoria", ["Mensalista", "Avulsa"], index=idx_tipo, key=f"t_{index}")
                        
                        # Status: Ativo ou Inativo
                        status_atual = joga.get("status", "Ativo")
                        idx_status = 0 if status_atual == "Ativo" else 1
                        novo_status = st.selectbox("Status", ["Ativo", "Inativo"], index=idx_status, key=f"s_{index}")
                        
                        col_btn1, col_btn2 = st.columns(2)
                        with col_btn1:
                            salvar_alt = st.form_submit_button("💾 Salvar Alterações")
                        with col_btn2:
                            excluir_btn = st.form_submit_button("🗑️ Excluir Jogadora", type="primary")
                            
                        if salvar_alt:
                            st.session_state.jogadoras[index]["nome"] = novo_nome
                            st.session_state.jogadoras[index]["tipo"] = novo_tipo
                            st.session_state.jogadoras[index]["status"] = novo_status
                            salvar_dados(DATA_FILE, st.session_state.jogadoras)
                            st.success(f"Dados de {novo_nome} atualizados!")
                            st.rerun()
                            
                        if excluir_btn:
                            nome_removido = joga.get("nome")
                            st.session_state.jogadoras.pop(index)
                            salvar_dados(DATA_FILE, st.session_state.jogadoras)
                            st.warning(f"Jogadora {nome_removido} excluída definitivamente!")
                            st.rerun()

elif menu == "⚙️ Painel Admin" and st.session_state.admin_logged:
    st.subheader("⚙️ Configurações Gerais do Sistema")
    
    # Abas organizadoras dentro do painel admin
    tab_cfg, tab_admins = st.tabs(["🛠️ Configurações e Vagas", "🔑 Gerenciar Administradores"])
    
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
        st.info("Aqui você pode criar novos logins de acesso para outras administradoras ajudarem a gerenciar o sistema.")
        
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
                    st.warning("Preencha o usuário e a senha.")
        
        st.markdown("### Administradores Cadastrados:")
        for adm in st.session_state.admins_lista:
            st.text(f"👤 Usuário: {adm['usuario']}")

# Rodapé
st.markdown("<div style='text-align: center; color: #94A3B8; margin-top: 40px; font-size: 0.85rem;'>Peladinha FC ⚽ — Todos os direitos reservados</div>", unsafe_allow_html=True)
                
